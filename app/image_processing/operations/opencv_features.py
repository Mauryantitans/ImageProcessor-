import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class SIFTDetectionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="SIFT Features",
            description="Detect SIFT keypoints and descriptors",
            icon="🔍"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create SIFT detector
        sift = cv2.SIFT_create(
            nfeatures=self._params['max_features'],
            contrastThreshold=self._params['contrast_threshold'] / 100.0,
            edgeThreshold=self._params['edge_threshold']
        )
        
        # Detect keypoints
        keypoints = sift.detect(gray, None)
        
        # Draw keypoints
        return cv2.drawKeypoints(
            image, keypoints, None,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            color=(0, 255, 0)
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'max_features': 100,
            'contrast_threshold': 10,
            'edge_threshold': 10
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'max_features': {
                'type': 'range',
                'min': 10,
                'max': 1000,
                'default': 100
            },
            'contrast_threshold': {
                'type': 'range',
                'min': 1,
                'max': 50,
                'default': 10
            },
            'edge_threshold': {
                'type': 'range',
                'min': 1,
                'max': 50,
                'default': 10
            }
        }

class ORBDetectionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="ORB Features",
            description="Detect ORB keypoints (faster alternative to SIFT)",
            icon="🎯"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create ORB detector
        orb = cv2.ORB_create(
            nfeatures=self._params['max_features'],
            scaleFactor=1.2,
            nlevels=self._params['scale_levels']
        )
        
        # Detect keypoints
        keypoints = orb.detect(gray, None)
        
        # Draw keypoints
        return cv2.drawKeypoints(
            image, keypoints, None,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            color=(0, 255, 0)
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'max_features': 500,
            'scale_levels': 8
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'max_features': {
                'type': 'range',
                'min': 100,
                'max': 2000,
                'default': 500
            },
            'scale_levels': {
                'type': 'range',
                'min': 3,
                'max': 15,
                'default': 8
            }
        }

class BlobDetectionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Blob Detection",
            description="Detect blobs using SimpleBlobDetector",
            icon="⭕"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Setup SimpleBlobDetector parameters
        params = cv2.SimpleBlobDetector_Params()
        
        # Threshold params
        params.minThreshold = 10
        params.maxThreshold = 200
        params.thresholdStep = 10
        
        # Area params
        params.filterByArea = True
        params.minArea = self._params['min_area']
        params.maxArea = self._params['max_area']
        
        # Circularity params
        params.filterByCircularity = self._params['filter_circularity']
        params.minCircularity = self._params['min_circularity'] / 100.0
        
        # Create detector
        detector = cv2.SimpleBlobDetector_create(params)
        
        # Detect blobs
        keypoints = detector.detect(image)
        
        # Draw blobs
        return cv2.drawKeypoints(
            image, keypoints, None,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            color=(0, 255, 0)
        )

    def default_params(self) -> Dict[str, Any]:
        return {
            'min_area': 100,
            'max_area': 5000,
            'filter_circularity': True,
            'min_circularity': 80
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'min_area': {
                'type': 'range',
                'min': 10,
                'max': 1000,
                'default': 100
            },
            'max_area': {
                'type': 'range',
                'min': 1000,
                'max': 10000,
                'default': 5000
            },
            'filter_circularity': {
                'type': 'select',
                'options': [True, False],
                'default': True
            },
            'min_circularity': {
                'type': 'range',
                'min': 10,
                'max': 100,
                'default': 80
            }
        }

class GoodFeaturesToTrackOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Good Features",
            description="Detect good features to track using Shi-Tomasi method",
            icon="📌"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect corners
        corners = cv2.goodFeaturesToTrack(
            gray,
            maxCorners=self._params['max_corners'],
            qualityLevel=self._params['quality_level'] / 100.0,
            minDistance=self._params['min_distance'],
            blockSize=3
        )
        
        # Draw corners
        result = image.copy()
        if corners is not None:
            corners = np.int0(corners)
            for corner in corners:
                x, y = corner.ravel()
                cv2.circle(result, (x, y), 3, (0, 255, 0), -1)
                
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'max_corners': 50,
            'quality_level': 1,
            'min_distance': 10
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'max_corners': {
                'type': 'range',
                'min': 10,
                'max': 200,
                'default': 50
            },
            'quality_level': {
                'type': 'range',
                'min': 1,
                'max': 99,
                'default': 1
            },
            'min_distance': {
                'type': 'range',
                'min': 5,
                'max': 50,
                'default': 10
            }
        } 