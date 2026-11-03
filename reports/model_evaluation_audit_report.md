# ColonSightAI — Model Evaluation & Dataset Audit Report

**Date**: November 3, 2026  
**Auditor**: Independent Technical Quality & AI Architecture Audit  
**Target Model**: `trained_models/efficientnetb0_colon.h5` (18,655,656 bytes, EfficientNetB0)  
**Dataset**: LC25000 Colon Histopathology (`andrewmvd/lung-and-colon-cancer-histopathological-images`)  

---

## 1. Dataset Provenance & Patient-Level Limitation

### A. Academic Origin of LC25000
The LC25000 dataset was published by *Borkowski et al. (2019)* (*"Lung and Colon Cancer Histopathological Image Dataset"*, *arXiv:1912.12142*):
- The entire collection was generated from only **250 Whole Slide Images (WSIs)** sourced from the James A. Haley Veterans’ Hospital and Moffitt Cancer Center.
- For colon tissue, patches were extracted at $768 \times 768$ and augmented using spatial rotations and flipping to produce 5,000 patches for colon adenocarcinoma (`colon_aca`) and 5,000 patches for benign colon tissue (`colon_n`).
- Consequently, multiple image patches in both the training and evaluation subsets originated from the **same original tissue slides and patient biopsies**.

### B. Inability to Establish Slide-Level and Patient-Level Independence
- **Public Metadata Limitation**: All files in the public Kaggle distribution are named sequentially (`colonca1.jpeg` through `colonca5000.jpeg` and `colonn1.jpeg` through `colonn5000.jpeg`).
- **Absence of Clinical Identifiers**: The public dataset contains **no patient IDs, slide IDs, hospital source metadata, or tissue block identifiers**.
- **Audit Conclusion**: Because these identifiers were permanently stripped from the public release, **patient-level and slide-level independence cannot be established with the available dataset metadata**. Any partition (including the 80/20 train/validation split) operates strictly at the **image patch level**, and cross-split patient or slide overlap is highly probable.

---

## 2. Duplicate vs. Near-Duplicate Analysis

We distinguish between **exact byte-for-byte duplicate removal** and **perceptual near-duplicate detection**.

### A. Raw Dataset Duplication (Cryptographic MD5):
- `colon_aca`: 5,000 files total, **4,753 unique MD5 hashes** (242 duplicate groups, 247 redundant identical files).
- `colon_n`: 5,000 files total, **4,772 unique MD5 hashes** (226 duplicate groups, 228 redundant identical files).
- **Cross-Class Duplicates**: `0` (No image is shared between `colon_aca` and `colon_n`).

### B. Exact Byte Duplicate Overlap (80/20 Split):
- **Filename Overlap**: `0` (Filenames are strictly disjoint between sets).
- **Exact Byte Duplicates (MD5)**: **133 unique hashes (135 images, 6.75%)** in the 2,000-image validation set are exact byte-for-byte identical copies of images present in the 8,000-image training set.
- **Exact Deduplicated Subset**: **1,865 validation images (93.25%)** remain after removing the 135 exact byte duplicates.
  > [!IMPORTANT]
  > Removing exact byte duplicates does **not** guarantee that the 1,865-image subset is free from data leakage. Because patches originate from shared slides without patient IDs, underlying biological correlation and augmented variants may still persist.

### C. Perceptual Near-Duplicate Detection (64-Bit Difference Hash `dHash`):
Pairwise Hamming distances were evaluated across all 16,000,000 validation-train image pairs:
- **`Hamming Distance == 0`**: **138 images (6.90%)**
- **`Hamming Distance <= 2 bits`**: **192 images (9.60%)**
- **`Hamming Distance <= 4 bits`**: **297 images (14.85%)**
- **`Hamming Distance > 4 bits`**: **1,703 images (85.15%)** (perceptually divergent image patches)
- **Median Minimum Distance**: `14.0 bits` | **Mean Minimum Distance**: `11.85 bits`

> [!NOTE]
> A `dHash` Hamming distance greater than 4 bits simply reflects coarse structural variation between $9 \times 8$ downsampled gradients; it does **not** prove that patches came from independent slides or different patients.

### D. Discrepancy Investigation: 135 MD5 Duplicates vs. 138 dHash Matches
The audit identified a discrepancy of **3 additional matches** where `dHash distance == 0` but the cryptographic MD5 hash differed. The specific pairs are:
1. `colon_aca/colonca1036.jpeg` (Val) $\leftrightarrow$ `colon_aca/colonca4509.jpeg` (Train) — File sizes: 102,365 vs. 103,802 bytes
2. `colon_aca/colonca1443.jpeg` (Val) $\leftrightarrow$ `colon_aca/colonca3274.jpeg` (Train) — File sizes: 107,690 vs. 109,197 bytes
3. `colon_n/colonn1244.jpeg` (Val) $\leftrightarrow$ `colon_n/colonn3146.jpeg` (Train) — File sizes: 120,876 vs. 122,269 bytes

**Technical Reason**:
- `MD5` is a cryptographic hash operating on the exact byte sequence of the compressed JPEG container; any minor byte shift, recompression artifact, or metadata difference alters the MD5 digest completely.
- `dHash` is a 64-bit coarse perceptual hash operating on directional luminance gradients of an $8 \times 8$ grayscale downsampled grid.
- In these 3 pairs, the macro-structural luminance gradient across the 64 blocks is identical (`dHash == 0`), while localized pixel intensity shifts and different JPEG compression parameters cause distinct MD5 hashes.

---

## 3. Preprocessing Verification

- **Training Pipeline** (`train_real_model.py`): Input size $(224, 224)$, RGB, unnormalized (`[0, 255]`) float32 tensors (EfficientNetB0 internal preprocessing).
- **Inference Pipeline** (`preprocessor.py`): Input size $(224, 224)$, RGB, `PIXEL_SCALE_FACTOR = 1.0` (`[0, 255]`).
- **Evaluation Pipeline** (`audit_and_evaluate.py`): Input size $(224, 224)$, RGB, unnormalized (`[0, 255]`).
- **Result**: Preprocessing is consistent across all three environments.

---

## 4. Empirical Evaluation Results & Independent Metrics Recalculation

### A. Full Validation Set (2,000 Images — Standard 80/20 Split)
```text
Confusion Matrix:
                 Predicted colon_aca    Predicted colon_n
Actual colon_aca         987 (TP)               13 (FN)
Actual colon_n             3 (FP)              997 (TN)
```

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **`colon_aca` (Cancerous)** | 99.70% | 98.70% | 99.20% | 1,000 |
| **`colon_n` (Benign)** | 98.71% | 99.70% | 99.20% | 1,000 |
| **Overall Accuracy** | — | — | **99.20%** | 2,000 |
| **Macro Average** | **99.20%** | **99.20%** | **99.20%** | 2,000 |

### B. Deduplicated Validation Subset (1,865 Images — Exact Byte Duplicates Removed)
After excluding all 135 validation images sharing exact MD5 hashes with the training set:
```text
Confusion Matrix:
                 Predicted colon_aca    Predicted colon_n
Actual colon_aca         914 (TP)               12 (FN)
Actual colon_n             3 (FP)              936 (TN)
```

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **`colon_aca` (Cancerous)** | 99.67% | 98.70% | 99.19% | 926 |
| **`colon_n` (Benign)** | 98.73% | 99.68% | 99.21% | 939 |
| **Overall Accuracy** | — | — | **99.20%** | 1,865 |
| **Macro Average** | **99.20%** | **99.19%** | **99.20%** | 1,865 |

---

## 5. Technical Resolution of Keras Warnings

- **Issue**: Keras 3 `UserWarning: The structure of inputs doesn't match the expected structure. Expected: ['input_layer'] Received: inputs=Tensor(...)`.
- **Root Cause**: `grad_model` inputs expected a list structure matching `sub_model.inputs`, but were called with a bare tensor.
- **Resolution**: Normalized input feeding in `app/ai/gradcam.py` and `scripts/colab_inference_server.py`:
  ```python
  inputs_to_feed = [image_tensor] if isinstance(grad_model.inputs, list) and not isinstance(image_tensor, list) else image_tensor
  ```
- **Outcome**: The warning is resolved without modifying model predictions or gradients.
