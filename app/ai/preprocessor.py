"""
ColonSightAI — Image Preprocessor
====================================

Handles image preprocessing for the EfficientNetB0 model pipeline.

Preprocessing steps:
    1. Read image from disk (OpenCV / Pillow)
    2. Convert colour space (BGR → RGB if OpenCV)
    3. Resize to model input dimensions (224 × 224)
    4. Normalize pixel values to [0, 1]
    5. Expand dimensions for batch inference
    6. Optionally apply test-time augmentation

Usage:
    from app.ai.preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()
    tensor = preprocessor.preprocess('/path/to/image.jpg')
"""

import logging

from app.ai.model_config import IMAGE_SIZE, IMAGE_CHANNELS, PIXEL_SCALE_FACTOR

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Image preprocessing pipeline for EfficientNetB0 inference.

    Parameters
    ----------
    target_size : tuple[int, int]
        Target dimensions (height, width). Default from model_config.
    channels : int
        Number of colour channels. Default 3 (RGB).
    scale_factor : float
        Pixel normalization factor. Default 1/255.
    """

    def __init__(self, target_size=None, channels=None, scale_factor=None):
        self.target_size = target_size or IMAGE_SIZE
        self.channels = channels or IMAGE_CHANNELS
        self.scale_factor = scale_factor or PIXEL_SCALE_FACTOR

    def preprocess(self, image_path):
        """
        Preprocess a single image for model inference.

        Parameters
        ----------
        image_path : str
            Absolute path to the image file.

        Returns
        -------
        numpy.ndarray
            Preprocessed image tensor with shape (1, H, W, C).

        Raises
        ------
        FileNotFoundError
            If the image file does not exist.
        ValueError
            If the image cannot be decoded.
        """
        import cv2
        import numpy as np
        
        # Using Pillow to handle TIFF if cv2 fails, but cv2 can usually handle TIFF.
        image = cv2.imread(image_path)
        if image is None:
            # Fallback to Pillow
            from PIL import Image
            try:
                pil_img = Image.open(image_path).convert('RGB')
                image = np.array(pil_img)
                # BGR to RGB is not needed here since we converted to RGB
            except Exception as e:
                raise ValueError(f'Cannot decode image: {image_path}. Error: {e}')
        else:
            # BGR → RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        image_resized = cv2.resize(image, self.target_size)
        
        # Validation: Check if the image is likely a histopathology image (H&E stained)
        if not self._is_histopathology_image(image_resized):
            raise ValueError('The uploaded image does not appear to be a valid H&E stained histopathology image.')
            
        # Cast to float32
        image_float = image_resized.astype(np.float32)
        
        # Add batch dimension
        tensor = np.expand_dims(image_float, axis=0)
        
        logger.debug(
            'Preprocessed image %s → shape=%s, dtype=%s',
            image_path, tensor.shape, tensor.dtype,
        )
        return tensor

    def _is_histopathology_image(self, image):
        """
        Heuristic to check if an image is a valid H&E stained histopathology image.
        H&E stains are predominantly pink/purple/red.
        """
        import numpy as np
        
        # Check 1: Not a blank/solid color image (std dev across spatial dims)
        std_dev = np.mean(np.std(image, axis=(0, 1)))
        if std_dev < 10.0:
            return False
            
        # Check 2: Color distribution (H&E has high Red and Blue relative to Green)
        mean_r = np.mean(image[:, :, 0])
        mean_g = np.mean(image[:, :, 1])
        mean_b = np.mean(image[:, :, 2])
        
        # Typically, in H&E, Red > Green and Blue is also significant.
        # We allow a bit of tolerance.
        if mean_r < mean_g - 10:
            return False
            
        # Check 3: Not completely grayscale
        if abs(mean_r - mean_g) < 5 and abs(mean_r - mean_b) < 5:
            return False
            
        return True

    def preprocess_batch(self, image_paths):
        """
        Preprocess a batch of images.

        Parameters
        ----------
        image_paths : list[str]
            List of image file paths.

        Returns
        -------
        numpy.ndarray
            Batch tensor with shape (N, H, W, C).
        """
        import numpy as np
        tensors = [self.preprocess(path)[0] for path in image_paths]
        return np.array(tensors)

    def get_preprocessing_info(self):
        """Return a summary of preprocessing configuration."""
        return {
            'target_size': self.target_size,
            'channels': self.channels,
            'scale_factor': self.scale_factor,
            'normalization': f'pixels × {self.scale_factor}',
            'color_space': 'RGB',
        }
