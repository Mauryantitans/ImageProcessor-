import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class OtsuThresholdOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Otsu Threshold",
            description="Automatic thresholding using Otsu's method",
            icon="📊"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(
            gray,
            0,
            self._params['maxval'],
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'maxval': 255
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'maxval': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'step': 1,
                'default': 255,
                'label': 'Max Value'
            }
        }

class AdaptiveThresholdOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Adaptive Threshold",
            description="Local adaptive thresholding",
            icon="🎯"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray,
            self._params['maxval'],
            cv2.ADAPTIVE_THRESH_MEAN_C if self._params['method'] == 'mean' else cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            self._params['blocksize'],
            self._params['c']
        )
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'maxval': 255,
            'method': 'mean',
            'blocksize': 11,
            'c': 2
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'maxval': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'step': 1,
                'default': 255,
                'label': 'Max Value'
            },
            'method': {
                'type': 'select',
                'options': [
                    {'value': 'mean', 'label': 'Mean'},
                    {'value': 'gaussian', 'label': 'Gaussian'}
                ],
                'default': 'mean',
                'label': 'Method'
            },
            'blocksize': {
                'type': 'range',
                'min': 3,
                'max': 99,
                'step': 2,
                'default': 11,
                'label': 'Block Size'
            },
            'c': {
                'type': 'range',
                'min': -10,
                'max': 10,
                'step': 1,
                'default': 2,
                'label': 'C Value'
            }
        } 