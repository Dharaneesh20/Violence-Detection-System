import cv2
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

class ViolenceDetector:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.frame_buffer = []
        self.buffer_size = 10
        self.model_path = 'models/violence_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        
        # Initialize or load model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the violence detection model"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            # Load existing model
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Loaded existing violence detection model")
        else:
            # Train a new model with synthetic data
            self._train_model()
    
    def _extract_features(self, frame):
        """Extract features from a video frame"""
        try:
            if frame is None:
                return np.zeros(50)  # Return zero features if frame is None
                
            features = []
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Motion features (using frame difference instead of optical flow)
            if len(self.frame_buffer) > 0:
                prev_gray = cv2.cvtColor(self.frame_buffer[-1], cv2.COLOR_BGR2GRAY)
                
                # Use frame difference for motion detection (more reliable)
                frame_diff = cv2.absdiff(prev_gray, gray)
                motion_magnitude = np.mean(frame_diff)
                motion_std = np.std(frame_diff)
                
                # Additional motion using contour analysis
                _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                motion_contours = len(contours)
            else:
                motion_magnitude = 0
                motion_std = 0
                motion_contours = 0
            
            features.extend([motion_magnitude, motion_std, motion_contours])
        
            # 2. Edge features
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # 3. Color features
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Red color detection (often associated with violence/blood)
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            red_ratio = np.sum(red_mask) / (frame.shape[0] * frame.shape[1])
            features.append(red_ratio)
            
            # 4. Intensity features
            intensity_mean = np.mean(gray)
            intensity_std = np.std(gray)
            features.extend([intensity_mean, intensity_std])
            
            # 5. Gradient features
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            grad_mean = np.mean(gradient_magnitude)
            grad_std = np.std(gradient_magnitude)
            features.extend([grad_mean, grad_std])
            
            # 6. Texture features (using Local Binary Pattern approximation)
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture = cv2.filter2D(gray, -1, kernel)
            texture_mean = np.mean(texture)
            texture_std = np.std(texture)
            features.extend([texture_mean, texture_std])
            
            # 7. Contour features
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            num_contours = len(contours)
            if contours:
                areas = [cv2.contourArea(c) for c in contours]
                max_area = max(areas) if areas else 0
                mean_area = np.mean(areas) if areas else 0
            else:
                max_area = 0
                mean_area = 0
            
            features.extend([num_contours, max_area, mean_area])
            
            # 8. Additional motion features
            if len(self.frame_buffer) > 0:
                # Frame difference
                diff = cv2.absdiff(gray, cv2.cvtColor(self.frame_buffer[-1], cv2.COLOR_BGR2GRAY))
                diff_mean = np.mean(diff)
                diff_std = np.std(diff)
                diff_max = np.max(diff)
            else:
                diff_mean = diff_std = diff_max = 0
            
            features.extend([diff_mean, diff_std, diff_max])
            
            # 9. Histogram features
            hist = cv2.calcHist([gray], [0], None, [16], [0, 256])
            hist_features = hist.flatten() / np.sum(hist)  # Normalize
            features.extend(hist_features[:16])  # Use first 16 bins
            
            # 10. Additional color variance features
            b, g, r = cv2.split(frame)
            color_vars = [np.var(b), np.var(g), np.var(r)]
            features.extend(color_vars)
            
            # Ensure we have exactly 50 features
            while len(features) < 50:
                features.append(0)
            
            return np.array(features[:50])
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return np.zeros(50)  # Return zero features if extraction fails
    
    def _generate_training_data(self):
        """Generate improved synthetic training data for violence detection"""
        print("Generating improved synthetic training data...")
        
        # Generate features for violent scenarios
        violent_features = []
        for _ in range(1000):
            # Create more realistic violent patterns
            features = np.zeros(50)
            
            # Motion features (0-2): High motion for violence
            features[0] = np.random.normal(15, 5)  # High motion magnitude
            features[1] = np.random.normal(8, 3)   # High motion std
            features[2] = np.random.normal(5, 2)   # Motion contours
            
            # Edge density (3): Sharp edges in fights
            features[3] = np.random.normal(0.2, 0.05)
            
            # Color features (4): More red/aggressive colors
            features[4] = np.random.normal(0.25, 0.1)
            
            # Intensity features (5-6): Variable lighting
            features[5] = np.random.normal(120, 30)  # Intensity mean
            features[6] = np.random.normal(50, 15)   # High intensity std
            
            # Gradient features (7-8): Sharp changes
            features[7] = np.random.normal(40, 10)   # High gradient mean
            features[8] = np.random.normal(30, 8)    # High gradient std
            
            # Texture features (9-10): Rough textures
            features[9] = np.random.normal(25, 8)
            features[10] = np.random.normal(20, 6)
            
            # Contour features (11-13): Many objects/people
            features[11] = np.random.normal(80, 20)  # Many contours
            features[12] = np.random.normal(500, 200) # Large areas
            features[13] = np.random.normal(100, 50)  # Mean area
            
            # Motion difference features (14-16): High frame changes
            features[14] = np.random.normal(30, 10)
            features[15] = np.random.normal(25, 8)
            features[16] = np.random.normal(150, 50)
            
            # Histogram features (17-32): More varied
            for i in range(17, 33):
                features[i] = np.random.normal(0.06, 0.02)
            
            # Color variance (33-35): High color variation
            features[33] = np.random.normal(800, 200)
            features[34] = np.random.normal(900, 250)
            features[35] = np.random.normal(700, 180)
            
            # Fill remaining features with correlated noise
            for i in range(36, 50):
                features[i] = np.random.normal(10, 3)
            
            # Ensure no negative values
            features = np.abs(features)
            violent_features.append(features)
        
        # Generate features for non-violent scenarios
        non_violent_features = []
        for _ in range(1000):
            features = np.zeros(50)
            
            # Motion features: Low motion for normal scenes
            features[0] = np.random.normal(2, 1)    # Low motion magnitude
            features[1] = np.random.normal(1.5, 0.5) # Low motion std
            features[2] = np.random.normal(1, 0.5)   # Few motion contours
            
            # Edge density: Smoother edges
            features[3] = np.random.normal(0.05, 0.02)
            
            # Color features: Less red/more neutral
            features[4] = np.random.normal(0.05, 0.03)
            
            # Intensity features: Stable lighting
            features[5] = np.random.normal(110, 15)  # Intensity mean
            features[6] = np.random.normal(20, 5)    # Low intensity std
            
            # Gradient features: Gentle changes
            features[7] = np.random.normal(15, 5)    # Low gradient mean
            features[8] = np.random.normal(10, 3)    # Low gradient std
            
            # Texture features: Smooth textures
            features[9] = np.random.normal(8, 3)
            features[10] = np.random.normal(6, 2)
            
            # Contour features: Fewer objects
            features[11] = np.random.normal(20, 8)   # Fewer contours
            features[12] = np.random.normal(200, 80) # Smaller areas
            features[13] = np.random.normal(40, 15)  # Smaller mean area
            
            # Motion difference: Low frame changes
            features[14] = np.random.normal(5, 2)
            features[15] = np.random.normal(4, 1.5)
            features[16] = np.random.normal(30, 10)
            
            # Histogram features: More uniform
            for i in range(17, 33):
                features[i] = np.random.normal(0.062, 0.01)
            
            # Color variance: Low color variation
            features[33] = np.random.normal(300, 100)
            features[34] = np.random.normal(350, 120)
            features[35] = np.random.normal(280, 90)
            
            # Fill remaining features
            for i in range(36, 50):
                features[i] = np.random.normal(3, 1)
            
            # Ensure no negative values
            features = np.abs(features)
            non_violent_features.append(features)
        
        # Combine data
        X = np.vstack([violent_features, non_violent_features])
        y = np.hstack([np.ones(len(violent_features)), np.zeros(len(non_violent_features))])
        
        return X, y
    
    def _load_real_dataset(self, dataset_path):
        """Load real video dataset from Kaggle or other sources"""
        print("Loading real video dataset...")
        
        violent_features = []
        non_violent_features = []
        
        # Common dataset structures
        violent_dirs = ['violence', 'violent', 'fight', 'Violence', 'Violent', 'Fight']
        non_violent_dirs = ['non-violence', 'non-violent', 'normal', 'NonViolence', 'Non-Violent', 'Normal']
        
        # Check which directories exist
        violent_path = None
        non_violent_path = None
        
        for dir_name in violent_dirs:
            path = os.path.join(dataset_path, dir_name)
            if os.path.exists(path):
                violent_path = path
                break
        
        for dir_name in non_violent_dirs:
            path = os.path.join(dataset_path, dir_name)
            if os.path.exists(path):
                non_violent_path = path
                break
        
        if not violent_path or not non_violent_path:
            print("Dataset structure not recognized. Expected folders like 'violence'/'non-violence'")
            print(f"Available folders: {os.listdir(dataset_path)}")
            return None, None
        
        # Process violent videos
        print(f"Processing violent videos from: {violent_path}")
        violent_files = self._get_video_files_recursive(violent_path)
        
        for i, video_path in enumerate(violent_files[:50]):  # Limit to first 50 videos for speed
            video_file = os.path.basename(video_path)
            print(f"Processing violent video {i+1}/{min(50, len(violent_files))}: {video_file}")
            
            features = self._extract_video_features(video_path)
            if features is not None:
                violent_features.extend(features)
        
        # Process non-violent videos
        print(f"Processing non-violent videos from: {non_violent_path}")
        non_violent_files = self._get_video_files_recursive(non_violent_path)
        
        for i, video_path in enumerate(non_violent_files[:50]):  # Limit to first 50 videos for speed
            video_file = os.path.basename(video_path)
            print(f"Processing non-violent video {i+1}/{min(50, len(non_violent_files))}: {video_file}")
            
            features = self._extract_video_features(video_path)
            if features is not None:
                non_violent_features.extend(features)
        
        if not violent_features or not non_violent_features:
            print("Failed to extract features from videos. Using synthetic data as fallback.")
            return None, None
        
        # Combine data
        X = np.vstack([violent_features, non_violent_features])
        y = np.hstack([np.ones(len(violent_features)), np.zeros(len(non_violent_features))])
        
        print(f"Loaded {len(violent_features)} violent samples and {len(non_violent_features)} non-violent samples")
        return X, y
    
    def _get_video_files_recursive(self, directory):
        """Recursively find all video files in directory and subdirectories"""
        video_files = []
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(video_extensions):
                    video_files.append(os.path.join(root, file))
        
        return video_files
    
    def _extract_video_features(self, video_path):
        """Extract features from an entire video file"""
        try:
            print(f"  Attempting to open: {video_path}")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"  ❌ Failed to open video: {video_path}")
                return None
            
            # Get video info
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"  📹 Video info: {total_frames} frames, {fps:.1f} FPS")
            
            features_list = []
            frame_count = 0
            processed_frames = 0
            
            # Extract features from multiple frames (every 30th frame)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 30 == 0:  # Sample every 30th frame
                    if frame is not None:
                        # Clear frame buffer for each new video
                        if frame_count == 0:
                            self.frame_buffer = []
                            
                        features = self._extract_features(frame)
                        if features is not None and len(features) == 50:
                            features_list.append(features)
                            processed_frames += 1
                            print(f"    ✓ Extracted features from frame {frame_count}")
                        else:
                            print(f"    ❌ Failed to extract features from frame {frame_count}")
                
                frame_count += 1
                
                # Limit to 10 frames per video for speed
                if processed_frames >= 10:
                    break
            
            cap.release()
            
            if features_list:
                print(f"  ✅ Successfully extracted {len(features_list)} feature sets")
                return np.array(features_list)
            else:
                print(f"  ❌ No features extracted from video")
                return None
                
        except Exception as e:
            print(f"  ❌ Error processing video {video_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def train_with_dataset(self, dataset_path):
        """Train model using real dataset instead of synthetic data"""
        print("Training with real dataset...")
        
        # Try to load real dataset
        X, y = self._load_real_dataset(dataset_path)
        
        # Fallback to synthetic data if real dataset fails
        if X is None or y is None:
            print("Falling back to synthetic training data...")
            X, y = self._generate_training_data()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=200,  # More trees for real data
            max_depth=15,      # Deeper trees for complex patterns
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_scaled, y)
        
        # Save model and scaler
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print("Model trained and saved successfully!")
        print(f"Training accuracy: {self.model.score(X_scaled, y):.3f}")
        return True
    
    def _train_model(self):
        """Train the violence detection model"""
        print("Training violence detection model...")
        
        # Generate training data
        X, y = self._generate_training_data()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model (good for this type of problem)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_scaled, y)
        
        # Save model and scaler
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print("Model trained and saved successfully!")
        print(f"Training accuracy: {self.model.score(X_scaled, y):.3f}")
    
    def detect_violence(self, frame):
        """Detect violence in a single frame"""
        if frame is None:
            return False, 0.0
        
        # Add frame to buffer
        self.frame_buffer.append(frame.copy())
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        # Extract features
        features = self._extract_features(frame)
        if features is None:
            return False, 0.0
            
        features_scaled = self.scaler.transform([features])
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled)[0][1]  # Probability of violence
        
        # Debug output (remove this later)
        print(f"Raw confidence: {confidence:.3f}, Features sample: {features[:5]}")
        
        # Apply lower threshold for better sensitivity
        is_violent = confidence > 0.3  # Lowered from 0.6 to 0.3
        
        return bool(is_violent), float(confidence)
    
    def detect_violence_in_video(self, video_path):
        """Detect violence in an uploaded video"""
        results = []
        
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        violent_frames = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Skip frames for faster processing (analyze every 10th frame)
            if frame_count % 10 == 0:
                is_violent, confidence = self.detect_violence(frame)
                
                results.append({
                    'frame': frame_count,
                    'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS),
                    'is_violent': is_violent,
                    'confidence': confidence
                })
                
                if is_violent:
                    violent_frames += 1
        
        cap.release()
        
        # Calculate overall statistics
        total_analyzed = len(results)
        violence_percentage = (violent_frames / total_analyzed * 100) if total_analyzed > 0 else 0
        
        overall_result = {
            'total_frames': frame_count,
            'analyzed_frames': total_analyzed,
            'violent_frames': violent_frames,
            'violence_percentage': violence_percentage,
            'is_violent_video': violence_percentage > 30,  # Consider video violent if >30% frames are violent
            'frame_results': results[-20:] if len(results) > 20 else results  # Return last 20 results
        }
        
        return overall_result
