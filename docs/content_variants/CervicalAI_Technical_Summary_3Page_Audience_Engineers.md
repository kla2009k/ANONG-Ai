# CervicalAI Technical Summary — 3-Page Version for Engineers & Researchers

**Core Model**: EfficientNet-B0 transfer ImageNet, 5-class Bethesda + koilocyte binary head (multi-task optional)

**Loss**: Weighted CE or Focal , primary metric Recall(HSIL+SCC)

**XAI**: Grad-CAM (target HSIL/koil) + MC Dropout (n=15-20) → entropy + std for defer

**Pipeline**: download → prep (stratified, aug albumentations) → train (SWA/TTA optional v2) → eval_xai → server FastAPI + predictor

**Z-Stack**: ml/zstack_edf.py Laplacian fuse + multi-channel input

**WSI Stub**: wsi_mil.py grid patches + topK attention

**Report**: template 2-layer (no LLM Phase1) + embed heatmap

**Metrics Target Phase1**: Recall>0.90 , ECE<0.10 , uncertainty corr with error

**Repro**: All config dumped, random seeds, docker/requirements ready

**Next for contributors**: Thai data fine-tune, conformal prediction, ONNX export

(Full expanded with code snippets, benchmark numbers from artifacts, architecture ascii)
