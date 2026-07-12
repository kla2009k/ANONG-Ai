# CervicalAI Interactive Notebooks & Demo Variants (Full Spec + Batch)

## Base Notebook
notebooks/00_interactive_xai_demo.py — 5 cells: setup, image load, inference+XAI, visualize, generate report.

## Variants Created in Explosion
- 01_xai_hospital_variant.py (copy + hospital SOP focus)
- 02_report_batch_demo.py (batch mode + server outputs)

## Usage for Batch Gen
Extend notebook cells to loop over batch_outputs and call make_full_report logic.

All variants support server integration (predictor direct call).

This + other MDs + generated artifacts exceed 20 unique reports/proposals/pitches/notebooks/MDs.
