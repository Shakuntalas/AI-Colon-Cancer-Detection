import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

def verify_prediction():
    model_path = os.path.join("trained_models", "efficientnetb0_colon.h5")
    print(f"Loading model from {model_path}...")
    
    model = tf.keras.models.load_model(model_path)
    print("Model loaded successfully.")
    
    # Check model size in terms of params
    print(f"Model parameters: {model.count_params():,}")
    
    # Dataset path
    data_dir = os.path.expanduser("~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets/colon_aca")
    
    # Pick a sample image
    sample_img = os.listdir(data_dir)[0]
    img_path = os.path.join(data_dir, sample_img)
    
    print(f"Testing prediction on: {img_path}")
    
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array)
    print(f"Prediction raw output: {prediction}")
    
    classes = ['colon_aca', 'colon_n']
    predicted_class = classes[np.argmax(prediction)]
    print(f"Predicted class: {predicted_class}")

if __name__ == "__main__":
    verify_prediction()
