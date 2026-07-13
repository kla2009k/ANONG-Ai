#!/usr/bin/env python3
"""Train and evaluate a real-data SIPaKMeD koilocytosis morphology model."""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import random
import sys
import time
from collections import Counter

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.koil_data import SIPAK_CLASSES
from ml.koil_model import build_koil_model


MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
KOIL_INDEX = SIPAK_CLASSES.index("Koilocytotic")


class SipakDataset(Dataset):
    def __init__(self, manifest: pathlib.Path, image_size: int, train: bool):
        with manifest.open(encoding="utf-8") as handle:
            self.rows = list(csv.DictReader(handle))
        if train:
            self.transform = transforms.Compose([
                transforms.RandomResizedCrop(image_size, scale=(0.72, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(20),
                transforms.ColorJitter(0.15, 0.15, 0.1, 0.04),
                transforms.ToTensor(),
                transforms.Normalize(MEAN, STD),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(MEAN, STD),
            ])

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int):
        row = self.rows[index]
        with Image.open(row["path"]) as image:
            tensor = self.transform(image.convert("RGB"))
        return tensor, int(row["sipak_label"]), row["group_id"], row["path"]


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


@torch.no_grad()
def infer(model: nn.Module, loader: DataLoader, device: torch.device) -> dict:
    model.eval()
    logits, labels, groups, paths = [], [], [], []
    for images, target, batch_groups, batch_paths in loader:
        logits.append(model(images.to(device)).cpu())
        labels.append(target)
        groups.extend(batch_groups)
        paths.extend(batch_paths)
    logits_array = torch.cat(logits).numpy()
    labels_array = torch.cat(labels).numpy()
    probabilities = torch.softmax(torch.from_numpy(logits_array), dim=1).numpy()
    return {
        "logits": logits_array,
        "probabilities": probabilities,
        "labels": labels_array,
        "groups": np.asarray(groups),
        "paths": paths,
    }


def multiclass_metrics(payload: dict) -> dict:
    labels = payload["labels"]
    probabilities = payload["probabilities"]
    predictions = probabilities.argmax(axis=1)
    matrix = confusion_matrix(labels, predictions, labels=np.arange(len(SIPAK_CLASSES)))
    return {
        "accuracy": float((predictions == labels).mean()),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "per_class_recall": {
            name: float(recall_score(labels == index, predictions == index, zero_division=0))
            for index, name in enumerate(SIPAK_CLASSES)
        },
        "confusion_matrix": matrix.tolist(),
    }


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    logits_tensor = torch.tensor(logits, dtype=torch.float32)
    labels_tensor = torch.tensor(labels, dtype=torch.long)
    log_temperature = torch.nn.Parameter(torch.zeros(()))
    optimizer = torch.optim.LBFGS([log_temperature], lr=0.1, max_iter=100, line_search_fn="strong_wolfe")

    def closure():
        optimizer.zero_grad()
        temperature = log_temperature.exp().clamp(0.05, 20.0)
        loss = torch.nn.functional.cross_entropy(logits_tensor / temperature, labels_tensor)
        loss.backward()
        return loss

    optimizer.step(closure)
    return float(log_temperature.detach().exp().clamp(0.05, 20.0))


def apply_temperature(payload: dict, temperature: float) -> dict:
    calibrated = dict(payload)
    calibrated["probabilities"] = torch.softmax(
        torch.from_numpy(payload["logits"]) / temperature, dim=1
    ).numpy()
    return calibrated


def choose_koil_threshold(labels: np.ndarray, scores: np.ndarray, minimum_sensitivity: float) -> dict:
    binary = (labels == KOIL_INDEX).astype(int)
    candidates = np.unique(np.concatenate(([0.0, 1.0], scores)))
    feasible = []
    for threshold in candidates:
        predicted = (scores >= threshold).astype(int)
        sensitivity = recall_score(binary, predicted, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(binary, predicted, labels=[0, 1]).ravel()
        specificity = tn / (tn + fp) if tn + fp else 0.0
        precision = precision_score(binary, predicted, zero_division=0)
        feasible.append((sensitivity >= minimum_sensitivity, specificity, precision, threshold, sensitivity))
    eligible = [row for row in feasible if row[0]]
    selected = max(eligible or feasible, key=lambda row: (row[0], row[1], row[2], row[3]))
    return {
        "threshold": float(selected[3]),
        "validation_sensitivity": float(selected[4]),
        "validation_specificity": float(selected[1]),
        "minimum_sensitivity_target": minimum_sensitivity,
    }


def binary_koil_metrics(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    binary = (labels == KOIL_INDEX).astype(int)
    predicted = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(binary, predicted, labels=[0, 1]).ravel()
    brier = float(np.mean((scores - binary) ** 2))
    ece = 0.0
    edges = np.linspace(0.0, 1.0, 11)
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (scores >= lower) & (scores < upper if upper < 1.0 else scores <= upper)
        if mask.any():
            ece += float(mask.mean()) * abs(float(scores[mask].mean()) - float(binary[mask].mean()))
    return {
        "support_positive": int(binary.sum()),
        "support_negative": int((1 - binary).sum()),
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
        "sensitivity": float(tp / (tp + fn)) if tp + fn else math.nan,
        "specificity": float(tn / (tn + fp)) if tn + fp else math.nan,
        "precision": float(tp / (tp + fp)) if tp + fp else math.nan,
        "f1": float(f1_score(binary, predicted, zero_division=0)),
        "auroc": float(roc_auc_score(binary, scores)),
        "auprc": float(average_precision_score(binary, scores)),
        "brier_score": brier,
        "ece_10_bin": ece,
        "threshold": float(threshold),
    }


def cluster_bootstrap_ci(payload: dict, threshold: float, iterations: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    groups = payload["groups"]
    unique_groups = np.unique(groups)
    values = {key: [] for key in (
        "sensitivity", "specificity", "precision", "f1", "auroc", "auprc", "brier_score", "ece_10_bin"
    )}
    for _ in range(iterations):
        sampled = rng.choice(unique_groups, size=len(unique_groups), replace=True)
        indexes = np.concatenate([np.flatnonzero(groups == group) for group in sampled])
        labels = payload["labels"][indexes]
        if len(np.unique(labels == KOIL_INDEX)) < 2:
            continue
        metrics = binary_koil_metrics(labels, payload["probabilities"][indexes, KOIL_INDEX], threshold)
        for key in values:
            if np.isfinite(metrics[key]):
                values[key].append(metrics[key])
    return {
        key: {
            "lower_95": float(np.quantile(samples, 0.025)),
            "upper_95": float(np.quantile(samples, 0.975)),
            "bootstrap_samples": len(samples),
        }
        for key, samples in values.items() if samples
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path, default=ROOT / "data" / "processed" / "sipakmed_koil_grouped")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--seed", type=int, default=20260713)
    parser.add_argument("--minimum-koil-sensitivity", type=float, default=0.95)
    parser.add_argument("--bootstrap", type=int, default=2000)
    args = parser.parse_args()

    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Keep the locked test manifest unopened until training, model selection,
    # calibration, and threshold selection are complete.
    datasets = {
        split: SipakDataset(args.data / f"{split}.csv", args.image_size, split == "train")
        for split in ("train", "val")
    }
    loaders = {
        split: DataLoader(
            dataset,
            batch_size=args.batch,
            shuffle=split == "train",
            num_workers=2,
            pin_memory=device.type == "cuda",
        )
        for split, dataset in datasets.items()
    }

    counts = Counter(int(row["sipak_label"]) for row in datasets["train"].rows)
    class_weights = torch.tensor(
        [len(datasets["train"]) / (len(SIPAK_CLASSES) * counts[index]) for index in range(len(SIPAK_CLASSES))],
        dtype=torch.float32,
        device=device,
    )
    model = build_koil_model(pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.03)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    best_score = -1.0
    best_state = None
    patience_left = args.patience
    history = []
    for epoch in range(1, args.epochs + 1):
        started = time.time()
        model.train()
        running_loss = 0.0
        for images, target, _, _ in loaders["train"]:
            images, target = images.to(device), target.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                output = model(images)
                loss = criterion(output, target)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item() * len(target)
        scheduler.step()

        validation = infer(model, loaders["val"], device)
        metrics = multiclass_metrics(validation)
        koil_recall = metrics["per_class_recall"]["Koilocytotic"]
        selection_score = 0.5 * metrics["macro_f1"] + 0.5 * koil_recall
        record = {
            "epoch": epoch,
            "train_loss": running_loss / len(datasets["train"]),
            "val_macro_f1": metrics["macro_f1"],
            "val_koil_recall": koil_recall,
            "selection_score": selection_score,
            "seconds": time.time() - started,
        }
        history.append(record)
        print(json.dumps(record))
        if selection_score > best_score + 1e-5:
            best_score = selection_score
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            patience_left = args.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_state is None:
        raise RuntimeError("training did not produce a checkpoint")
    model.load_state_dict(best_state)
    validation = infer(model, loaders["val"], device)
    temperature = fit_temperature(validation["logits"], validation["labels"])
    validation = apply_temperature(validation, temperature)
    threshold = choose_koil_threshold(
        validation["labels"], validation["probabilities"][:, KOIL_INDEX], args.minimum_koil_sensitivity
    )

    # The locked test manifest is opened only after model and threshold selection.
    test_dataset = SipakDataset(args.data / "test.csv", args.image_size, train=False)
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch,
        shuffle=False,
        num_workers=2,
        pin_memory=device.type == "cuda",
    )
    test_payload = apply_temperature(infer(model, test_loader, device), temperature)
    test_multiclass = multiclass_metrics(test_payload)
    test_koil = binary_koil_metrics(
        test_payload["labels"], test_payload["probabilities"][:, KOIL_INDEX], threshold["threshold"]
    )
    intervals = cluster_bootstrap_ci(test_payload, threshold["threshold"], args.bootstrap, args.seed + 1)
    result = {
        "dataset": "SIPaKMeD",
        "endpoint": "koilocytosis morphology one-vs-rest",
        "domain": "conventional Pap-smear single-cell crops; not ThinPrep and not HPV DNA/RNA",
        "split_unit": "original source cluster",
        "classes": list(SIPAK_CLASSES),
        "seed": args.seed,
        "counts": {
            "train": len(datasets["train"]),
            "val": len(datasets["val"]),
            "test": len(test_dataset),
        },
        "validation_threshold_selection": threshold,
        "temperature_scaling": {
            "temperature": temperature,
            "fit_split": "validation",
            "test_used_for_fit": False,
        },
        "test_multiclass": test_multiclass,
        "test_koil": test_koil,
        "cluster_bootstrap_95_ci": intervals,
        "history": history,
    }
    output_dir = ROOT / "models" / "koil_sipakmed"
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": best_state,
        "arch": "efficientnet_b0",
        "classes": list(SIPAK_CLASSES),
        "koil_index": KOIL_INDEX,
        "koil_threshold": threshold["threshold"],
        "temperature": temperature,
        "img_size": args.image_size,
        "mean": MEAN,
        "std": STD,
        "dataset": "SIPaKMeD",
        "split_unit": "source_cluster",
    }, output_dir / "best_koil_model.pt")
    (output_dir / "test_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    predictions = []
    for index, path in enumerate(test_payload["paths"]):
        predictions.append({
            "path": path,
            "group_id": str(test_payload["groups"][index]),
            "true_label": int(test_payload["labels"][index]),
            "predicted_label": int(test_payload["probabilities"][index].argmax()),
            "koil_probability": float(test_payload["probabilities"][index, KOIL_INDEX]),
        })
    (output_dir / "locked_test_predictions.json").write_text(json.dumps(predictions, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
