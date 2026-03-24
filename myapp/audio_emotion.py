import os
import numpy as np
import librosa
import pickle

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report
from collections import Counter

# ----------------------------------------------------
# EMOTIONS
# ----------------------------------------------------
emotions = ('Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Suprised', 'Neutral')

emotion_map = {
    "Angry": 0,
    "Disgusted": 1,
    "Fearful": 2,
    "Happy": 3,
    "Sad": 4,
    "Suprised": 5,
    "Neutral": 6
}

reverse_emotion_map = {v: k for k, v in emotion_map.items()}

# ----------------------------------------------------
# FEATURE EXTRACTION (IMPROVED)
# ----------------------------------------------------
def extract_features(file_path):
    try:
        # Load audio
        y, sr = librosa.load(file_path, duration=3)

        # Remove silence
        y, _ = librosa.effects.trim(y, top_db=25)

        if len(y) == 0:
            return None

        # Normalize amplitude
        y = librosa.util.normalize(y)

        # MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        mfcc_mean = np.mean(mfcc.T, axis=0)

        # MFCC Delta
        delta = librosa.feature.delta(mfcc)
        delta_mean = np.mean(delta.T, axis=0)

        # MFCC Delta-Delta
        delta2 = librosa.feature.delta(mfcc, order=2)
        delta2_mean = np.mean(delta2.T, axis=0)

        # Chroma
        chroma = np.mean(
            librosa.feature.chroma_stft(y=y, sr=sr, tuning=0).T,
            axis=0
        )

        # Log-Mel Spectrogram
        mel = np.mean(
            librosa.power_to_db(
                librosa.feature.melspectrogram(y=y, sr=sr)
            ).T,
            axis=0
        )

        return np.hstack((mfcc_mean, delta_mean, delta2_mean, chroma, mel))

    except Exception as e:
        print("Feature error:", e)
        return None

# ----------------------------------------------------
# LOAD DATASET
# ----------------------------------------------------
def load_dataset(dataset_path=r"Emotions"): #Path of dataset
    X, y = [], []

    for emotion in emotions:
        folder = os.path.join(dataset_path, emotion)

        if not os.path.exists(folder):
            print(f"Missing folder: {folder}")
            continue

        for file in os.listdir(folder):
            if file.lower().endswith(".wav"):
                path = os.path.join(folder, file)
                features = extract_features(path)

                if features is not None:
                    X.append(features)
                    y.append(emotion_map[emotion])

    return np.array(X), np.array(y)

# ----------------------------------------------------
# TRAIN MODEL (WITH GRID SEARCH)
# ----------------------------------------------------
def train_model():
    print("🔹 Loading dataset...")
    X, y = load_dataset()

    print("Feature shape:", X.shape)
    print("Label shape:", y.shape)
    print("Class distribution:", Counter(y))

    if len(X) == 0:
        print("❌ No data found.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Pipeline
    pipeline = make_pipeline(
        StandardScaler(),
        SVC(kernel='rbf', probability=True, class_weight='balanced')
    )

    # Hyperparameter tuning
    param_grid = {
        'svc__C': [1, 10, 100],
        'svc__gamma': ['scale', 0.01, 0.001]
    }

    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        n_jobs=-1,
        verbose=2
    )

    print("🚀 Training with GridSearch...")
    grid.fit(X_train, y_train)

    model = grid.best_estimator_
    print("✅ Best parameters:", grid.best_params_)

    # Evaluation
    y_pred = model.predict(X_test)
    print("\n🎯 Accuracy:", accuracy_score(y_test, y_pred))
    print("\n📊 Classification Report:\n")
    print(classification_report(y_test, y_pred, target_names=emotions))

    # Save model
    with open("emotion_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("💾 Model saved as emotion_model.pkl")

# ----------------------------------------------------
# PREDICT EMOTION
# ----------------------------------------------------
def predict_emotion(audio_file):
    with open("emotion_model.pkl", "rb") as f:
        model = pickle.load(f)

    features = extract_features(audio_file)
    if features is None:
        print("Invalid audio")
        return

    features = features.reshape(1, -1)
    pred = model.predict(features)[0]
    conf = model.predict_proba(features).max()

    print(f"Detected Emotion: {reverse_emotion_map[pred]}")
    print(f"Confidence: {conf:.2f}")

# ----------------------------------------------------
# MAIN
# ----------------------------------------------------
# if __name__ == "__main__":
#     print("\n1. Train Model")
#     print("2. Predict Emotion")
#     choice = input("Select option (1/2): ")
#     if choice == "1":
#         train_model()
#     elif choice == "2":
#         path = input("Enter WAV file path: ")
#         predict_emotion(path)
#     else:
#         print("Invalid choice")
