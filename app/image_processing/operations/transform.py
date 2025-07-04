import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class RotateOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Rotate",
            description="Rotate image by degrees",
            icon="🔄"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        angle = self._params['angle']
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new image dimensions
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Adjust translation
        matrix[0, 2] += (new_width / 2) - center[0]
        matrix[1, 2] += (new_height / 2) - center[1]
        
        # Perform rotation
        return cv2.warpAffine(image, matrix, (new_width, new_height))

    def default_params(self) -> Dict[str, Any]:
        return {
            'angle': 0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'angle': {
                'type': 'range',
                'min': -180,
                'max': 180,
                'default': 0
            }
        }

class FlipOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Flip",
            description="Flip image horizontally or vertically",
            icon="↔️"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        direction = self._params['direction']
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        else:  # vertical
            return cv2.flip(image, 0)

    def default_params(self) -> Dict[str, Any]:
        return {
            'direction': 'horizontal'
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'direction': {
                'type': 'select',
                'options': ['horizontal', 'vertical'],
                'default': 'horizontal'
            }
        } 