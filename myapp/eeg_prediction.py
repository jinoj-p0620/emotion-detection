import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import os

# --- HARDCODED ABSOLUTE PATHS ---
# Ensure these files are physically present in G:\BTech\EEG\myapp\
MODEL_PATH = r'eeg_emotion_model.h5'
SCALER_PATH = r'scaler.gz'
ENCODER_PATH = r'label_encoder.gz'
FEAT_PATH = r'selected_features.gz'

# Safe Global Loading
try:
    # 1. Load the essential feature names (the 50 names selected by Random Forest)
    selected_features = joblib.load(FEAT_PATH)

    # 2. Load the Neural Network model
    model = tf.keras.models.load_model(MODEL_PATH)

    # 3. Load the scaler (fitted only on those 50 columns)
    scaler = joblib.load(SCALER_PATH)

    # 4. Load the Label Encoder (to turn 0,1,2 back into Positive, Negative, Neutral)
    label_encoder = joblib.load(ENCODER_PATH)

    print("--- SUCCESS: AI Pipeline Assets Loaded ---")
except Exception as e:
    print(f"--- ERROR: Could not initialize AI assets: {e} ---")
    model = scaler = label_encoder = selected_features = None


def predict_eeg_emotion(file_path):
    """
    Predicts emotion based on the 50 essential features defined during training.
    """
    if model is None:
        return "Model not loaded. Check paths."

    try:
        # 1. Read the uploaded CSV file
        df = pd.read_csv(file_path)

        # 2. FEATURE SELECTION: Only take the 50 columns the model expects
        # This matches your training: X_essential = X[essential_feature_names]
        df_essential = df[selected_features]

        # 3. Take the first row for prediction
        sample_row = df_essential.iloc[0]

        # 4. SCALING: Transform the sample using the loaded scaler
        # Reshape to (1, 50) because the model expects a 2D batch input
        scaled_sample = scaler.transform(sample_row.values.reshape(1, -1))

        # 5. PREDICTION
        prediction = model.predict(scaled_sample, verbose=0)
        class_idx = np.argmax(prediction)

        # 6. DECODE: Convert numeric index back to emotion text
        result = label_encoder.inverse_transform([class_idx])[0]

        print(f"Result: {result} (Processed {len(selected_features)} essential features)")
        return result

    except KeyError as e:
        return f"CSV Mismatch: Uploaded file is missing required feature: {str(e)}"
    except Exception as e:
        return f"Processing Error: {str(e)}"