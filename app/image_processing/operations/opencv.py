import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class CannyEdgeOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Canny Edge",
            description="Detect edges using Canny algorithm",
            icon="🔲"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        threshold1 = self._params['threshold1']
        threshold2 = self._params['threshold2']
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply Canny edge detection
        edges = cv2.Canny(gray, threshold1, threshold2)
        
        # Convert back to BGR for consistency
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'threshold1': 100,
            'threshold2': 200
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'threshold1': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'default': 100
            },
            'threshold2': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'default': 200
            }
        }

class AdaptiveThresholdOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Adaptive Threshold",
            description="Apply adaptive thresholding",
            icon="⬜"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        block_size = self._params['block_size']
        if block_size % 2 == 0:
            block_size += 1  # Must be odd
            
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C if self._params['method'] == 'gaussian' else cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY if self._params['threshold_type'] == 'binary' else cv2.THRESH_BINARY_INV,
            block_size,
            self._params['c']
        )
        
        # Convert back to BGR for consistency
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'block_size': 11,
            'c': 2,
            'method': 'gaussian',
            'threshold_type': 'binary'
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'block_size': {
                'type': 'range',
                'min': 3,
                'max': 99,
                'step': 2,
                'default': 11
            },
            'c': {
                'type': 'range',
                'min': -10,
                'max': 10,
                'default': 2
            },
            'method': {
                'type': 'select',
                'options': ['gaussian', 'mean'],
                'default': 'gaussian'
            },
            'threshold_type': {
                'type': 'select',
                'options': ['binary', 'binary_inv'],
                'default': 'binary'
            }
        }

class ContourDrawOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Draw Contours",
            description="Find and draw contours in the image",
            icon="📏"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, self._params['threshold'], 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create output image
        result = image.copy()
        
        # Draw contours
        cv2.drawContours(
            result, 
            contours, 
            -1,  # Draw all contours
            (0, 255, 0),  # Green color
            self._params['thickness']
        )
        
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'threshold': 127,
            'thickness': 2
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'threshold': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'default': 127
            },
            'thickness': {
                'type': 'range',
                'min': 1,
                'max': 10,
                'default': 2
            }
        }

class MorphologyOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Morphology",
            description="Apply morphological operations (erosion, dilation, etc.)",
            icon="🔄"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        operation = self._params['operation']
        kernel_size = self._params['kernel_size']
        iterations = self._params['iterations']
        
        # Create kernel
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        # Apply morphological operation
        if operation == 'erode':
            return cv2.erode(image, kernel, iterations=iterations)
        elif operation == 'dilate':
            return cv2.dilate(image, kernel, iterations=iterations)
        elif operation == 'open':
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == 'close':
            return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        else:  # gradient
            return cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel, iterations=iterations)

    def default_params(self) -> Dict[str, Any]:
        return {
            'operation': 'dilate',
            'kernel_size': 3,
            'iterations': 1
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'operation': {
                'type': 'select',
                'options': ['erode', 'dilate', 'open', 'close', 'gradient'],
                'default': 'dilate'
            },
            'kernel_size': {
                'type': 'range',
                'min': 1,
                'max': 15,
                'step': 2,
                'default': 3
            },
            'iterations': {
                'type': 'range',
                'min': 1,
                'max': 10,
                'default': 1
            }
        }

class CornerDetectionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Corner Detection",
            description="Detect corners using Harris or FAST algorithm",
            icon="📍"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        method = self._params['method']
        result = image.copy()
        
        if method == 'harris':
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = np.float32(gray)
            
            # Detect corners
            corners = cv2.cornerHarris(
                gray, 
                blockSize=2, 
                ksize=3, 
                k=self._params['k'] / 100.0
            )
            
            # Normalize and threshold
            corners = cv2.dilate(corners, None)
            threshold = self._params['threshold'] / 100.0
            result[corners > threshold * corners.max()] = [0, 0, 255]
            
        else:  # FAST
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect corners
            fast = cv2.FastFeatureDetector_create(
                threshold=self._params['threshold']
            )
            keypoints = fast.detect(gray, None)
            
            # Draw corners
            return cv2.drawKeypoints(
                image, 
                keypoints, 
                None, 
                color=(0, 0, 255)
            )
            
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'method': 'harris',
            'threshold': 10,
            'k': 5
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'method': {
                'type': 'select',
                'options': ['harris', 'fast'],
                'default': 'harris'
            },
            'threshold': {
                'type': 'range',
                'min': 1,
                'max': 50,
                'default': 10
            },
            'k': {
                'type': 'range',
                'min': 1,
                'max': 20,
                'default': 5,
                'description': 'Harris corner detector free parameter'
            }
        }

class ColorSpaceOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Color Space",
            description="Convert image between different color spaces",
            icon="🎨"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        space = self._params['space']
        
        if space == 'gray':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        elif space == 'hsv':
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        elif space == 'lab':
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        elif space == 'yuv':
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:  # luv
            luv = cv2.cvtColor(image, cv2.COLOR_BGR2LUV)
            return cv2.cvtColor(luv, cv2.COLOR_LUV2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'space': 'hsv'
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'space': {
                'type': 'select',
                'options': ['gray', 'hsv', 'lab', 'yuv', 'luv'],
                'default': 'hsv'
            }
        }

class HistogramEqualizationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Histogram Equalization",
            description="Enhance image contrast using histogram equalization",
            icon="📊"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        method = self._params['method']
        
        if method == 'global':
            # Convert to YUV
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            # Equalize Y channel
            yuv[..., 0] = cv2.equalizeHist(yuv[..., 0])
            # Convert back to BGR
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:  # CLAHE
            # Convert to LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            # Create CLAHE object
            clahe = cv2.createCLAHE(
                clipLimit=self._params['clip_limit'],
                tileGridSize=(8, 8)
            )
            # Apply CLAHE to L channel
            lab[..., 0] = clahe.apply(lab[..., 0])
            # Convert back to BGR
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def default_params(self) -> Dict[str, Any]:
        return {
            'method': 'clahe',
            'clip_limit': 2
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'method': {
                'type': 'select',
                'options': ['global', 'clahe'],
                'default': 'clahe'
            },
            'clip_limit': {
                'type': 'range',
                'min': 1,
                'max': 10,
                'default': 2,
                'description': 'Threshold for contrast limiting in CLAHE'
            }
        } 