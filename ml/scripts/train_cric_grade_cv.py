#!/usr/bin/env python3
"""Train one parent-image-disjoint CRIC fold without touching production."""

from __future__ import annotations

import argparse
import copy
import json
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

from ml.cric_grade_data import CricCellDataset
from ml.grade_research_v3 import GRADE_CLASSES, GradeResearchNet, multitask_loss, safety_selection_score, selective_metrics
from ml.scripts.train_grade_research_v3 import seed_everything


def loader(dataset, batch: int, workers: int, train: bool = False) -> DataLoader:
    sampler = None
    if train:
        counts = Counter(int(row["label5"]) for row in dataset.rows)
        weights = np.asarray([np.sqrt(len(dataset) / counts[int(row["label5"])]) for row in dataset.rows])
        sampler = WeightedRandomSampler(torch.as_tensor(weights, dtype=torch.double), len(dataset), replacement=True)
    return DataLoader(
        dataset, batch_size=batch, sampler=sampler, shuffle=False, num_workers=workers,
        pin_memory=torch.cuda.is_available(), persistent_workers=workers > 0,
    )


def metrics_from_predictions(labels: np.ndarray, probabilities: np.ndarray, triage_scores: np.ndarray,
                             high_risk_scores: np.ndarray) -> dict:
    predicted = probabilities.argmax(axis=1)
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
        metrics["macro_f1"], metrics["high_risk_exact_recall"],
        metrics["triage_head_recall_at_0_5"], metrics["balanced_accuracy"],
    )
    return metrics


@torch.no_grad()
def evaluate(model, data_loader, device, tta: bool = False) -> tuple[dict, dict[str, np.ndarray]]:
    model.eval()
    labels, probabilities, triage, high_risk = [], [], [], []
    for batch_data in data_loader:
        images = batch_data["image"].to(device, non_blocking=True)
        variants = [images]
        if tta:
            variants.extend([torch.flip(images, (-1,)), torch.flip(images, (-2,))])
        outputs = [model(variant) for variant in variants]
        probabilities.append(torch.stack([torch.softmax(output["grade_logits"], 1) for output in outputs]).mean(0).cpu().numpy())
        triage.append(torch.stack([torch.sigmoid(output["triage_logit"]) for output in outputs]).mean(0).cpu().numpy())
        high_risk.append(torch.stack([torch.sigmoid(output["high_risk_logit"]) for output in outputs]).mean(0).cpu().numpy())
        labels.append(batch_data["label"].numpy())
    arrays = {
        "labels": np.concatenate(labels),
        "probabilities": np.concatenate(probabilities),
        "triage_scores": np.concatenate(triage),
        "high_risk_scores": np.concatenate(high_risk),
    }
    return metrics_from_predictions(**arrays), arrays


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed" / "cric_grade_grouped")
    parser.add_argument("--out", type=Path, default=ROOT / "models" / "cric_grade_cv")
    parser.add_argument("--fold", type=int, choices=range(1, 6), required=True)
    parser.add_argument("--epochs", type=int, default=18)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--batch", type=int, default=48)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--crop-size", type=int, default=320)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=2e-4)
    parser.add_argument("--seed", type=int, default=20260725)
    args = parser.parse_args()

    seed_everything(args.seed + args.fold)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    fold_dir = args.data / f"fold_{args.fold}"
    train_data = CricCellDataset(fold_dir / "train.csv", args.image_size, args.crop_size, train=True)
    val_data = CricCellDataset(fold_dir / "val.csv", args.image_size, args.crop_size, train=False)
    test_data = CricCellDataset(fold_dir / "test.csv", args.image_size, args.crop_size, train=False)
    train_loader = loader(train_data, args.batch, args.workers, train=True)
    val_loader = loader(val_data, args.batch, args.workers)
    model = GradeResearchNet("efficientnet_b0", pretrained=True, dropout=0.25).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_state, best_metrics, best_epoch, patience = None, None, 0, args.patience
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        started = time.time()
        for batch_data in train_loader:
            images = batch_data["image"].to(device, non_blocking=True)
            labels = batch_data["label"].to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                output = model(images)
                loss = multitask_loss(
                    output, labels, batch_data["mask"].to(device), batch_data["mask_available"].to(device),
                    class_weights=None, label_smoothing=0.03, segmentation_weight=0.0,
                    hierarchy_weight=0.20, ordinal_weight=0.12,
                )["loss"]
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            total_loss += float(loss.detach()) * len(labels)
        scheduler.step()
        validation, _ = evaluate(model, val_loader, device, tta=False)
        record = {"epoch": epoch, "seconds": time.time() - started, "loss": total_loss / len(train_data), "validation": validation}
        history.append(record)
        print(json.dumps({"fold": args.fold, "epoch": epoch, "loss": record["loss"], "val_accuracy": validation["accuracy"], "val_macro_f1": validation["macro_f1"], "val_score": validation["selection_score"]}), flush=True)
        if best_metrics is None or validation["selection_score"] > best_metrics["selection_score"] + 1e-5:
            best_state = copy.deepcopy({name: value.detach().cpu() for name, value in model.state_dict().items()})
            best_metrics, best_epoch, patience = validation, epoch, args.patience
        else:
            patience -= 1
            if patience <= 0:
                break

    if best_state is None:
        raise RuntimeError("no validation checkpoint selected")
    model.load_state_dict(best_state)
    test_metrics, arrays = evaluate(model, loader(test_data, args.batch, args.workers), device, tta=True)
    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"cric_b0_grouped_fold_{args.fold}"
    torch.save({"state_dict": best_state, "fold": args.fold, "best_epoch": best_epoch, "validation_metrics": best_metrics, "test_metrics": test_metrics, "classes": GRADE_CLASSES}, args.out / f"{stem}.pt")
    np.savez_compressed(args.out / f"{stem}_oof.npz", **arrays)
    result = {
        "experiment": {**vars(args), "data": str(args.data), "out": str(args.out)},
        "split_unit": "CRIC parent microscope image",
        "best_epoch": best_epoch,
        "validation": best_metrics,
        "test_tta": test_metrics,
        "history": history,
        "claim_gate": "Do not claim cross-validated performance until all five parent-image-disjoint folds are complete.",
    }
    (args.out / f"{stem}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": stem, "test_tta": test_metrics}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
