import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class BlurOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Gaussian Blur",
            description="Apply gaussian blur effect",
            icon="🌫️"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        radius = self._params['radius']
        # Ensure radius is odd
        if radius % 2 == 0:
            radius += 1
        return cv2.GaussianBlur(image, (radius, radius), 0)

    def default_params(self) -> Dict[str, Any]:
        return {
            'radius': 5
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'radius': {
                'type': 'range',
                'min': 1,
                'max': 50,
                'default': 5
            }
        }

class SharpenOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Sharpen",
            description="Enhance image sharpness",
            icon="✨"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        amount = self._params['amount'] / 100.0
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        sharpened = cv2.filter2D(image, -1, kernel * amount)
        return cv2.addWeighted(image, 1 - amount, sharpened, amount, 0)

    def default_params(self) -> Dict[str, Any]:
        return {
            'amount': 50
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'amount': {
                'type': 'range',
                'min': 0,
                'max': 100,
                'default': 50
            }
        }

class BilateralFilterOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Bilateral Filter",
            description="Edge-preserving smoothing filter",
            icon="🔍"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        return cv2.bilateralFilter(
            image,
            self._params['diameter'],
            self._params['sigma_color'],
            self._params['sigma_space']
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'diameter': 9,
            'sigma_color': 75,
            'sigma_space': 75
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'diameter': {
                'type': 'range',
                'min': 1,
                'max': 30,
                'step': 2,
                'default': 9,
                'label': 'Diameter'
            },
            'sigma_color': {
                'type': 'range',
                'min': 10,
                'max': 150,
                'step': 5,
                'default': 75,
                'label': 'Color Sigma'
            },
            'sigma_space': {
                'type': 'range',
                'min': 10,
                'max': 150,
                'step': 5,
                'default': 75,
                'label': 'Space Sigma'
            }
        }

class GaussianBlurOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Gaussian Blur",
            description="Gaussian smoothing filter",
            icon="🌫️"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        ksize = self._params['kernel_size']
        return cv2.GaussianBlur(
            image,
            (ksize, ksize),
            self._params['sigma']
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'kernel_size': 5,
            'sigma': 1.0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'kernel_size': {
                'type': 'range',
                'min': 1,
                'max': 31,
                'step': 2,
                'default': 5,
                'label': 'Kernel Size'
            },
            'sigma': {
                'type': 'range',
                'min': 0.1,
                'max': 10.0,
                'step': 0.1,
                'default': 1.0,
                'label': 'Sigma'
            }
        } 