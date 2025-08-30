# Violence Detection - Real Dataset Training Guide

## Current Issue
Your model is showing "safe" for violent videos because it was trained on synthetic data, which may not capture real violence patterns accurately.

## Solution: Use Your Kaggle Dataset

### Step 1: Prepare Your Dataset
1. Download your violence detection dataset from Kaggle
2. Extract it to a folder (e.g., `C:\Users\YourName\Downloads\violence_dataset`)
3. Make sure it has this structure:
   ```
   dataset_folder/
   ├── violence/     (or violent, fight, Violence, etc.)
   │   ├── video1.mp4
   │   ├── video2.avi
   │   └── ...
   └── non-violence/ (or non-violent, normal, NonViolence, etc.)
       ├── video1.mp4
       ├── video2.avi
       └── ...
   ```

### Step 2: Train with Real Data
Run the training script:
```bash
python train_real_model.py "C:\path\to\your\dataset"
```

Example:
```bash
python train_real_model.py "C:\Users\Dharaneesh\Downloads\violence_dataset"
```

### Step 3: Test the Improved Model
1. The script will automatically replace the synthetic model with one trained on real data
2. Restart your Flask app: `python app.py`
3. Test with your violent video again

## What the Script Does
1. **Loads real videos** from your dataset folders
2. **Extracts features** from actual violent and non-violent scenes
3. **Trains a better model** using Random Forest with 200 trees
4. **Saves the improved model** for use in your app

## Expected Improvements
- ✅ Better accuracy on real violent content
- ✅ Reduced false negatives (violent videos marked as safe)
- ✅ More realistic feature patterns
- ✅ Improved confidence scores

## Troubleshooting
If you get errors:
1. **"Dataset structure not recognized"** - Check folder names (should be like violence/non-violence)
2. **"Failed to open video"** - Make sure videos are in supported formats (.mp4, .avi, .mov, .mkv)
3. **"No features extracted"** - Try with different videos or check if videos are corrupted

## Performance Notes
- The script processes up to 50 videos from each category for speed
- Each video samples 10 frames for feature extraction
- Training takes 2-5 minutes depending on your dataset size
- Larger datasets = better accuracy but longer training time

## Alternative Dataset Structures
The script automatically detects these folder patterns:
- `violence` / `non-violence`
- `violent` / `non-violent` 
- `fight` / `normal`
- `Violence` / `NonViolence`

If your dataset has different folder names, rename them to match one of these patterns.
