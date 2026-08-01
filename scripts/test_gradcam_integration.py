import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tensorflow as tf
from app.ai.gradcam import GradCAMGenerator
from app.ai.model_config import MODEL_PATH
import cv2

def test_gradcam():
    model = tf.keras.models.load_model(MODEL_PATH)
    
    # Grab a sample image
    dataset_path = os.path.expanduser("~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets")
    img_path = os.path.join(dataset_path, "colon_aca", "colonca1.jpeg")
    
    gen = GradCAMGenerator()
    try:
        heatmap_path = gen.generate(img_path, model, 0)
        print(f"Success! Heatmap saved at {heatmap_path}")
        assert os.path.exists(heatmap_path)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gradcam()
