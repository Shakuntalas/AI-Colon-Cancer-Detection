import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score

def evaluate_model():
    model_path = os.path.join("trained_models", "efficientnetb0_colon_new.h5")
    model = tf.keras.models.load_model(model_path)
    
    dataset_path = os.path.expanduser("~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets")
    aca_dir = os.path.join(dataset_path, "colon_aca")
    n_dir = os.path.join(dataset_path, "colon_n")
    
    classes = ['colon_aca', 'colon_n']
    print(f"Training used classes parameter: {classes}")
    print(f"CLASS_LABELS used during inference (in verify script): {classes}")
    print(f"Index 0 -> {classes[0]}, Index 1 -> {classes[1]}")
    
    # Get 10 images from each
    aca_images = [os.path.join(aca_dir, f) for f in os.listdir(aca_dir)[:10]]
    n_images = [os.path.join(n_dir, f) for f in os.listdir(n_dir)[:10]]
    
    y_true = []
    y_pred = []
    
    def process_images(img_paths, true_label_idx):
        for img_path in img_paths:
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)  # Removed / 255.0
            
            pred_probs = model.predict(img_array, verbose=0)
            pred_idx = np.argmax(pred_probs)
            
            y_true.append(true_label_idx)
            y_pred.append(pred_idx)
            print(f"Image: {os.path.basename(img_path)} | True: {classes[true_label_idx]} | Pred: {classes[pred_idx]} | Probs: {pred_probs}")

    print("\n--- Testing colon_aca images ---")
    process_images(aca_images, 0)
    
    print("\n--- Testing colon_n images ---")
    process_images(n_images, 1)
    
    cm = confusion_matrix(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    
    print("\n--- Results ---")
    print("Confusion Matrix:")
    print(cm)
    print(f"Accuracy: {acc:.4f}")

if __name__ == "__main__":
    evaluate_model()
