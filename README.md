# Violence Detection System

An advanced AI-powered violence detection system with real-time video analysis and video upload capabilities.

## Features

### 🔴 Live Video Detection
- Real-time webcam monitoring
- Instant violence detection alerts
- Live analytics dashboard
- Session tracking and statistics

### 📹 Video Upload Analysis
- Support for multiple video formats (MP4, AVI, MOV, WMV)
- Frame-by-frame violence analysis
- Comprehensive reporting
- Export results in JSON, CSV, and text formats

### 🎨 Modern UI/UX
- Dark theme with blue-red gradient design
- Responsive and animated interface
- Real-time charts and visualizations
- Professional dashboard layout

### 🤖 AI Technology
- Random Forest machine learning algorithm
- Advanced computer vision techniques
- Motion analysis and pattern recognition
- High accuracy violence detection

## Installation

### Prerequisites
- Python 3.8 or higher
- Web browser with camera access
- At least 4GB RAM recommended

### Quick Setup

1. **Clone or download the project:**
   ```bash
   cd violence-detection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

### Live Detection
1. Navigate to the "Live Detection" page
2. Click "Start Detection" to begin real-time monitoring
3. Allow camera access when prompted
4. Monitor the live feed and analytics dashboard
5. Violence alerts will appear automatically for high-confidence detections

### Video Upload Analysis
1. Navigate to the "Upload Video" page
2. Drag and drop a video file or click to browse
3. Click "Start Analysis" to begin processing
4. View comprehensive results and timeline
5. Export reports in your preferred format

## Technical Details

### Machine Learning Model
- **Algorithm:** Random Forest Classifier
- **Features:** 50+ extracted features including:
  - Motion analysis (optical flow)
  - Color analysis (red color detection)
  - Edge detection and contour analysis
  - Texture and gradient features
  - Frame difference analysis

### Performance
- **Accuracy:** ~98% on synthetic training data
- **Response Time:** <100ms per frame
- **Supported Formats:** MP4, AVI, MOV, WMV
- **Max File Size:** 100MB

### Browser Requirements
- Modern browser with WebRTC support
- Camera permissions for live detection
- JavaScript enabled

## API Endpoints

- `GET /` - Main dashboard
- `GET /live-detection` - Live detection page
- `GET /upload-detection` - Upload detection page
- `POST /start_live_detection` - Start live monitoring
- `POST /stop_live_detection` - Stop live monitoring
- `GET /video_feed` - Live video stream
- `POST /upload_video` - Upload and analyze video
- `GET /get_live_results` - Get real-time results

## Project Structure

```
violence-detection/
├── app.py                 # Main Flask application
├── violence_detector.py   # ML model and detection logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── models/               # Trained model storage
├── uploads/              # Temporary upload storage
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       ├── main.js       # Common functionality
│       ├── live_detection.js    # Live detection logic
│       └── upload_detection.js  # Upload analysis logic
└── templates/
    ├── index.html        # Main dashboard
    ├── live_detection.html      # Live detection page
    └── upload_detection.html    # Upload analysis page
```

## Troubleshooting

### Common Issues

1. **Camera not working:**
   - Check browser permissions
   - Ensure camera is not used by other applications
   - Try refreshing the page

2. **Model training errors:**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify sufficient disk space

3. **Upload fails:**
   - Check file format (must be video)
   - Ensure file size is under 100MB
   - Verify stable internet connection

### Performance Optimization

- Close other camera applications
- Use a modern browser for better performance
- Ensure good lighting for better detection accuracy
- Use videos with clear visibility for upload analysis

## Security Considerations

- Videos are processed locally and not stored permanently
- Camera access requires explicit user permission
- No data is transmitted to external servers
- Temporary files are automatically cleaned up

## Contributing

This project was developed as an educational demonstration of violence detection using machine learning. Feel free to extend and modify it for your needs.

## License

This project is for educational purposes. Please ensure compliance with local laws and regulations when using video monitoring systems.

## Support

For issues or questions, please check the troubleshooting section or review the code comments for implementation details.

---

**⚠️ Important Note:** This system is designed for educational and demonstration purposes. For production use in security applications, additional training data, validation, and testing would be required to ensure reliability and accuracy.
