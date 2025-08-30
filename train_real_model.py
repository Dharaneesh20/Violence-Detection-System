#!/usr/bin/env python3
"""
Train Violence Detection Model with Real Dataset

This script helps you train the violence detection model using your Kaggle dataset.

Expected dataset structure:
dataset_folder/
├── violence/     (or violent, fight, Violence, etc.)
│   ├── video1.mp4
│   ├── video2.avi
│   └── ...
└── non-violence/ (or non-violent, normal, NonViolence, etc.)
    ├── video1.mp4
    ├── video2.avi
    └── ...

Usage:
    python train_real_model.py /path/to/your/dataset

Example:
    python train_real_model.py "C:/Users/YourName/Downloads/violence_dataset"
"""

import sys
import os
from violence_detector import ViolenceDetector

def main():
    if len(sys.argv) != 2:
        print("Usage: python train_real_model.py <dataset_path>")
        print("\nExpected dataset structure:")
        print("dataset_folder/")
        print("├── violence/     (violent videos)")
        print("│   ├── video1.mp4")
        print("│   ├── video2.avi")
        print("│   └── ...")
        print("└── non-violence/ (non-violent videos)")
        print("    ├── video1.mp4")
        print("    ├── video2.avi")
        print("    └── ...")
        return
    
    dataset_path = sys.argv[1]
    
    # Check if dataset path exists
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path '{dataset_path}' does not exist!")
        return
    
    print(f"Dataset path: {dataset_path}")
    print(f"Available folders: {os.listdir(dataset_path)}")
    
    # Initialize detector
    detector = ViolenceDetector()
    
    # Train with real dataset
    success = detector.train_with_dataset(dataset_path)
    
    if success:
        print("\n✅ Model training completed successfully!")
        print("The model will now use real video data for better accuracy.")
        print("You can now run the Flask app with: python app.py")
    else:
        print("\n❌ Model training failed!")
        print("Please check your dataset structure and try again.")

if __name__ == "__main__":
    main()
