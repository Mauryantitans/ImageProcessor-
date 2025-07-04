import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class WatershedSegmentationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Watershed Segmentation",
            description="Segment image using watershed algorithm",
            icon="💧"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Sure background
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # Finding sure foreground
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, self._params['foreground_threshold'] * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        
        # Finding unknown region
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # Apply watershed
        markers = cv2.watershed(image, markers)
        
        # Color the segments
        result = image.copy()
        result[markers == -1] = [0, 0, 255]  # Boundaries in red
        
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'foreground_threshold': 20
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'foreground_threshold': {
                'type': 'range',
                'min': 1,
                'max': 90,
                'default': 20,
                'description': 'Threshold percentage for sure foreground'
            }
        }

class GrabCutSegmentationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="GrabCut Segmentation",
            description="Segment image using GrabCut algorithm",
            icon="✂️"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Create mask
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Calculate rectangle based on margin
        margin = self._params['margin']
        rect = (
            margin,
            margin,
            image.shape[1] - margin * 2,
            image.shape[0] - margin * 2
        )
        
        # Temporary arrays
        bgdModel = np.zeros((1,65), np.float64)
        fgdModel = np.zeros((1,65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(
            image, mask, rect,
            bgdModel, fgdModel,
            self._params['iterations'],
            cv2.GC_INIT_WITH_RECT
        )
        
        # Create mask for probable and definite foreground
        mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
        
        # Apply mask to image
        result = image * mask2[:,:,np.newaxis]
        
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'margin': 10,
            'iterations': 5
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'margin': {
                'type': 'range',
                'min': 5,
                'max': 100,
                'default': 10,
                'description': 'Margin from image edges'
            },
            'iterations': {
                'type': 'range',
                'min': 1,
                'max': 10,
                'default': 5,
                'description': 'Number of iterations'
            }
        }

class KMeansSegmentationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="K-Means Segmentation",
            description="Segment image using K-means clustering",
            icon="🎯"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Reshape image for k-means
        pixels = image.reshape((-1, 3))
        pixels = np.float32(pixels)
        
        # Define criteria and apply k-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        k = self._params['clusters']
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10,
            cv2.KMEANS_RANDOM_CENTERS
        )
        
        # Convert back to uint8
        centers = np.uint8(centers)
        segmented = centers[labels.flatten()]
        
        # Reshape back to image dimensions
        return segmented.reshape(image.shape)

    def default_params(self) -> Dict[str, Any]:
        return {
            'clusters': 5
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'clusters': {
                'type': 'range',
                'min': 2,
                'max': 10,
                'default': 5,
                'description': 'Number of color clusters'
            }
        }

class MeanShiftSegmentationOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Mean Shift Segmentation",
            description="Segment image using mean shift clustering",
            icon="🎯"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to float32
        data = np.float32(image).reshape((-1, 3))
        
        # Define criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        
        # Apply mean shift
        _, labels, centers = cv2.kmeans(
            data,
            self._params['max_clusters'],
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS
        )
        
        # Convert back to uint8
        centers = np.uint8(centers)
        result = centers[labels.flatten()]
        
        # Reshape back to original image shape
        return result.reshape(image.shape) 