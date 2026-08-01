import os
import argparse
import logging
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.model_config import (
    IMAGE_SIZE, NUM_CLASSES, TRAINING_CONFIG, MODEL_PATH
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_mock_model():
    """Generates a dummy mock model for testing the inference pipeline quickly."""
    logger.info("Generating mock model for testing...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    inputs = layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    # EfficientNetB0's last conv layer is named 'top_conv'
    # We add a layer named 'top_conv' so Grad-CAM works.
    x = layers.Conv2D(32, (3, 3), padding='same', name='top_conv')(inputs)
    x = layers.GlobalAveragePooling2D()(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = models.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.save(MODEL_PATH)
    logger.info(f"Mock model saved to {MODEL_PATH}")


def train_model(dataset_dir):
    """Full EfficientNetB0 training pipeline."""
    logger.info("Initializing EfficientNetB0 training pipeline...")
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(MODEL_PATH)), 'logs', 'fit')
    os.makedirs(log_dir, exist_ok=True)
    
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_dir,
        validation_split=TRAINING_CONFIG['validation_split'],
        subset="training",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=TRAINING_CONFIG['batch_size'],
        label_mode='categorical'
    )
    
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_dir,
        validation_split=TRAINING_CONFIG['validation_split'],
        subset="validation",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=TRAINING_CONFIG['batch_size'],
        label_mode='categorical'
    )
    
    # Data Augmentation
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ])
    
    # Model Architecture
    base_model = EfficientNetB0(
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base model initially
    
    inputs = layers.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    x = data_augmentation(inputs)
    
    # EfficientNet expects unnormalized inputs (it has its own normalization)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = models.Model(inputs, outputs)
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=TRAINING_CONFIG['learning_rate']),
        loss=TRAINING_CONFIG['loss'],
        metrics=TRAINING_CONFIG['metrics']
    )
    
    callbacks = [
        EarlyStopping(patience=TRAINING_CONFIG['early_stopping_patience'], restore_best_weights=True),
        ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_loss'),
        TensorBoard(log_dir=log_dir),
        ReduceLROnPlateau(patience=TRAINING_CONFIG['reduce_lr_patience'], factor=TRAINING_CONFIG['reduce_lr_factor'])
    ]
    
    logger.info("Starting training...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=TRAINING_CONFIG['epochs'],
        callbacks=callbacks
    )
    
    logger.info(f"Training complete. Model saved to {MODEL_PATH}")
    return history


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train AI Colon Cancer Detection Model')
    parser.add_argument('--dataset', type=str, default='datasets/colon_image_sets', help='Path to dataset directory')
    parser.add_argument('--mock', action='store_true', help='Generate a mock model for testing pipeline')
    args = parser.parse_args()
    
    if args.mock:
        generate_mock_model()
    else:
        if not os.path.exists(args.dataset):
            logger.error(f"Dataset directory not found: {args.dataset}")
            sys.exit(1)
        train_model(args.dataset)
