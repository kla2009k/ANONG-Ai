"""Leakage guards, fold-safe ensembling, and explicit promotion gates."""

from __future__ import annotations

import numpy as np


def average_member_predictions(members: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    if not members:
        raise ValueError("at least one ensemble member is required")
    reference = members[0]
    required = ("labels", "groups", "probabilities", "triage_scores", "high_risk_scores")
    if any(key not in reference for key in required):
        raise ValueError("ensemble member is missing required arrays")
    for member in members[1:]:
        if not np.array_equal(member["labels"], reference["labels"]):
            raise ValueError("ensemble labels are not aligned")
        if not np.array_equal(member["groups"], reference["groups"]):
            raise ValueError("ensemble groups are not aligned")
        if member["probabilities"].shape != reference["probabilities"].shape:
            raise ValueError("ensemble probability shapes are not aligned")
    return {
        "labels": reference["labels"].copy(),
        "groups": reference["groups"].copy(),
        "probabilities": np.mean([member["probabilities"] for member in members], axis=0),
        "triage_scores": np.mean([member["triage_scores"] for member in members], axis=0),
        "high_risk_scores": np.mean([member["high_risk_scores"] for member in members], axis=0),
    }


def promotion_gate(per_class_recall: dict[str, float], parent_disjoint: bool,
                   external_lbc_complete: bool, minimum_exact_recall: float = 0.90,
                   external_per_class_recall: dict[str, float] | None = None) -> dict:
    failures = []
    for grade in ("NILM", "LSIL", "HSIL", "SCC"):
        value = per_class_recall.get(grade)
        if value is None or value < minimum_exact_recall:
            rendered = "missing" if value is None else f"{value:.3f}"
            failures.append(f"{grade} exact recall {rendered} is below {minimum_exact_recall:.2f}")
    if not parent_disjoint:
        failures.append("parent-image-disjoint evaluation is not complete")
    if not external_lbc_complete:
        failures.append("external LBC evaluation is not complete")
    elif external_per_class_recall is None:
        failures.append("external LBC per-class recall is missing")
    else:
        for grade in ("NILM", "LSIL", "HSIL", "SCC"):
            value = external_per_class_recall.get(grade)
            if value is None or value < minimum_exact_recall:
                rendered = "missing" if value is None else f"{value:.3f}"
                failures.append(f"external {grade} exact recall {rendered} is below {minimum_exact_recall:.2f}")
    return {
        "passed": not failures,
        "minimum_exact_recall": minimum_exact_recall,
        "failures": failures,
        "effect": "production promotion allowed" if not failures else "research candidate only",
    }
