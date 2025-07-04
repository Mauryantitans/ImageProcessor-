import cv2
import numpy as np
from typing import Dict, Any
from .base import ImageOperation

class HaarCascadeDetectionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Haar Cascade Detection",
            description="Detect objects using Haar Cascade classifiers",
            icon="👁️"
        )
        
        self._cascades = {
            'face': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
            'eye': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml'),
            'smile': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml'),
            'body': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        }

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Get selected cascade
        cascade = self._cascades[self._params['detector']]
        
        # Detect objects
        objects = cascade.detectMultiScale(
            gray,
            scaleFactor=self._params['scale_factor'],
            minNeighbors=self._params['min_neighbors'],
            minSize=(30, 30)
        )
        
        # Draw rectangles around detected objects
        result = image.copy()
        for (x, y, w, h) in objects:
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'detector': 'face',
            'scale_factor': 1.1,
            'min_neighbors': 5
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'detector': {
                'type': 'select',
                'options': ['face', 'eye', 'smile', 'body'],
                'default': 'face'
            },
            'scale_factor': {
                'type': 'range',
                'min': 1.1,
                'max': 2.0,
                'step': 0.1,
                'default': 1.1
            },
            'min_neighbors': {
                'type': 'range',
                'min': 1,
                'max': 10,
                'default': 5
            }
        }

class TemplateMatchingOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Template Matching",
            description="Find template pattern in image",
            icon="🔍"
        )

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert both images to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(self._params['template_path'], 0)
        
        if template is None:
            raise ValueError("Template image not found")
            
        w, h = template.shape[::-1]
        
        # Apply template matching
        method = eval(f'cv2.TM_CCOEFF_NORMED')
        res = cv2.matchTemplate(gray, template, method)
        
        # Get best match locations
        threshold = self._params['threshold']
        loc = np.where(res >= threshold)
        
        # Draw rectangles around matches
        result = image.copy()
        for pt in zip(*loc[::-1]):
            cv2.rectangle(result, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'template_path': '',
            'threshold': 0.8
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'template_path': {
                'type': 'file',
                'description': 'Path to template image'
            },
            'threshold': {
                'type': 'range',
                'min': 0.1,
                'max': 1.0,
                'step': 0.1,
                'default': 0.8,
                'description': 'Matching threshold'
            }
        }

class BackgroundSubtractionOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Background Subtraction",
            description="Detect moving objects using background subtraction",
            icon="🎬"
        )
        
        self._subtractors = {
            'mog2': cv2.createBackgroundSubtractorMOG2(),
            'knn': cv2.createBackgroundSubtractorKNN()
        }

    def process(self, image: np.ndarray) -> np.ndarray:
        # Get selected subtractor
        subtractor = self._subtractors[self._params['method']]
        
        # Apply background subtraction
        fgmask = subtractor.apply(image)
        
        # Apply threshold to get binary mask
        _, mask = cv2.threshold(
            fgmask,
            self._params['threshold'],
            255,
            cv2.THRESH_BINARY
        )
        
        # Apply morphological operations to remove noise
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Draw bounding boxes around moving objects
        result = image.copy()
        for contour in contours:
            if cv2.contourArea(contour) > self._params['min_area']:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'method': 'mog2',
            'threshold': 127,
            'min_area': 500
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'method': {
                'type': 'select',
                'options': ['mog2', 'knn'],
                'default': 'mog2'
            },
            'threshold': {
                'type': 'range',
                'min': 0,
                'max': 255,
                'default': 127
            },
            'min_area': {
                'type': 'range',
                'min': 100,
                'max': 5000,
                'default': 500
            }
        }

class OpticalFlowOperation(ImageOperation):
    def __init__(self):
        super().__init__(
            name="Optical Flow",
            description="Track motion using optical flow",
            icon="➡️"
        )
        
        self._prev_gray = None
        self._prev_points = None

    def process(self, image: np.ndarray) -> np.ndarray:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if self._prev_gray is None:
            self._prev_gray = gray
            # Find initial points to track
            self._prev_points = cv2.goodFeaturesToTrack(
                gray,
                maxCorners=self._params['max_corners'],
                qualityLevel=0.01,
                minDistance=10
            )
            return image
            
        if self._prev_points is None:
            return image
            
        # Calculate optical flow
        new_points, status, _ = cv2.calcOpticalFlowPyrLK(
            self._prev_gray,
            gray,
            self._prev_points,
            None
        )
        
        # Select good points
        good_new = new_points[status == 1]
        good_old = self._prev_points[status == 1]
        
        # Draw the tracks
        result = image.copy()
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            cv2.line(result, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
            cv2.circle(result, (int(a), int(b)), 3, (0, 0, 255), -1)
            
        # Update previous points and frame
        self._prev_gray = gray
        self._prev_points = good_new.reshape(-1, 1, 2)
        
        return result

    def default_params(self) -> Dict[str, Any]:
        return {
            'max_corners': 100
        }

    def param_schema(self) -> Dict[str, Dict[str, Any]]:
        return {
            'max_corners': {
                'type': 'range',
                'min': 10,
                'max': 500,
                'default': 100,
                'description': 'Maximum number of corners to track'
            }
        } 