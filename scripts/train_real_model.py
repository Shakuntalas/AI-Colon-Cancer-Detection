import os
import sys
import kagglehub
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam

def get_dataset_path():
    print("Downloading/Locating dataset via kagglehub...")
    path = kagglehub.dataset_download("andrewmvd/lung-and-colon-cancer-histopathological-images")
    
    # Check possible paths
    colon_dir = os.path.join(path, "lung_colon_image_set", "colon_image_sets")
    if not os.path.exists(colon_dir):
        # Maybe it's directly at the root
        colon_dir = os.path.join(path, "colon_image_sets")
        if not os.path.exists(colon_dir):
            raise FileNotFoundError(f"Could not find colon_image_sets inside {path}")
    
    return colon_dir

def build_model(input_shape=(224, 224, 3), num_classes=2):
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=input_shape)
    
    # Freeze the base model
    base_model.trainable = False

    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax' if num_classes > 1 else 'sigmoid')
    ])

    # For a binary classification with one-hot encoded outputs from ImageDataGenerator (class_mode='categorical'), use categorical_crossentropy.
    # We will use class_mode='categorical' and num_classes=2
    model.compile(optimizer=Adam(learning_rate=0.001), 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    
    return model

def main():
    try:
        data_dir = get_dataset_path()
        print(f"Dataset located at: {data_dir}")
    except Exception as e:
        print(f"Error locating dataset: {e}")
        sys.exit(1)

    # Use a small subset or fewer epochs so that we can train it relatively quickly
    # but still create a real trained model.
    batch_size = 32
    img_size = (224, 224)
    epochs = 3 # Kept small so it finishes in a reasonable time, user didn't specify accuracy target, just real model

    datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        validation_split=0.2 # 20% for validation
    )

    train_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        classes=['colon_aca', 'colon_n']
    )

    val_generator = datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        classes=['colon_aca', 'colon_n']
    )

    model = build_model()
    model.summary()

    # Callbacks
    save_path = os.path.join(os.path.dirname(__file__), "..", "trained_models", "efficientnetb0_colon_new.h5")
    
    callbacks = [
        EarlyStopping(patience=2, restore_best_weights=True, monitor='val_accuracy'),
        ModelCheckpoint(save_path, save_best_only=True, monitor='val_accuracy')
    ]

    print("Starting training...")
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=val_generator,
        callbacks=callbacks
    )

    print("Training finished!")
    
    # Print accuracy
    val_acc = history.history.get('val_accuracy')
    train_acc = history.history.get('accuracy')
    
    if val_acc and train_acc:
        print(f"Final Training Accuracy: {train_acc[-1]:.4f}")
        print(f"Final Validation Accuracy: {val_acc[-1]:.4f}")
    
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    main()
