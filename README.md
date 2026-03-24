# 🎭 Multimodal Emotion Detection System (Face + Audio + EEG)

## 📌 Overview

This project is a **Django-based web application** that detects human emotions using three different modalities:

* 🧑 Facial Expressions (via webcam/image)
* 🎤 Speech/Audio Signals
* 🧠 EEG Brain Signals

The system provides **role-based access**:

* 👨‍💼 Admin
* 👩‍💻 Staff
* 👤 User

---

## ⚙️ Features

* 🔐 Login & Authentication System
* 📷 Real-time Facial Emotion Detection (OpenCV + CNN)
* 🎧 Audio Emotion Recognition (Librosa + ML)
* 🧠 EEG-based Emotion Prediction (Deep Learning)
* 📊 Patient Reports & Dashboard
* 📥 Report Viewing for Staff/Admin

---

## 🛠️ Tech Stack

* **Backend:** Django (Python)
* **ML/DL:** TensorFlow, Keras, Scikit-learn
* **Image Processing:** OpenCV, dlib
* **Audio Processing:** Librosa
* **Frontend:** HTML, CSS, JS

---

## 📁 Project Structure

```
EMOTION/
│── manage.py
│── EEG/                # Django settings
│── myapp/              # Main app
│── templates/          # HTML files
│── media/              # Uploaded files
```

---

## 🚀 Setup Instructions

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/emotion-detection.git
cd emotion-detection
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Run Migrations

```
python manage.py migrate
```

---

### 5️⃣ Create Admin User

```
python manage.py createsuperuser
```

---

### 6️⃣ Run Server

```
python manage.py runserver
```

 Access

* Admin Panel → `/admin`
* Application → `http://127.0.0.1:8000/`

Important Notes

* Model files are not included due to size:

  * EEG model (.h5)
  * Face model (.h5)
  * Landmark file (.dat)

Download from:
https://drive.google.com/drive/folders/1aHY2eUDFOfOjF6qZlL3TiIV5xuljc5dA?usp=drive_link

Modules

 Admin

* Manage staff
* View reports
* Monitor system

Staff

* Upload EEG data
* View patient reports

User

* Submit data
* View results


 Future Improvements

* Real-time EEG streaming
* Mobile app integration
* Model accuracy improvement

 Author

JINOJ P
