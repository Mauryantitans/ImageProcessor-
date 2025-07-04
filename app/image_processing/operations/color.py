import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class GrayscaleOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Grayscale",
            description="Convert to black and white",
            icon="⚫"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {}

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {}

class BrightnessOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Brightness",
            description="Adjust image brightness",
            icon="☀️"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        value = self._params['value']
        if value > 0:
            return cv2.addWeighted(image, 1, np.zeros_like(image), 0, value)
        else:
            return cv2.addWeighted(image, 1, np.zeros_like(image), 0, value)

    def default_params(self) -> Dict[str, Any]:
        return {
            'value': 0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'value': {
                'type': 'range',
                'min': -100,
                'max': 100,
                'default': 0
            }
        }

class ContrastOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Contrast",
            description="Adjust image contrast",
            icon="◐"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        value = self._params['value']
        factor = (259 * (value + 255)) / (255 * (259 - value))
        return cv2.addWeighted(
            image, factor, 
            np.zeros_like(image), 0, 
            128 * (1 - factor)
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'value': 0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'value': {
                'type': 'range',
                'min': -100,
                'max': 100,
                'default': 0
            }
        }

class SaturationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Saturation",
            description="Adjust color saturation",
            icon="🎨"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        value = self._params['value']
        
        # Convert value from -100 to 100 range to 0 to 2 range
        # -100 -> 0 (no saturation)
        # 0 -> 1 (original saturation)
        # 100 -> 2 (double saturation)
        saturation_factor = (value + 100) / 100
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Adjust saturation
        hsv[..., 1] = hsv[..., 1] * saturation_factor
        
        # Clip values to valid range
        hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
        
        # Convert back to uint8 and BGR color space
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'value': 0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'value': {
                'type': 'range',
                'min': -100,
                'max': 100,
                'default': 0
            }
        }

class HueOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Hue Rotation",
            description="Rotate image hue",
            icon="🌈"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        value = self._params['value']
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # OpenCV uses H: 0-179, S: 0-255, V: 0-255
        # Convert UI value (0-360) to OpenCV range (0-179)
        hue_shift = int((value % 360) * 179 / 360.0)
        
        # Add hue shift and wrap around
        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
        
        # Convert back to uint8 and BGR
        hsv = hsv.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'value': 0
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'value': {
                'type': 'range',
                'min': 0,
                'max': 360,
                'default': 0
            }
        } 