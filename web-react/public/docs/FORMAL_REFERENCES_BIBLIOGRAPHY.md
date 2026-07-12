# Formal References Bibliography

Last updated: 2026-07-07

Use this bibliography for the formal research report, poster, and slide deck.
These sources support framing, terminology, methods, and governance. They do
not create new model-performance claims. Model-performance claims must still
come from canonical project files under `models/*.json`.

## Public Health and Screening

1. World Health Organization. (2026). *Cervical cancer*. Fact sheet, 3 July
   2026. https://www.who.int/news-room/fact-sheets/detail/cervical-cancer

2. Centers for Disease Control and Prevention. (2025). *Screening for cervical
   cancer*. https://www.cdc.gov/cervical-cancer/screening/index.html

3. World Health Organization. (2020). *Global strategy to accelerate the
   elimination of cervical cancer as a public health problem*. World Health
   Organization.

## Cytology Terminology and Dataset

4. Nayar, R., & Wilbur, D. C. (Eds.). (2015). *The Bethesda System for
   Reporting Cervical Cytology: Definitions, Criteria, and Explanatory Notes*
   (3rd ed.). Springer.

5. Jantzen, J., Norup, J., Dounias, G., & Bjerregaard, B. (2005).
   Pap-smear benchmark data for pattern classification. *Nature Inspired Smart
   Information Systems (NiSIS 2005)*.

## Model, Explainability, and Uncertainty

6. Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking model scaling for
   convolutional neural networks. *Proceedings of the 36th International
   Conference on Machine Learning (ICML)*. https://arxiv.org/abs/1905.11946

7. Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., &
   Batra, D. (2017). Grad-CAM: Visual explanations from deep networks via
   gradient-based localization. *IEEE International Conference on Computer
   Vision (ICCV)*. https://arxiv.org/abs/1610.02391

8. Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian approximation:
   Representing model uncertainty in deep learning. *Proceedings of the 33rd
   International Conference on Machine Learning (ICML)*.
   https://arxiv.org/abs/1506.02142

## Medical-AI Governance and Reporting

9. U.S. Food and Drug Administration, Health Canada, & Medicines and Healthcare
   products Regulatory Agency. (2021). *Good Machine Learning Practice for
   Medical Device Development: Guiding Principles*.
   https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles

10. International Medical Device Regulators Forum. (2025). *Good Machine
    Learning Practice for Medical Device Development: Guiding Principles*.
    IMDRF.

11. Liu, X., Cruz Rivera, S., Moher, D., Calvert, M. J., Denniston, A. K., &
    the SPIRIT-AI and CONSORT-AI Working Group. (2020). Reporting guidelines
    for clinical trial reports for interventions involving artificial
    intelligence: The CONSORT-AI extension. *Nature Medicine, 26*, 1364-1374.
    https://doi.org/10.1038/s41591-020-1034-x

12. Vasey, B., Nagendran, M., Campbell, B., Clifton, D. A., Collins, G. S.,
    Denaxas, S., Denniston, A. K., et al. (2022). Reporting guideline for the
    early-stage clinical evaluation of decision support systems driven by
    artificial intelligence: DECIDE-AI. *Nature Medicine, 28*, 924-933.
    https://doi.org/10.1038/s41591-022-01772-9

13. Finlayson, S. G., Subbaswamy, A., Singh, K., Bowers, J., Kupke, A.,
    Zittrain, J., Kohane, I. S., & Saria, S. (2021). The clinician and dataset
    shift in artificial intelligence. *New England Journal of Medicine, 385*,
    283-286.

## Project Evidence

14. Project canonical evidence files. (2026). `models/test_metrics.json`,
    `models/triage_metrics.json`, `models/cv_results.json`,
    `models/calibration_temperature.json`. Project_CervicalAI repository.

15. Project governance documents. (2026). `docs/CLAIMS_LEDGER.md`,
    `docs/INTENDED_USE_STATEMENT.md`, `docs/VALIDATION_ROADMAP.md`,
    `docs/SOURCE_CITATION_LEDGER.md`. Project_CervicalAI repository.

## Usage Notes

- WHO/CDC sources support problem framing and screening terminology only.
- Bethesda sources support class-label language and cytology terminology.
- EfficientNet, Grad-CAM, and MC Dropout sources support method descriptions.
- GMLP, CONSORT-AI, and DECIDE-AI support governance and evaluation planning.
- Only canonical project files support CerviCo-Pilot performance numbers.
- Do not use external papers to imply Thai-domain validation or clinical
  readiness for this prototype.
