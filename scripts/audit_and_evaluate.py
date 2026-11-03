import os
import hashlib
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support, classification_report

def run_evaluation_audit():
    model_path = os.path.join("trained_models", "efficientnetb0_colon.h5")
    data_dir = os.path.expanduser(
        '~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets'
    )

    print(f"[*] Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    datagen = tf.keras.preprocessing.image.ImageDataGenerator(validation_split=0.2)
    train_gen = datagen.flow_from_directory(
        data_dir, subset='training', classes=['colon_aca', 'colon_n'], shuffle=False
    )
    val_gen = datagen.flow_from_directory(
        data_dir, target_size=(224, 224), batch_size=32, class_mode='categorical',
        subset='validation', classes=['colon_aca', 'colon_n'], shuffle=False
    )

    train_hashes = set()
    for f in train_gen.filenames:
        h = hashlib.md5(open(os.path.join(data_dir, f), 'rb').read()).hexdigest()
        train_hashes.add(h)

    print("[*] Running inference on validation dataset (2,000 images)...")
    preds = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = val_gen.classes

    # Metric calculations - Full 2,000 validation images
    cm_full = confusion_matrix(y_true, y_pred)
    acc_full = accuracy_score(y_true, y_pred)
    p_full, r_full, f1_full, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average='macro')

    print("\n" + "="*60)
    print("FULL VALIDATION SET (2,000 Images)")
    print("="*60)
    print(f"Confusion Matrix:\n{cm_full}")
    print(f"Accuracy:  {acc_full:.4f}")
    print(f"Binary Precision: {p_full:.4f}, Recall: {r_full:.4f}, F1: {f1_full:.4f}")
    print(f"Macro Precision:  {p_macro:.4f}, Recall: {r_macro:.4f}, F1: {f1_macro:.4f}")
    print("\nClassification Report (Full):")
    print(classification_report(y_true, y_pred, target_names=['colon_aca', 'colon_n'], digits=4))

    # Metric calculations - Clean Non-Leaked Set (1,865 images)
    clean_mask = [
        hashlib.md5(open(os.path.join(data_dir, f), 'rb').read()).hexdigest() not in train_hashes
        for f in val_gen.filenames
    ]
    clean_mask = np.array(clean_mask)

    y_true_clean = y_true[clean_mask]
    y_pred_clean = y_pred[clean_mask]

    cm_clean = confusion_matrix(y_true_clean, y_pred_clean)
    acc_clean = accuracy_score(y_true_clean, y_pred_clean)
    p_clean_bin, r_clean_bin, f1_clean_bin, _ = precision_recall_fscore_support(y_true_clean, y_pred_clean, average='binary')
    p_clean_macro, r_clean_macro, f1_clean_macro, _ = precision_recall_fscore_support(y_true_clean, y_pred_clean, average='macro')

    print("\n" + "="*60)
    print(f"CLEAN NON-LEAKED VALIDATION SET ({len(y_true_clean)} Images - Strictly No Train Overlap)")
    print("="*60)
    print(f"Confusion Matrix:\n{cm_clean}")
    print(f"Accuracy:  {acc_clean:.4f}")
    print(f"Binary Precision: {p_clean_bin:.4f}, Recall: {r_clean_bin:.4f}, F1: {f1_clean_bin:.4f}")
    print(f"Macro Precision:  {p_clean_macro:.4f}, Recall: {r_clean_macro:.4f}, F1: {f1_clean_macro:.4f}")
    print("\nClassification Report (Clean Non-Leaked):")
    print(classification_report(y_true_clean, y_pred_clean, target_names=['colon_aca', 'colon_n'], digits=4))

    # Write report file
    report_path = os.path.join("reports", "model_evaluation_audit_report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("# ColonSightAI — Model Evaluation & Dataset Audit Report\n\n")
        rf.write(f"- Model file: `trained_models/efficientnetb0_colon.h5`\n")
        rf.write(f"- Dataset: LC25000 Colon Histopathology (`andrewmvd/lung-and-colon-cancer-histopathological-images`)\n\n")
        rf.write("## 1. Full Validation Set (2,000 Images)\n\n")
        rf.write(f"- **Accuracy**: `{acc_full * 100:.2f}%` ({acc_full:.4f})\n")
        rf.write(f"- **Macro Precision**: `{p_macro * 100:.2f}%`\n")
        rf.write(f"- **Macro Recall**: `{r_macro * 100:.2f}%`\n")
        rf.write(f"- **Macro F1-Score**: `{f1_macro * 100:.2f}%`\n\n")
        rf.write("### Confusion Matrix (Full):\n")
        rf.write("```text\n")
        rf.write(f"[[{cm_full[0, 0]:>4}, {cm_full[0, 1]:>4}],\n")
        rf.write(f" [{cm_full[1, 0]:>4}, {cm_full[1, 1]:>4}]]\n")
        rf.write("```\n\n")
        rf.write("## 2. Clean Non-Leaked Validation Set (1,865 Images)\n\n")
        rf.write(f"- **Accuracy**: `{acc_clean * 100:.2f}%` ({acc_clean:.4f})\n")
        rf.write(f"- **Macro Precision**: `{p_clean_macro * 100:.2f}%`\n")
        rf.write(f"- **Macro Recall**: `{r_clean_macro * 100:.2f}%`\n")
        rf.write(f"- **Macro F1-Score**: `{f1_clean_macro * 100:.2f}%`\n\n")
        rf.write("### Confusion Matrix (Clean):\n")
        rf.write("```text\n")
        rf.write(f"[[{cm_clean[0, 0]:>4}, {cm_clean[0, 1]:>4}],\n")
        rf.write(f" [{cm_clean[1, 0]:>4}, {cm_clean[1, 1]:>4}]]\n")
        rf.write("```\n")

    print(f"\n[OK] Reproducible evaluation audit report written to: {report_path}")

if __name__ == '__main__':
    run_evaluation_audit()

