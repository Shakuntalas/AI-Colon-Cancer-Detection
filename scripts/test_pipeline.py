import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tensorflow as tf
from app.ai.predictor import Predictor
from app.ai.gradcam import GradCAMGenerator
from app.ai.preprocessor import ImagePreprocessor
from app.ai.model_loader import ModelLoader

def test_pipeline():
    print("Testing programmatic integration...")
    
    model = ModelLoader().get_model()
    
    dataset_path = os.path.expanduser("~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets")
    img_path = os.path.join(dataset_path, "colon_aca", "colonca1.jpeg")
    
    # Preprocess
    preprocessor = ImagePreprocessor()
    tensor = preprocessor.preprocess(img_path)
    print("Preprocessed shape:", tensor.shape)
    
    # Predict
    predictor = Predictor()
    result = predictor.predict(tensor, model)
    print("Prediction Result:", result)
    
    # GradCAM
    class_idx = 0 if result['predicted_class'] == 'colon_aca' else 1
    gen = GradCAMGenerator()
    heatmap = gen.generate(img_path, model, class_idx)
    print("GradCAM heatmap saved at:", heatmap)
    
    print("End-to-end programmatic pipeline succeeded!")

if __name__ == "__main__":
    test_pipeline()
