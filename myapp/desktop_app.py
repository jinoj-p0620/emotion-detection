import os
import django
import tkinter as tk
from tkinter import messagebox
import threading
import cv2
import numpy as np
import dlib
import sounddevice as sd
import librosa
import pickle
from datetime import datetime
from tensorflow.keras.models import model_from_json
import warnings
warnings.filterwarnings("ignore")

# ====================================================
# DJANGO SETUP
# ====================================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EEG.settings")
django.setup()

from myapp.models import emotion_table, patient_table

PATIENT_ID = 4   # Change dynamically if needed

# ====================================================
# SAVE EMOTION USING DJANGO ORM
# ====================================================
def save_emotion(emotion, source):
    emotion_table.objects.create(
        patient_id=patient_table.objects.get(id=PATIENT_ID),
        emotion=emotion,
        source=source,
        date=datetime.now().date(),
        time=datetime.now().time()
    )
    print(f"💾 Saved → {emotion} ({source})")

# ====================================================
# LOAD VIDEO EMOTION MODEL
# ====================================================
with open("facial_expression_model_structure.json", "r") as f:
    video_model = model_from_json(f.read())

video_model.load_weights("facial_expression_model_weights.h5")

face_detector = dlib.get_frontal_face_detector()

video_emotions = (
    'angry', 'disgust', 'fear',
    'happy', 'sad', 'surprise', 'neutral'
)

# ====================================================
# VIDEO EMOTION THREAD (SAFE)
# ====================================================
def run_video_emotion():
    cap = cv2.VideoCapture(0)
    frame_skip = 0
    last_emotion = None

    print("🎥 Video Emotion Monitoring Started")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_skip += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h_frame, w_frame = gray.shape

        faces = face_detector(gray)

        for face in faces:
            x = max(0, face.left())
            y = max(0, face.top())
            w = face.width()
            h = face.height()

            x2 = min(x + w, w_frame)
            y2 = min(y + h, h_frame)

            if x2 <= x or y2 <= y:
                continue

            cv2.rectangle(frame, (x, y), (x2, y2), (255, 0, 0), 2)

            if frame_skip % 10 == 0:
                roi = gray[y:y2, x:x2]

                if roi.size == 0:
                    continue

                roi = cv2.resize(roi, (48, 48))
                roi = roi.astype("float32") / 255.0
                roi = np.expand_dims(roi, axis=-1)
                roi = np.expand_dims(roi, axis=0)

                preds = video_model.predict(roi, verbose=0)
                emotion = video_emotions[np.argmax(preds[0])]
                confidence = float(np.max(preds[0]))

                if emotion != last_emotion:
                    save_emotion(emotion, "Video")
                    last_emotion = emotion

                cv2.putText(
                    frame,
                    f"{emotion} ({confidence:.2f})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

        cv2.imshow("Patient Video Emotion", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🎥 Video Emotion Stopped")

# ====================================================
# AUDIO FEATURE EXTRACTION (EXACTLY 260 FEATURES)
# ====================================================
def extract_audio_features(y, sr):
    y, _ = librosa.effects.trim(y, top_db=25)
    if len(y) == 0:
        return None

    y = librosa.util.normalize(y)

    # MFCC (40)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfcc_mean = np.mean(mfcc.T, axis=0)

    # Delta (40)
    delta = librosa.feature.delta(mfcc)
    delta_mean = np.mean(delta.T, axis=0)

    # Delta-Delta (40)
    delta2 = librosa.feature.delta(mfcc, order=2)
    delta2_mean = np.mean(delta2.T, axis=0)

    # Chroma (12)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma.T, axis=0)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_mean = np.mean(librosa.power_to_db(mel).T, axis=0)

    features = np.hstack([
        mfcc_mean,    # 40
        delta_mean,   # 40
        delta2_mean,  # 40
        chroma_mean,  # 12
        mel_mean      # 128
    ])

    if features.shape[0] != 260:
        raise ValueError(f"Audio feature mismatch: {features.shape[0]}")
    return features

# ====================================================
# AUDIO EMOTION THREAD (SAFE)
# ====================================================

def run_audio_emotion():
    with open("emotion_model.pkl", "rb") as f:
        audio_model = pickle.load(f)
    fs = 22050
    duration = 3
    last_emotion = None

    labels = [
        'Angry', 'Disgusted', 'Fearful',
        'Happy', 'Sad', 'Suprised', 'Neutral'
    ]

    print("🎤 Audio Emotion Monitoring Started")

    def audio_callback(indata, frames, time, status):
        nonlocal last_emotion
        audio_data = indata.flatten()

        features = extract_audio_features(audio_data, fs)
        if features is None:
            return

        features = features.reshape(1, -1)

        pred = audio_model.predict(features)[0]
        conf = audio_model.predict_proba(features).max()
        emotion = labels[pred]

        if emotion != last_emotion:
            save_emotion(emotion, "Audio")
            last_emotion = emotion

        print(f"🎧 {emotion} ({conf:.2f})")

    with sd.InputStream(
        samplerate=fs,
        channels=1,
        blocksize=fs * duration,
        callback=audio_callback
    ):
        sd.sleep(1000000)

# ====================================================
# TKINTER GUI
# ====================================================
class EmotionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bed Patient Emotion Monitor")
        self.root.geometry("420x400")

        tk.Label(
            root,
            text="Patient Emotion Monitoring",
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        self.video_var = tk.BooleanVar()
        self.audio_var = tk.BooleanVar()

        tk.Checkbutton(
            root,
            text="Video Emotion (Camera)",
            variable=self.video_var,
            font=("Arial", 11)
        ).pack(anchor="w", padx=100, pady=5)

        tk.Checkbutton(
            root,
            text="Audio Emotion (Microphone)",
            variable=self.audio_var,
            font=("Arial", 11)
        ).pack(anchor="w", padx=100, pady=5)

        tk.Button(
            root,
            text="START MONITORING",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_selected
        ).pack(pady=30)

        tk.Label(
            root,
            text="Press 'q' in video window to stop",
            font=("Arial", 9, "italic")
        ).pack()

    def start_selected(self):
        if not self.video_var.get() and not self.audio_var.get():
            messagebox.showwarning(
                "Selection Required",
                "Please select Audio or Video (or both)."
            )
            return

        if self.video_var.get():
            threading.Thread(
                target=run_video_emotion,
                daemon=True
            ).start()

        if self.audio_var.get():
            threading.Thread(
                target=run_audio_emotion,
                daemon=True
            ).start()

# ====================================================
# MAIN
# ====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionApp(root)
    root.mainloop()
