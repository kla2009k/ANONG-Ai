#!/usr/bin/env python3
"""Train the mask-guided hierarchical Herlev grade research model.

The locked test split is loaded only after model selection. This script creates
an experiment checkpoint; it never overwrites models/best_cervical.pt.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, recall_score
from torch.utils.data import DataLoader, WeightedRandomSampler


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.grade_research_v3 import (
    DISPLAY_OUTPUTS,
    GRADE_CLASSES,
    GradeResearchNet,
    HerlevMaskDataset,
    multitask_loss,
    safety_selection_score,
    selective_metrics,
    update_hard_example_weights,
)


def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def class_weights(dataset: HerlevMaskDataset, device):
    counts = Counter(int(row["label5"]) for row in dataset.rows)
    values = [len(dataset) / (len(GRADE_CLASSES) * counts[index]) for index in range(len(GRADE_CLASSES))]
    return np.asarray(values, dtype=np.float64), torch.tensor(values, dtype=torch.float32, device=device)


def make_loader(dataset, batch, workers, sampling_weights=None, shuffle=False):
    sampler = None
    if sampling_weights is not None:
        sampler = WeightedRandomSampler(
            torch.as_tensor(sampling_weights, dtype=torch.double), len(dataset), replacement=True
        )
    return DataLoader(
        dataset, batch_size=batch, shuffle=shuffle and sampler is None, sampler=sampler,
        num_workers=workers, pin_memory=torch.cuda.is_available(), persistent_workers=False,
    )


def train_epoch(model, loader, optimizer, scaler, device, weights, args):
    model.train()
    seen_losses = np.full(len(loader.dataset), np.nan, dtype=np.float64)
    totals = Counter()
    for batch in loader:
        image = batch["image"].to(device, non_blocking=True)
        labels = batch["label"].to(device, non_blocking=True)
        masks = batch["mask"].to(device, non_blocking=True)
        mask_available = batch["mask_available"].to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
            outputs = model(image)
            losses = multitask_loss(
                outputs, labels, masks, mask_available, weights,
                label_smoothing=args.label_smoothing,
                segmentation_weight=args.segmentation_weight,
                hierarchy_weight=args.hierarchy_weight,
                ordinal_weight=args.ordinal_weight,
            )
        scaler.scale(losses["loss"]).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        scaler.step(optimizer)
        scaler.update()
        indexes = batch["index"].numpy()
        seen_losses[indexes] = losses["per_sample_grade"].cpu().numpy()
        size = len(labels)
        for name in ("loss", "grade", "hierarchy", "ordinal", "segmentation"):
            totals[name] += float(losses[name].detach()) * size
        totals["samples"] += size
    fallback = float(np.nanmedian(seen_losses)) if np.isfinite(seen_losses).any() else 1.0
    seen_losses = np.nan_to_num(seen_losses, nan=fallback)
    return {name: totals[name] / totals["samples"] for name in ("loss", "grade", "hierarchy", "ordinal", "segmentation")}, seen_losses


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    labels, probabilities = [], []
    triage_scores, high_risk_scores = [], []
    for batch in loader:
        image = batch["image"].to(device, non_blocking=True)
        outputs = model(image)
        labels.append(batch["label"].numpy())
        probabilities.append(torch.softmax(outputs["grade_logits"], dim=1).cpu().numpy())
        triage_scores.append(torch.sigmoid(outputs["triage_logit"]).cpu().numpy())
        high_risk_scores.append(torch.sigmoid(outputs["high_risk_logit"]).cpu().numpy())
    labels = np.concatenate(labels)
    probabilities = np.concatenate(probabilities)
    predicted = probabilities.argmax(axis=1)
    triage_scores = np.concatenate(triage_scores)
    high_risk_scores = np.concatenate(high_risk_scores)
    metrics = {
        "n": int(len(labels)),
        "accuracy": float((predicted == labels).mean()),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predicted)),
        "macro_f1": float(f1_score(labels, predicted, average="macro", zero_division=0)),
        "per_class_recall": {
            name: float(recall_score(labels == index, predicted == index, zero_division=0))
            for index, name in enumerate(GRADE_CLASSES)
        },
        "high_risk_exact_recall": float(recall_score(labels >= 2, predicted >= 2, zero_division=0)),
        "triage_head_recall_at_0_5": float(recall_score(labels > 0, triage_scores >= 0.5, zero_division=0)),
        "high_risk_head_recall_at_0_5": float(recall_score(labels >= 2, high_risk_scores >= 0.5, zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predicted, labels=range(4)).tolist(),
        "selective_prediction": selective_metrics(labels, probabilities),
    }
    metrics["selection_score"] = safety_selection_score(
        macro_f1=metrics["macro_f1"],
        high_risk_recall=metrics["high_risk_exact_recall"],
        triage_recall=metrics["triage_head_recall_at_0_5"],
        balanced_accuracy=metrics["balanced_accuracy"],
    )
    return metrics


def limit_rows(dataset, maximum):
    if maximum and len(dataset.rows) > maximum:
        dataset.rows = dataset.rows[:maximum]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument("--out", type=Path, default=ROOT / "models" / "grade_research_v3")
    parser.add_argument("--tag", default="mask_hierarchical")
    parser.add_argument("--architecture", choices=["efficientnet_b0", "efficientnet_b2", "efficientnet_b3", "convnext_tiny"], default="efficientnet_b0")
    parser.add_argument("--image-size", type=int, default=320)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=24)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=2e-4)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--label-smoothing", type=float, default=0.04)
    parser.add_argument("--segmentation-weight", type=float, default=0.15)
    parser.add_argument("--hierarchy-weight", type=float, default=0.20)
    parser.add_argument("--ordinal-weight", type=float, default=0.15)
    parser.add_argument("--hard-mining-strength", type=float, default=1.5)
    parser.add_argument("--stain-normalize", action="store_true")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--max-train", type=int, default=0, help="smoke-test limiter")
    parser.add_argument("--max-val", type=int, default=0, help="smoke-test limiter")
    parser.add_argument("--max-test", type=int, default=0, help="smoke-test limiter")
    args = parser.parse_args()

    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.out.mkdir(parents=True, exist_ok=True)
    train = HerlevMaskDataset(args.data / "split_train.csv", args.image_size, True, args.stain_normalize, True)
    val = HerlevMaskDataset(args.data / "split_val.csv", args.image_size, False, args.stain_normalize, False)
    limit_rows(train, args.max_train)
    limit_rows(val, args.max_val)
    class_weight_values, loss_weights = class_weights(train, device)
    base_sampling = np.asarray([class_weight_values[int(row["label5"])] for row in train.rows])
    sampling = base_sampling / base_sampling.mean()
    val_loader = make_loader(val, args.batch, args.workers, shuffle=False)

    model = GradeResearchNet(args.architecture, not args.no_pretrained, args.dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_state, best_metrics, best_epoch = None, None, 0
    patience = args.patience
    history = []

    for epoch in range(1, args.epochs + 1):
        started = time.time()
        train_loader = make_loader(train, args.batch, args.workers, sampling_weights=sampling)
        losses, example_losses = train_epoch(model, train_loader, optimizer, scaler, device, loss_weights, args)
        validation = evaluate(model, val_loader, device)
        scheduler.step()
        sampling = update_hard_example_weights(base_sampling, example_losses, args.hard_mining_strength)
        record = {"epoch": epoch, "seconds": time.time() - started, "train": losses, "validation": validation}
        history.append(record)
        print(json.dumps({"epoch": epoch, "loss": losses["loss"], "val": validation["selection_score"], "acc": validation["accuracy"]}))
        if best_metrics is None or validation["selection_score"] > best_metrics["selection_score"] + 1e-5:
            best_state = copy.deepcopy({key: value.detach().cpu() for key, value in model.state_dict().items()})
            best_metrics, best_epoch, patience = validation, epoch, args.patience
        else:
            patience -= 1
            if patience <= 0:
                break

    if best_state is None:
        raise RuntimeError("no checkpoint selected")
    model.load_state_dict(best_state)

    # The held-out test is opened only after model selection is complete.
    test = HerlevMaskDataset(args.data / "split_test.csv", args.image_size, False, args.stain_normalize, False)
    limit_rows(test, args.max_test)
    test_metrics = evaluate(model, make_loader(test, args.batch, args.workers), device)
    checkpoint_path = args.out / f"{args.tag}.pt"
    torch.save({
        "state_dict": best_state,
        "architecture": args.architecture,
        "image_size": args.image_size,
        "grade_classes": list(GRADE_CLASSES),
        "display_outputs": list(DISPLAY_OUTPUTS),
        "koil_contract": "independent SIPaKMeD morphology model; not part of grade softmax",
        "hpv_contract": "external laboratory context only; no molecular image endpoint",
        "mask_auxiliary_supervision": True,
        "best_epoch": best_epoch,
        "validation_metrics": best_metrics,
        "test_metrics": test_metrics,
        "seed": args.seed,
    }, checkpoint_path)
    result = {
        "experiment": vars(args) | {"data": str(args.data), "out": str(args.out)},
        "best_epoch": best_epoch,
        "validation": best_metrics,
        "test": test_metrics,
        "history": history,
        "checkpoint": str(checkpoint_path),
        "claim_boundary": "Research experiment only. Do not promote unless full locked-test and external validation gates pass.",
    }
    (args.out / f"{args.tag}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"checkpoint": str(checkpoint_path), "test": test_metrics}, indent=2))


if __name__ == "__main__":
    main()
