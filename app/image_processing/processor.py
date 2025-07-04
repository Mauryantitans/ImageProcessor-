"""Main module for image processing functionality."""

from typing import List, Dict, Any, Type, Optional
import numpy as np
from .operations.base import ImageOperation
from .operations.color import (
    GrayscaleOperation, BrightnessOperation, ContrastOperation,
    SaturationOperation, HueOperation
)
from .operations.filters import BlurOperation, SharpenOperation
from .operations.effects import SepiaOperation
from .operations.transform import RotateOperation, FlipOperation
from .operations.noise import AddNoiseOperation, DenoiseOperation
from .operations.opencv import (
    CannyEdgeOperation, AdaptiveThresholdOperation, ContourDrawOperation,
    MorphologyOperation, CornerDetectionOperation, ColorSpaceOperation,
    HistogramEqualizationOperation
)
from .operations.opencv_features import (
    SIFTDetectionOperation, ORBDetectionOperation,
    BlobDetectionOperation, GoodFeaturesToTrackOperation
)
from .operations.opencv_segmentation import (
    WatershedSegmentationOperation, GrabCutSegmentationOperation,
    KMeansSegmentationOperation, MeanShiftSegmentationOperation
)
from .operations.opencv_detection import (
    HaarCascadeDetectionOperation, TemplateMatchingOperation,
    BackgroundSubtractionOperation, OpticalFlowOperation
)
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Main class for managing image processing operations.
    
    This class handles the registration, instantiation, and execution of
    image processing operations. It maintains a registry of available
    operations and their instances for efficient reuse.
    """

    def __init__(self):
        """Initialize the ImageProcessor with available operations."""
        # Initialize available operations
        self._operations: Dict[str, Type[ImageOperation]] = {
            # Basic operations
            'brightness': BrightnessOperation,
            'contrast': ContrastOperation,
            'saturation': SaturationOperation,
            'hue': HueOperation,
            'blur': BlurOperation,
            'sharpen': SharpenOperation,
            'grayscale': GrayscaleOperation,
            'sepia': SepiaOperation,
            'rotate': RotateOperation,
            'flip': FlipOperation,
            'add_noise': AddNoiseOperation,
            'denoise': DenoiseOperation,
            
            # OpenCV - Edge & Contour Detection
            'canny_edge': CannyEdgeOperation,
            'adaptive_threshold': AdaptiveThresholdOperation,
            'contour_draw': ContourDrawOperation,
            
            # OpenCV - Morphological Operations
            'morphology': MorphologyOperation,
            
            # OpenCV - Feature Detection
            'corner_detection': CornerDetectionOperation,
            'sift_detection': SIFTDetectionOperation,
            'orb_detection': ORBDetectionOperation,
            'blob_detection': BlobDetectionOperation,
            'good_features': GoodFeaturesToTrackOperation,
            
            # OpenCV - Segmentation
            'watershed': WatershedSegmentationOperation,
            'grabcut': GrabCutSegmentationOperation,
            'kmeans_segment': KMeansSegmentationOperation,
            'meanshift_segment': MeanShiftSegmentationOperation,
            
            # OpenCV - Object Detection
            'haar_cascade': HaarCascadeDetectionOperation,
            'template_matching': TemplateMatchingOperation,
            'background_subtraction': BackgroundSubtractionOperation,
            'optical_flow': OpticalFlowOperation,
            
            # OpenCV - Color & Histogram
            'color_space': ColorSpaceOperation,
            'histogram_eq': HistogramEqualizationOperation
        }
        
        # Initialize operation instances cache
        self._instances: Dict[str, ImageOperation] = {}
        
    def get_available_operations(self) -> List[Dict[str, Any]]:
        """Get list of available operations and their metadata.
        
        Returns:
            List[Dict[str, Any]]: List of operation metadata dictionaries.
        """
        operations = []
        for op_id, op_class in self._operations.items():
            try:
                instance = self._get_operation_instance(op_id)
                operations.append({
                    'id': op_id,
                    **instance.to_dict()
                })
            except Exception as e:
                logger.error(f"Error getting metadata for operation {op_id}: {str(e)}")
        return operations

    def _get_operation_instance(self, operation_id: str) -> ImageOperation:
        """Get or create an operation instance.
        
        Args:
            operation_id (str): The identifier of the operation.
            
        Returns:
            ImageOperation: The operation instance.
            
        Raises:
            ValueError: If the operation_id is unknown.
        """
        if operation_id not in self._instances:
            if operation_id not in self._operations:
                raise ValueError(f"Unknown operation: {operation_id}")
            self._instances[operation_id] = self._operations[operation_id]()
        return self._instances[operation_id]

    def process_pipeline(self, image: np.ndarray, pipeline: List[Dict[str, Any]]) -> np.ndarray:
        """Process image through a pipeline of operations.
        
        Args:
            image (np.ndarray): Input image to process.
            pipeline (List[Dict[str, Any]]): List of operations to apply.
            
        Returns:
            np.ndarray: The processed image.
        """
        result = image.copy()
        
        for step in pipeline:
            operation_id = step['id']
            params = step.get('params', {})
            
            try:
                operation = self._get_operation_instance(operation_id)
                operation.set_params(params)
                result = operation.process(result)
            except ValueError as e:
                logger.warning(f"Skipping invalid operation: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing operation {operation_id}: {str(e)}")
                raise
            
        return result

    def get_operation_params(self, operation_id: str) -> Dict[str, Any]:
        """Get current parameters for an operation.
        
        Args:
            operation_id (str): The identifier of the operation.
            
        Returns:
            Dict[str, Any]: Current parameter values.
        """
        operation = self._get_operation_instance(operation_id)
        return operation.get_params()

    def get_operation_schema(self, operation_id: str) -> Dict[str, Dict[str, Any]]:
        """Get parameter schema for an operation.
        
        Args:
            operation_id (str): The identifier of the operation.
            
        Returns:
            Dict[str, Dict[str, Any]]: Parameter schema definition.
        """
        operation = self._get_operation_instance(operation_id)
        return operation.param_schema()

    def set_operation_params(self, operation_id: str, params: Dict[str, Any]) -> None:
        """Set parameters for an operation.
        
        Args:
            operation_id (str): The identifier of the operation.
            params (Dict[str, Any]): Parameter values to set.
        """
        operation = self._get_operation_instance(operation_id)
        operation.set_params(params) 