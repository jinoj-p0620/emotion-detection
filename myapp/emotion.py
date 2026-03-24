import cv2
import numpy as np
import dlib
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import model_from_json

# ----------------------------------------------------
# LOAD EMOTION MODEL
# ----------------------------------------------------
with open("facial_expression_model_structure.json", "r") as f:
    model = model_from_json(f.read())

model.load_weights("facial_expression_model_weights.h5")

# ----------------------------------------------------
# FACE DETECTOR
# ----------------------------------------------------
 
face_detector = dlib.get_frontal_face_detector()

# ----------------------------------------------------
# EMOTIONS
# ----------------------------------------------------
emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

# ----------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------
def detect_emotion():
    cap = cv2.VideoCapture(0)

    frame_skip = 0
    current_emotion = "Detecting..."

    print("🚀 Emotion detection started (Press 'q' to quit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_skip += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector(gray)

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()

            # Draw face box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Emotion detection every 5 frames
            if frame_skip % 5 == 0:
                try:
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_gray = cv2.resize(roi_gray, (48, 48))

                    img_pixels = image.img_to_array(roi_gray)
                    img_pixels = np.expand_dims(img_pixels, axis=0)
                    img_pixels /= 255.0

                    predictions = model.predict(img_pixels, verbose=0)
                    current_emotion = emotions[np.argmax(predictions[0])]
                except Exception:
                    pass

            # Display emotion
            cv2.putText(frame, current_emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ----------------------------------------------------
# RUN
# ----------------------------------------------------
if __name__ == "__main__":
    detect_emotion()
