"""Configuration for image processing operations."""

OPERATIONS_CONFIG = [
    # Basic Adjustments
    {
        'id': 'brightness',
        'name': 'Brightness',
        'description': 'Adjust image brightness',
        'icon': '☀️',
        'category': 'basic',
        'params': {'value': {'type': 'range', 'min': -100, 'max': 100, 'default': 0}}
    },
    {
        'id': 'contrast',
        'name': 'Contrast',
        'description': 'Adjust image contrast',
        'icon': '◐',
        'category': 'basic',
        'params': {'value': {'type': 'range', 'min': -100, 'max': 100, 'default': 0}}
    },
    
    # Color Operations
    {
        'id': 'saturation',
        'name': 'Saturation',
        'description': 'Adjust color saturation',
        'icon': '🎨',
        'category': 'color',
        'params': {'value': {'type': 'range', 'min': -100, 'max': 100, 'default': 0}}
    },
    {
        'id': 'hue',
        'name': 'Hue Rotation',
        'description': 'Rotate image hue',
        'icon': '🌈',
        'category': 'color',
        'params': {'value': {'type': 'range', 'min': 0, 'max': 360, 'default': 0}}
    },
    
    # Filters
    {
        'id': 'blur',
        'name': 'Gaussian Blur',
        'description': 'Apply gaussian blur effect',
        'icon': '🌫️',
        'category': 'filters',
        'params': {'radius': {'type': 'range', 'min': 0, 'max': 50, 'default': 5}}
    },
    {
        'id': 'sharpen',
        'name': 'Sharpen',
        'description': 'Enhance image sharpness',
        'icon': '✨',
        'category': 'filters',
        'params': {'amount': {'type': 'range', 'min': 0, 'max': 100, 'default': 50}}
    },
    
    # Effects
    {
        'id': 'grayscale',
        'name': 'Grayscale',
        'description': 'Convert to black and white',
        'icon': '⚫',
        'category': 'effects',
        'params': {}
    },
    {
        'id': 'sepia',
        'name': 'Sepia',
        'description': 'Apply vintage sepia effect',
        'icon': '🌅',
        'category': 'effects',
        'params': {'intensity': {'type': 'range', 'min': 0, 'max': 100, 'default': 100}}
    },
    
    # Transform
    {
        'id': 'rotate',
        'name': 'Rotate',
        'description': 'Rotate image by degrees',
        'icon': '🔄',
        'category': 'transform',
        'params': {'angle': {'type': 'range', 'min': -180, 'max': 180, 'default': 0}}
    },
    {
        'id': 'flip',
        'name': 'Flip',
        'description': 'Flip image horizontally or vertically',
        'icon': '↔️',
        'category': 'transform',
        'params': {'direction': {'type': 'select', 'options': ['horizontal', 'vertical']}}
    },
    
    # Noise
    {
        'id': 'add_noise',
        'name': 'Add Noise',
        'description': 'Add random noise to the image',
        'icon': '🎲',
        'category': 'noise',
        'params': {
            'amount': {'type': 'range', 'min': 0, 'max': 100, 'default': 25},
            'type': {'type': 'select', 'options': ['gaussian', 'uniform', 'salt_and_pepper']}
        }
    },
    {
        'id': 'denoise',
        'name': 'Denoise',
        'description': 'Remove noise from the image',
        'icon': '✨',
        'category': 'noise',
        'params': {
            'strength': {'type': 'range', 'min': 1, 'max': 50, 'default': 10},
            'method': {'type': 'select', 'options': ['gaussian', 'median', 'non_local_means']}
        }
    },
    
    # OpenCV Operations - Edge Detection
    {
        'id': 'canny_edge',
        'name': 'Canny Edge',
        'description': 'Detect edges using Canny algorithm',
        'icon': '🔲',
        'category': 'opencv',
        'subcategory': 'edge_detection',
        'params': {
            'threshold1': {'type': 'range', 'min': 0, 'max': 255, 'default': 100},
            'threshold2': {'type': 'range', 'min': 0, 'max': 255, 'default': 200}
        }
    },
    {
        'id': 'adaptive_threshold',
        'name': 'Adaptive Threshold',
        'description': 'Apply adaptive thresholding',
        'icon': '⬜',
        'category': 'opencv',
        'subcategory': 'edge_detection',
        'params': {
            'block_size': {'type': 'range', 'min': 3, 'max': 99, 'step': 2, 'default': 11},
            'c': {'type': 'range', 'min': -10, 'max': 10, 'default': 2},
            'method': {'type': 'select', 'options': ['gaussian', 'mean'], 'default': 'gaussian'},
            'threshold_type': {'type': 'select', 'options': ['binary', 'binary_inv'], 'default': 'binary'}
        }
    },
    {
        'id': 'contour_draw',
        'name': 'Draw Contours',
        'description': 'Find and draw contours in the image',
        'icon': '📏',
        'category': 'opencv',
        'subcategory': 'edge_detection',
        'params': {
            'threshold': {'type': 'range', 'min': 0, 'max': 255, 'default': 127},
            'thickness': {'type': 'range', 'min': 1, 'max': 10, 'default': 2}
        }
    },
    
    # OpenCV Operations - Morphology
    {
        'id': 'morphology',
        'name': 'Morphological Ops',
        'description': 'Apply morphological operations (erosion, dilation, etc.)',
        'icon': '🔄',
        'category': 'opencv',
        'subcategory': 'morphological',
        'params': {
            'operation': {'type': 'select', 'options': ['erode', 'dilate', 'open', 'close', 'gradient'], 'default': 'dilate'},
            'kernel_size': {'type': 'range', 'min': 1, 'max': 15, 'step': 2, 'default': 3},
            'iterations': {'type': 'range', 'min': 1, 'max': 10, 'default': 1}
        }
    },
    
    # OpenCV Operations - Feature Detection
    {
        'id': 'corner_detection',
        'name': 'Corner Detection',
        'description': 'Detect corners using Harris or FAST algorithm',
        'icon': '📍',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'method': {'type': 'select', 'options': ['harris', 'fast'], 'default': 'harris'},
            'threshold': {'type': 'range', 'min': 1, 'max': 50, 'default': 10},
            'k': {'type': 'range', 'min': 1, 'max': 20, 'default': 5}
        }
    },
    {
        'id': 'sift_detection',
        'name': 'SIFT',
        'description': 'Detect SIFT keypoints and descriptors',
        'icon': '🔍',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'max_features': {'type': 'range', 'min': 10, 'max': 1000, 'default': 100},
            'contrast_threshold': {'type': 'range', 'min': 1, 'max': 50, 'default': 10},
            'edge_threshold': {'type': 'range', 'min': 1, 'max': 50, 'default': 10}
        }
    },
    {
        'id': 'orb_detection',
        'name': 'ORB',
        'description': 'Detect ORB keypoints (faster alternative to SIFT)',
        'icon': '🎯',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'max_features': {'type': 'range', 'min': 100, 'max': 2000, 'default': 500},
            'scale_levels': {'type': 'range', 'min': 3, 'max': 15, 'default': 8}
        }
    },
    {
        'id': 'blob_detection',
        'name': 'Blob Detection',
        'description': 'Detect blobs using SimpleBlobDetector',
        'icon': '⭕',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'min_area': {'type': 'range', 'min': 10, 'max': 1000, 'default': 100},
            'max_area': {'type': 'range', 'min': 1000, 'max': 10000, 'default': 5000},
            'filter_circularity': {'type': 'select', 'options': [True, False], 'default': True},
            'min_circularity': {'type': 'range', 'min': 10, 'max': 100, 'default': 80}
        }
    },
    {
        'id': 'good_features',
        'name': 'Good Features',
        'description': 'Detect good features to track using Shi-Tomasi method',
        'icon': '📌',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'max_corners': {'type': 'range', 'min': 10, 'max': 200, 'default': 50},
            'quality_level': {'type': 'range', 'min': 1, 'max': 99, 'default': 1},
            'min_distance': {'type': 'range', 'min': 5, 'max': 50, 'default': 10}
        }
    },
    
    # OpenCV Operations - Segmentation
    {
        'id': 'watershed',
        'name': 'Watershed',
        'description': 'Segment image using watershed algorithm',
        'icon': '💧',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'foreground_threshold': {'type': 'range', 'min': 1, 'max': 90, 'default': 20}
        }
    },
    {
        'id': 'grabcut',
        'name': 'GrabCut',
        'description': 'Segment image using GrabCut algorithm',
        'icon': '✂️',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'margin': {'type': 'range', 'min': 5, 'max': 100, 'default': 10},
            'iterations': {'type': 'range', 'min': 1, 'max': 10, 'default': 5}
        }
    },
    {
        'id': 'kmeans_segment',
        'name': 'K-Means',
        'description': 'Segment image using K-means clustering',
        'icon': '🎯',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'clusters': {'type': 'range', 'min': 2, 'max': 10, 'default': 5}
        }
    },
    {
        'id': 'meanshift_segment',
        'name': 'Mean Shift',
        'description': 'Segment image using mean shift clustering',
        'icon': '🎯',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'max_clusters': {'type': 'range', 'min': 2, 'max': 20, 'default': 8}
        }
    },
    
    # OpenCV Operations - Object Detection
    {
        'id': 'haar_cascade',
        'name': 'Haar Cascade',
        'description': 'Detect objects using Haar Cascade classifiers',
        'icon': '👁️',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'detector': {'type': 'select', 'options': ['face', 'eye', 'smile', 'body'], 'default': 'face'},
            'scale_factor': {'type': 'range', 'min': 1.1, 'max': 2.0, 'step': 0.1, 'default': 1.1},
            'min_neighbors': {'type': 'range', 'min': 1, 'max': 10, 'default': 5}
        }
    },
    {
        'id': 'template_matching',
        'name': 'Template Match',
        'description': 'Find template pattern in image',
        'icon': '🔍',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'template_path': {'type': 'file', 'description': 'Path to template image'},
            'threshold': {'type': 'range', 'min': 0.1, 'max': 1.0, 'step': 0.1, 'default': 0.8}
        }
    },
    {
        'id': 'background_subtraction',
        'name': 'Background Subtraction',
        'description': 'Detect moving objects using background subtraction',
        'icon': '🎬',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'method': {'type': 'select', 'options': ['mog2', 'knn'], 'default': 'mog2'},
            'threshold': {'type': 'range', 'min': 0, 'max': 255, 'default': 127},
            'min_area': {'type': 'range', 'min': 100, 'max': 5000, 'default': 500}
        }
    },
    {
        'id': 'optical_flow',
        'name': 'Optical Flow',
        'description': 'Track motion using optical flow',
        'icon': '➡️',
        'category': 'opencv',
        'subcategory': 'object_detection',
        'params': {
            'max_corners': {'type': 'range', 'min': 10, 'max': 500, 'default': 100}
        }
    },
    
    # OpenCV Operations - Color & Histogram
    {
        'id': 'color_space',
        'name': 'Color Space Convert',
        'description': 'Convert image between different color spaces',
        'icon': '🎨',
        'category': 'opencv',
        'subcategory': 'color',
        'params': {
            'space': {'type': 'select', 'options': ['gray', 'hsv', 'lab', 'yuv', 'luv'], 'default': 'hsv'}
        }
    },
    {
        'id': 'histogram_eq',
        'name': 'Histogram Equalization',
        'description': 'Enhance image contrast using histogram equalization',
        'icon': '📊',
        'category': 'opencv',
        'subcategory': 'color',
        'params': {
            'method': {'type': 'select', 'options': ['global', 'clahe'], 'default': 'clahe'},
            'clip_limit': {'type': 'range', 'min': 1, 'max': 10, 'default': 2}
        }
    }
]

# Category metadata
CATEGORY_METADATA = {
    'basic': {
        'name': 'Basic Operations',
        'icon': '⚙️'
    },
    'color': {
        'name': 'Color Operations',
        'icon': '🎨'
    },
    'filters': {
        'name': 'Filters',
        'icon': '🔍'
    },
    'effects': {
        'name': 'Effects',
        'icon': '✨'
    },
    'transform': {
        'name': 'Transform',
        'icon': '🔄'
    },
    'noise': {
        'name': 'Noise',
        'icon': '🎲'
    },
    'opencv': {
        'name': 'OpenCV',
        'icon': '🔬',
        'subcategories': {
            'edge_detection': {'name': 'Edge Detection', 'icon': '📏'},
            'morphological': {'name': 'Morphological', 'icon': '🔄'},
            'object_detection': {'name': 'Object Detection', 'icon': '🎯'},
            'color': {'name': 'Color Processing', 'icon': '🎨'}
        }
    }
} 