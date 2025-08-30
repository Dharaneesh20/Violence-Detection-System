from flask import Flask, request, jsonify, render_template, Response
import cv2
import numpy as np
import os
import io
import base64
from PIL import Image
import threading
import time
from violence_detector import ViolenceDetector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize violence detector
detector = ViolenceDetector()

# Global variables for live video
camera = None
live_detection_active = False
live_detection_results = []

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
    def __del__(self):
        self.video.release()
        
    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
        return image
    
    def get_frame_with_detection(self):
        frame = self.get_frame()
        if frame is None:
            return None
            
        # Perform violence detection
        is_violent, confidence = detector.detect_violence(frame)
        
        # Draw detection results on frame
        color = (0, 0, 255) if is_violent else (0, 255, 0)
        status = "VIOLENCE DETECTED!" if is_violent else "Safe"
        
        cv2.putText(frame, f"Status: {status}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), is_violent, confidence

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live-detection')
def live_detection():
    return render_template('live_detection.html')

@app.route('/upload-detection')
def upload_detection():
    return render_template('upload_detection.html')

def generate_frames():
    global camera, live_detection_active, live_detection_results
    
    if camera is None:
        camera = VideoCamera()
    
    while live_detection_active:
        try:
            result = camera.get_frame_with_detection()
            if result is None:
                break
                
            frame_bytes, is_violent, confidence = result
            
            # Store detection result
            live_detection_results.append({
                'timestamp': time.time(),
                'is_violent': is_violent,
                'confidence': confidence
            })
            
            # Keep only last 100 results
            if len(live_detection_results) > 100:
                live_detection_results = live_detection_results[-100:]
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in frame generation: {e}")
            break

@app.route('/video_feed')
def video_feed():
    global live_detection_active
    live_detection_active = True
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_live_detection', methods=['POST'])
def start_live_detection():
    global live_detection_active, live_detection_results
    live_detection_active = True
    live_detection_results = []
    return jsonify({'status': 'started'})

@app.route('/stop_live_detection', methods=['POST'])
def stop_live_detection():
    global live_detection_active, camera
    live_detection_active = False
    if camera:
        del camera
        camera = None
    return jsonify({'status': 'stopped'})

@app.route('/get_live_results')
def get_live_results():
    global live_detection_results
    return jsonify({
        'results': live_detection_results[-10:],  # Last 10 results
        'total_detections': len([r for r in live_detection_results if r['is_violent']])
    })

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = f"video_{int(time.time())}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process video for violence detection
        results = detector.detect_violence_in_video(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect violence
        is_violent, confidence = detector.detect_violence(frame)
        
        return jsonify({
            'is_violent': is_violent,
            'confidence': confidence,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, threaded=True)
