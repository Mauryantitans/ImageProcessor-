import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class SepiaOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Sepia",
            description="Apply vintage sepia effect",
            icon="🌅"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        intensity = self._params['intensity'] / 100.0
        
        # Convert to float32
        image_float = image.astype(np.float32) / 255.0
        
        # Sepia matrix
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        # Apply sepia effect
        sepia_image = cv2.transform(image_float, sepia_matrix)
        sepia_image = np.clip(sepia_image * 255, 0, 255).astype(np.uint8)
        
        # Blend with original based on intensity
        return cv2.addWeighted(image, 1 - intensity, sepia_image, intensity, 0)

    def default_params(self) -> Dict[str, Any]:
        return {
            'intensity': 100
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'intensity': {
                'type': 'range',
                'min': 0,
                'max': 100,
                'default': 100
            }
        } 