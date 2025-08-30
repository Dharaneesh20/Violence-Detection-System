#!/usr/bin/env python3
"""
Retrain Violence Detection Model with Improved Synthetic Data

This script retrains the model with better synthetic data patterns
to improve live detection accuracy.
"""

import os
from violence_detector import ViolenceDetector

def main():
    print("🔄 Retraining violence detection model with improved data...")
    
    # Remove existing model to force retraining
    model_path = "models/violence_model.pkl"
    scaler_path = "models/scaler.pkl"
    
    if os.path.exists(model_path):
        os.remove(model_path)
        print("Removed old model")
    
    if os.path.exists(scaler_path):
        os.remove(scaler_path)
        print("Removed old scaler")
    
    # Initialize detector (will train new model)
    print("Initializing detector with improved training data...")
    detector = ViolenceDetector()
    
    print("\n✅ Model retraining completed!")
    print("🎯 Improvements made:")
    print("   • Better synthetic data patterns")
    print("   • Lowered detection threshold (0.6 → 0.3)")
    print("   • More realistic feature distributions")
    print("   • Enhanced motion detection")
    
    print("\n🚀 Now restart your Flask app:")
    print("   python app.py")
    print("\n💡 The live detection should be more sensitive now!")

if __name__ == "__main__":
    main()
