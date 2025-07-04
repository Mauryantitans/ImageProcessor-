import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class AddNoiseOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Add Noise",
            description="Add random noise to the image",
            icon="🎲"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        amount = self._params['amount'] / 100.0  # Convert to 0-1 range
        noise_type = self._params['type']
        
        # Convert to float32 for processing
        img_float = image.astype(np.float32) / 255.0
        
        if noise_type == 'gaussian':
            # Generate Gaussian noise
            noise = np.random.normal(0, amount * 0.15, image.shape)
            noisy = img_float + noise
        elif noise_type == 'salt_and_pepper':
            # Generate salt and pepper noise
            noisy = img_float.copy()
            # Salt
            salt = np.random.random(image.shape) < (amount * 0.5)
            noisy[salt] = 1
            # Pepper
            pepper = np.random.random(image.shape) < (amount * 0.5)
            noisy[pepper] = 0
        else:  # uniform
            # Generate uniform noise
            noise = np.random.uniform(-amount, amount, image.shape)
            noisy = img_float + noise
            
        # Clip and convert back to uint8
        return np.clip(noisy * 255, 0, 255).astype(np.uint8)

    def default_params(self) -> Dict[str, Any]:
        return {
            'amount': 25,
            'type': 'gaussian'
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'amount': {
                'type': 'range',
                'min': 0,
                'max': 100,
                'default': 25
            },
            'type': {
                'type': 'select',
                'options': ['gaussian', 'uniform', 'salt_and_pepper'],
                'default': 'gaussian'
            }
        }

class DenoiseOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Denoise",
            description="Remove noise from the image",
            icon="✨"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        strength = self._params['strength']
        method = self._params['method']
        
        if method == 'gaussian':
            return cv2.GaussianBlur(image, (0, 0), strength * 0.5)
        elif method == 'median':
            # Ensure kernel size is odd
            ksize = 2 * int(strength / 10) + 1
            return cv2.medianBlur(image, ksize)
        else:  # non_local_means
            return cv2.fastNlMeansDenoisingColored(
                image,
                None,
                strength * 0.1,  # h (filter strength for luminance)
                strength * 0.1,  # hColor (filter strength for color)
                7,              # templateWindowSize
                21             # searchWindowSize
            )

    def default_params(self) -> Dict[str, Any]:
        return {
            'strength': 10,
            'method': 'non_local_means'
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'strength': {
                'type': 'range',
                'min': 1,
                'max': 50,
                'default': 10
            },
            'method': {
                'type': 'select',
                'options': ['gaussian', 'median', 'non_local_means'],
                'default': 'non_local_means'
            }
        } 