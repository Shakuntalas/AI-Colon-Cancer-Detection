import tensorflow as tf
import os

model_path = 'trained_models/efficientnetb0_colon.h5'

try:
    model = tf.keras.models.load_model(model_path)
    print("1. Valid Keras model: Yes")
    print(f"2. Architecture/Layers: {[layer.name for layer in model.layers]}")
    print(f"3. Trainable parameters: {model.count_params()}")
    print(f"4. Input shape: {model.input_shape}")
    print(f"5. Output layer: {model.layers[-1].name} ({type(model.layers[-1]).__name__})")
    print(f"6. Classes (output shape): {model.output_shape}")
except Exception as e:
    print(f"Error loading model: {e}")
