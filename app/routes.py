import os
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from PIL import Image
import base64
from io import BytesIO
from .image_processing import ImageProcessor
from .image_processing.operations_config import OPERATIONS_CONFIG, CATEGORY_METADATA
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)
processor = ImageProcessor()

def encode_image_to_base64(image: np.ndarray) -> str:
    """Convert an OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.png', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f'data:image/png;base64,{img_str}'

@bp.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(current_app.static_folder, 'index.html')

@bp.route('/api/operations', methods=['GET'])
def get_operations():
    """Return the list of available image processing operations."""
    logger.info('Fetching operations...')
    logger.info(f'Operations: {len(OPERATIONS_CONFIG)} available')
    logger.info(f'Categories: {list(CATEGORY_METADATA.keys())}')
    
    response = {
        'operations': OPERATIONS_CONFIG,
        'categories': CATEGORY_METADATA
    }
    
    logger.info('Sending operations response')
    return jsonify(response)

@bp.route('/api/process', methods=['POST'])
def process_image():
    """Process an image with the specified pipeline of operations."""
    try:
        # Validate input
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'}), 400
        
        # Parse request data
        try:
            pipeline_data = json.loads(request.form.get('pipeline', '[]'))
            preview_steps = json.loads(request.form.get('preview_steps', '[]'))
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return jsonify({'success': False, 'error': 'Invalid pipeline data format'}), 400
        
        # Read and decode image
        try:
            image_data = file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'success': False, 'error': 'Invalid image format'}), 400
        except Exception as e:
            logger.error(f"Image decoding error: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to decode image'}), 400
        
        # Process image and collect intermediate results
        result = image.copy()
        intermediate_results = {}
        
        try:
            # Initialize total processing time
            total_processing_time = 0
            
            for i, step in enumerate(pipeline_data):
                # Validate operation
                operation_id = step['id']
                if operation_id not in processor._operations:
                    logger.warning(f"Skipping unknown operation: {operation_id}")
                    continue
                
                # Get operation parameters
                params = step.get('params', {})
                
                # Get or create operation instance
                if operation_id not in processor._instances:
                    processor._instances[operation_id] = processor._operations[operation_id]()
                
                # Apply operation and measure time
                operation = processor._instances[operation_id]
                operation.set_params(params)
                
                start_time = time.perf_counter()
                result = operation.process(result)
                end_time = time.perf_counter()
                
                # Add to total processing time
                total_processing_time += (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Save intermediate result if requested
                if i in preview_steps:
                    intermediate_results[str(i)] = encode_image_to_base64(result)
            
            # Encode final result
            final_image = encode_image_to_base64(result)
            
            return jsonify({
                'success': True,
                'image': final_image,
                'intermediate_results': intermediate_results,
                'processing_time': round(total_processing_time)  # Round to nearest millisecond
            })
            
        except Exception as e:
            logger.error(f"Error during image processing: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'An error occurred during image processing'
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename) 