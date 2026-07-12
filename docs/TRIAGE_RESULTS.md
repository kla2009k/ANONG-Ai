# Triage & 5-class Results — with bootstrap 95% CI (honest, real Herlev held-out)
> efficientnet_b0 · best_cervical.pt · n_test=137 · TTA=True · bootstrap n=2000

## Binary Triage (ปกติ vs ผิดปกติ) — headline
| ตัวชี้วัด | ค่า (95% CI) |
|---|---|
| **Sensitivity** | **1.0 (1.0–1.0)** |
| **AUROC** | **0.964 (0.9249–0.991)** |
| **AUPRC** | 0.9856 (0.9686–0.9972) |
| Accuracy | 0.927 (0.8759–0.9708) |
| Balanced Accuracy | 0.8611 |
| Specificity | 0.7222 (0.5714–0.8621) |
| **MCC** | 0.8107 (0.7045–0.9092) |
| PPV / NPV | 0.9099 / 1.0 |
| F1 / Youden J | 0.9528 / 0.7222 |
| Confusion | TP 101 · TN 26 · FP 10 · FN 0 |

**High-risk catch (HSIL+SCC): 1.0**

## 5-class (Bethesda, ordinal)
| ตัวชี้วัด | ค่า (95% CI) |
|---|---|
| Accuracy | 0.6934 (0.6131–0.7666) |
| **Quadratic Weighted Kappa** (ordinal) | **0.687 (0.561–0.7974)** |
| Balanced Accuracy | 0.698 (0.614–0.7729) |
| MCC | 0.6167 |
| Recall (HSIL+SCC) | 0.75 · Macro F1 0.5545 · AUC 0.7311 |

| กลุ่ม | support | recall | precision | f1 |
|---|---|---|---|---|
| NILM | 36 | 0.7222 | 0.9286 | 0.8125 |
| LSIL | 49 | 0.6122 | 0.9677 | 0.75 |
| HSIL | 30 | 0.8667 | 0.4483 | 0.5909 |
| SCC | 22 | 0.5909 | 0.65 | 0.619 |
| KOIL | 0 | 0.0 | 0.0 | 0.0 |

*CI = bootstrap percentile 95%. QWK เหมาะกับ Bethesda เพราะเป็น ordinal. ดู k-fold ใน docs/CV_RESULTS.md*