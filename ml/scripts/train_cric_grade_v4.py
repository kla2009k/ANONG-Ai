#!/usr/bin/env python3
"""Train one fold-safe multi-scale CRIC ensemble member."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.cric_grade_data import CricCellDataset, parent_balanced_sample_weights
from ml.grade_research_v3 import GRADE_CLASSES, MultiScaleGradeResearchNet, multitask_loss
from ml.scripts.train_cric_grade_cv import metrics_from_predictions
from ml.scripts.train_grade_research_v3 import seed_everything


def make_loader(dataset: CricCellDataset, batch: int, workers: int,
                train: bool = False, class_power: float = 0.5) -> DataLoader:
    sampler = None
    if train:
        weights = parent_balanced_sample_weights(dataset.rows, class_power=class_power)
        sampler = WeightedRandomSampler(torch.as_tensor(weights, dtype=torch.double), len(dataset), replacement=True)
    return DataLoader(
        dataset, batch_size=batch, sampler=sampler, shuffle=False, num_workers=workers,
        pin_memory=torch.cuda.is_available(), persistent_workers=train and workers > 0,
    )


def loss_class_weights(rows: list[dict[str, str]], power: float, device: torch.device) -> torch.Tensor | None:
    if power <= 0:
        return None
    counts = Counter(int(row["label5"]) for row in rows)
    values = np.asarray([(len(rows) / counts[index]) ** power for index in range(4)], dtype=np.float32)
    values /= values.mean()
    return torch.as_tensor(values, device=device)


@torch.no_grad()
def evaluate(model, data_loader, device, tta: bool = False) -> tuple[dict, dict[str, np.ndarray]]:
    model.eval()
    labels, probabilities, triage, high_risk, groups = [], [], [], [], []
    for batch_data in data_loader:
        cells = batch_data["image"].to(device, non_blocking=True)
        contexts = batch_data["context_image"].to(device, non_blocking=True)
        variants = [(cells, contexts)]
        if tta:
            variants.extend([
                (torch.flip(cells, (-1,)), torch.flip(contexts, (-1,))),
                (torch.flip(cells, (-2,)), torch.flip(contexts, (-2,))),
            ])
        outputs = [model(cell, context) for cell, context in variants]
        probabilities.append(torch.stack([torch.softmax(output["grade_logits"], 1) for output in outputs]).mean(0).cpu().numpy())
        triage.append(torch.stack([torch.sigmoid(output["triage_logit"]) for output in outputs]).mean(0).cpu().numpy())
        high_risk.append(torch.stack([torch.sigmoid(output["high_risk_logit"]) for output in outputs]).mean(0).cpu().numpy())
        labels.append(batch_data["label"].numpy())
        groups.extend(batch_data["group_id"])
    arrays = {
        "labels": np.concatenate(labels),
        "probabilities": np.concatenate(probabilities),
        "triage_scores": np.concatenate(triage),
        "high_risk_scores": np.concatenate(high_risk),
        "groups": np.asarray(groups),
    }
    return metrics_from_predictions(
        arrays["labels"], arrays["probabilities"], arrays["triage_scores"], arrays["high_risk_scores"]
    ), arrays


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/cric_grade_grouped")
    parser.add_argument("--out", type=Path, default=ROOT / "models/cric_grade_v4")
    parser.add_argument("--fold", type=int, choices=range(1, 6), required=True)
    parser.add_argument("--member", type=int, default=1)
    parser.add_argument("--architecture", choices=("efficientnet_b0", "convnext_tiny"), default="efficientnet_b0")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--crop-size", type=int, default=320)
    parser.add_argument("--context-crop-size", type=int, default=640)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=3e-4)
    parser.add_argument("--sampler-class-power", type=float, default=0.5)
    parser.add_argument("--loss-class-power", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--limit-train", type=int)
    parser.add_argument("--limit-val", type=int)
    parser.add_argument("--limit-test", type=int)
    args = parser.parse_args()

    effective_seed = args.seed + 1000 * args.member + args.fold
    seed_everything(effective_seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    fold_dir = args.data / f"fold_{args.fold}"
    dataset_args = (args.image_size, args.crop_size)
    train_data = CricCellDataset(
        fold_dir / "train.csv", *dataset_args, train=True, context_crop_size=args.context_crop_size
    )
    val_data = CricCellDataset(
        fold_dir / "val.csv", *dataset_args, train=False, context_crop_size=args.context_crop_size
    )
    test_data = CricCellDataset(
        fold_dir / "test.csv", *dataset_args, train=False, context_crop_size=args.context_crop_size
    )
    for dataset, limit in (
        (train_data, args.limit_train), (val_data, args.limit_val), (test_data, args.limit_test)
    ):
        if limit is not None:
            if limit <= 0:
                raise ValueError("smoke-test limits must be positive")
            dataset.rows = dataset.rows[:limit]
    smoke_test_only = any(value is not None for value in (args.limit_train, args.limit_val, args.limit_test))
    train_loader = make_loader(train_data, args.batch, args.workers, True, args.sampler_class_power)
    val_loader = make_loader(val_data, args.batch, 0)
    model = MultiScaleGradeResearchNet(
        args.architecture, pretrained=not args.no_pretrained, dropout=0.30
    ).to(device)
    class_weights = loss_class_weights(train_data.rows, args.loss_class_power, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    best_state, best_metrics, best_epoch, patience_left = None, None, 0, args.patience
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss, started = 0.0, time.time()
        for batch_data in train_loader:
            cells = batch_data["image"].to(device, non_blocking=True)
            contexts = batch_data["context_image"].to(device, non_blocking=True)
            labels = batch_data["label"].to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                output = model(cells, contexts)
                loss = multitask_loss(
                    output, labels, batch_data["mask"].to(device), batch_data["mask_available"].to(device),
                    class_weights=class_weights, label_smoothing=0.03, segmentation_weight=0.0,
                    hierarchy_weight=0.25, ordinal_weight=0.15,
                )["loss"]
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            total_loss += float(loss.detach()) * len(labels)
        scheduler.step()
        validation, _ = evaluate(model, val_loader, device)
        record = {
            "epoch": epoch, "seconds": time.time() - started,
            "loss": total_loss / len(train_data), "validation": validation,
        }
        history.append(record)
        print(json.dumps({
            "fold": args.fold, "member": args.member, "epoch": epoch,
            "loss": record["loss"], "val_accuracy": validation["accuracy"],
            "val_macro_f1": validation["macro_f1"], "val_score": validation["selection_score"],
        }), flush=True)
        if best_metrics is None or validation["selection_score"] > best_metrics["selection_score"] + 1e-5:
            best_state = copy.deepcopy({name: value.detach().cpu() for name, value in model.state_dict().items()})
            best_metrics, best_epoch, patience_left = validation, epoch, args.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_state is None:
        raise RuntimeError("no validation checkpoint selected")
    model.load_state_dict(best_state)
    test_metrics, arrays = evaluate(model, make_loader(test_data, args.batch, 0), device, tta=True)
    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"cric_v4_{args.architecture}_fold_{args.fold}_member_{args.member}"
    torch.save({
        "state_dict": best_state, "fold": args.fold, "member": args.member,
        "architecture": args.architecture, "best_epoch": best_epoch,
        "validation_metrics": best_metrics, "test_metrics": test_metrics, "classes": GRADE_CLASSES,
        "crop_size": args.crop_size, "context_crop_size": args.context_crop_size,
    }, args.out / f"{stem}.pt")
    np.savez_compressed(args.out / f"{stem}_oof.npz", **arrays)
    result = {
        "experiment": {**vars(args), "data": str(args.data), "out": str(args.out), "effective_seed": effective_seed},
        "split_unit": "CRIC parent microscope image",
        "best_epoch": best_epoch,
        "validation": best_metrics,
        "test_tta": test_metrics,
        "history": history,
        "status": "smoke_test_only" if smoke_test_only else "research_candidate_only",
        "claim_gate": (
            "Smoke-test artifact; metrics are invalid for model claims."
            if smoke_test_only else
            "Research candidate only until all folds, fold-safe ensemble, and external LBC evaluation complete."
        ),
    }
    (args.out / f"{stem}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": stem, "test_tta": test_metrics}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
