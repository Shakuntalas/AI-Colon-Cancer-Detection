import os
import tensorflow as tf
import numpy as np

def test_gradcam_model():
    model_path = os.path.join("trained_models", "efficientnetb0_colon.h5")
    model = tf.keras.models.load_model(model_path)
    
    # 1. Why model.input is undefined?
    # Because it's a Sequential without InputLayer explicitly tracking inputs when saved/loaded.
    # We can fix it by calling model.build() or just passing the input shape explicitly.
    try:
        print("Model input:", model.input)
    except Exception as e:
        print(f"Exception getting model.input: {e}")
        
    # Create a dummy tensor and call it
    dummy_input = tf.zeros((1, 224, 224, 3))
    _ = model(dummy_input)
    print("Model inputs after call:", model.inputs)
    
    # 2. Get the target layer
    layer_name = 'top_conv'
    
    # Let's find the base model.
    # Usually it's model.layers[0] if it's named 'efficientnetb0'
    base_model = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):
            base_model = layer
            break
            
    if base_model:
        print(f"Found base model: {base_model.name}")
        # Build a GradCAM model.
        # But wait, grad_model needs to take the original image tensor and output BOTH the conv layer AND the final prediction.
        # If we use base_model.input, we have to run the rest of the Sequential model to get the final predictions!
        
        try:
            target_layer = base_model.get_layer(layer_name)
            
            grad_model = tf.keras.models.Model(
                inputs=base_model.inputs,
                outputs=[target_layer.output, base_model.output]
            )
            
            with tf.GradientTape() as tape:
                conv_outputs, base_output = grad_model(dummy_input)
                x = base_output
                for layer in model.layers[1:]:
                    x = layer(x)
                predictions = x
                loss = predictions[:, 0]
                
            grads = tape.gradient(loss, conv_outputs)
            print("Successfully computed gradients! Shape:", grads.shape)
            
        except Exception as e:
            print(f"Failed to create grad_model: {e}")
    else:
        print("No base model found inside the sequential model.")

if __name__ == "__main__":
    test_gradcam_model()
