# 5-Fold Cross-Validation (honest, real Herlev 917 imgs)
> efficientnet_b0 · stratified · TTA=True · mean ± SD across 5 folds

## Binary Triage (ปกติ vs ผิดปกติ)
| ตัวชี้วัด | mean ± SD |
|---|---|
| **Sensitivity** | **0.9867 ± 0.0086** |
| **AUROC** | **0.9435 ± 0.0448** |
| AUPRC | 0.9756 ± 0.0217 |
| Specificity | 0.691 ± 0.1151 |
| Balanced Accuracy | 0.8388 ± 0.0591 |
| MCC | 0.7564 ± 0.0923 |

## 5-class (Bethesda, ordinal)
| ตัวชี้วัด | mean ± SD |
|---|---|
| Accuracy | 0.6904 ± 0.0618 |
| **Quadratic Weighted Kappa** | **0.6981 ± 0.0866** |
| Balanced Accuracy | 0.701 ± 0.0579 |
| MCC | 0.5995 ± 0.0786 |
| Recall (HSIL+SCC) | 0.6859 ± 0.0553 |
| Macro F1 | 0.5482 ± 0.0475 · AUC 0.7271 ± 0.0249 |

*k-fold = robust กว่า single split; รายงาน mean±SD. per-fold ใน models/cv_results.json*