# 📖 Literature Survey

## Colon Cancer Detection Using Deep Learning

### 1. Introduction

Colon cancer (colorectal cancer) is the third most commonly diagnosed cancer worldwide and the second leading cause of cancer-related deaths. Early detection through histopathological analysis significantly improves patient survival rates. Computer-aided diagnosis (CAD) systems powered by deep learning have shown remarkable potential in automating this process.

---

### 2. Traditional Approaches

| Year | Authors | Method | Accuracy | Limitations |
|---|---|---|---|---|
| 2016 | Sirinukunwattana et al. | Spatially Constrained CNN | 82.7% | Small dataset, limited generalizability |
| 2017 | Korbar et al. | ResNet-based classification | 87.0% | Computationally expensive |
| 2018 | Bychkov et al. | LSTM + CNN | 88.2% | Complex architecture, slow inference |

### 3. Deep Learning Approaches

#### 3.1 Convolutional Neural Networks (CNNs)

CNNs have become the dominant architecture for medical image analysis. Key developments:

- **AlexNet (2012)** — Pioneered deep learning for image classification
- **VGGNet (2014)** — Demonstrated depth matters (16-19 layers)
- **ResNet (2015)** — Introduced skip connections, enabling very deep networks
- **EfficientNet (2019)** — Balanced scaling of depth, width, and resolution

#### 3.2 Transfer Learning

Transfer learning from ImageNet pre-trained models has proven effective for medical imaging where labeled data is scarce:

| Study | Base Model | Dataset | Accuracy |
|---|---|---|---|
| Ghosh et al. (2021) | VGG16 | LC25000 | 96.0% |
| Masud et al. (2021) | ResNet50 | LC25000 | 96.3% |
| Talukder et al. (2022) | EfficientNetB3 | LC25000 | 99.1% |
| Kumar et al. (2022) | EfficientNetB0 | LC25000 | 99.5% |

#### 3.3 EfficientNet Architecture

EfficientNet (Tan & Le, 2019) introduces compound scaling — uniformly scaling network depth, width, and resolution using a compound coefficient. EfficientNetB0 provides an optimal trade-off between accuracy and computational efficiency, making it suitable for clinical deployment.

#### 3.4 Explainable AI in Healthcare

Explainability is critical in clinical AI systems:

- **Grad-CAM** (Selvaraju et al., 2017) — Gradient-based visual explanations
- **LIME** (Ribeiro et al., 2016) — Local interpretable model-agnostic explanations
- **SHAP** (Lundberg & Lee, 2017) — Shapley additive explanations

Grad-CAM is preferred for image-based medical AI due to its ability to generate spatially relevant heatmaps without modifying the model architecture.

---

### 4. Key Datasets

| Dataset | Images | Classes | Resolution | Source |
|---|---|---|---|---|
| LC25000 | 25,000 | 5 | 768×768 | Borkowski et al. (2019) |
| CRC-VAL-HE-7K | 7,180 | 9 | 150×150 | Kather et al. (2019) |
| BreakHis | 9,109 | 8 | 700×460 | Spanhol et al. (2016) |

---

### 5. References

1. Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. *ICML 2019*.
2. Selvaraju, R.R. et al. (2017). Grad-CAM: Visual Explanations from Deep Networks. *ICCV 2017*.
3. Borkowski, A.A. et al. (2019). Lung and Colon Cancer Histopathological Image Dataset (LC25000). *arXiv:1912.12142*.
4. Kumar, A. et al. (2022). Colon Cancer Detection Using EfficientNet with Transfer Learning. *IJERT*.
5. Talukder, M.A. et al. (2022). Machine Learning-Based Lung and Colon Cancer Detection. *Scientific Reports*.

---

> **TODO**: Expand with additional references as research progresses.
