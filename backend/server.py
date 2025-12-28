from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import re
import time
import mimetypes
from pathlib import Path
from detect import ThreatDetector
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for Electron app

# Configure upload folder
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize detector with correct path to model file
model_path = Path(__file__).parent.parent / 'yolo11s.pt'
detector = ThreatDetector(str(model_path))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in {'mp4', 'avi', 'mov'}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.route('/api/detect', methods=['POST'])
def detect():
    """
    Main detection endpoint
    Accepts image or video file and returns detections
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check if video or image
        if is_video(filename):
            # Get processing speed settings from request
            speed_mode = request.form.get('speed_mode', 'fast')  # fast, normal, high_quality
            
            # Configure processing parameters based on speed mode
            if speed_mode == 'fast':
                skip_frames = 3  # Skip 3 frames, process every 4th
                max_size = 480   # Smaller resolution for faster processing
            elif speed_mode == 'normal':
                skip_frames = 1  # Skip 1 frame, process every 2nd
                max_size = 640   # Medium resolution
            else:  # high_quality
                skip_frames = 0  # Process all frames
                max_size = 1080  # Full resolution
            
            # Process video and create output file
            output_filename = f'processed_{filename}'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Use the optimized processing method
            total_detections = detector.create_processed_video_fast(
                filepath, output_path, skip_frames=skip_frames, max_size=max_size
            )
            
            response = {
                'type': 'video',
                'filename': filename,
                'output_video': output_filename,
                'total_detections': total_detections,
                'video_url': f'/api/video/{output_filename}',
                'speed_mode': speed_mode,
                'processing_info': {
                    'skip_frames': skip_frames,
                    'max_resolution': max_size,
                    'optimization': 'enabled'
                }
            }
            
            # Clean up input file
            os.remove(filepath)
            
            return jsonify(response), 200
        else:
            # Process image
            result = detector.detect_image(filepath)
            result['type'] = 'image'
            result['filename'] = filename
            
            # Clean up
            os.remove(filepath)
            
            return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect/video-stream', methods=['POST'])
def detect_video_stream():
    """
    Process video and stream results frame by frame
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename) or not is_video(file.filename):
        return jsonify({'error': 'Invalid video file'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        def generate():
            for frame_result in detector.detect_video(filepath):
                yield f"data: {jsonify(frame_result).get_data(as_text=True)}\n\n"
            
            # Clean up
            os.remove(filepath)
        
        from flask import Response
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    # Convert class names dict to list
    class_names = list(detector.class_names.values()) if isinstance(detector.class_names, dict) else detector.class_names
    
    return jsonify({
        'model_name': 'YOLOv11',
        'classes': class_names,
        'status': 'loaded'
    }), 200

@app.route('/api/download/image', methods=['POST'])
def download_image():
    """
    Save and serve detection result image
    """
    try:
        data = request.get_json()
        
        if not data or 'image_data' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        import base64
        import tempfile
        
        # Decode base64 image
        image_data = data['image_data']
        filename = data.get('filename', f"detection_result_{int(time.time())}.jpg")
        
        # Ensure filename has proper extension
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename = f"{filename}.jpg"
        
        # Create output path
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"saved_{filename}")
        
        # Decode and save image
        image_bytes = base64.b64decode(image_data)
        with open(output_path, 'wb') as f:
            f.write(image_bytes)
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='image/jpeg'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<filename>')
def serve_video(filename):
    """Serve processed video files with proper headers for web playback"""
    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Ensure proper MIME type
        mimetype = 'video/mp4'
        
        def generate():
            with open(video_path, 'rb') as video:
                data = video.read(1024)  # Read in chunks
                while data:
                    yield data
                    data = video.read(1024)
        
        response = Response(generate(), mimetype=mimetype)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = str(os.path.getsize(video_path))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
        
    except Exception as e:
        print(f"Video serving error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Aerial Threat Detection Server...")
    print("Model loaded successfully!")
    app.run(host='127.0.0.1', port=5000, debug=True)