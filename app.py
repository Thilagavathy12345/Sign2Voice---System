from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pyttsx3

app = Flask(__name__)

# Load trained model
from tensorflow.keras import layers, models

# Dummy model (no training)
model = models.Sequential([
    layers.Input(shape=(63,)),
    layers.Dense(128, activation='relu'),
    layers.Dense(26, activation='softmax')
])

# Labels A-Z
labels = [chr(i) for i in range(65, 91)]

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

camera = cv2.VideoCapture(0)

current_sentence = ""

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def generate_frames():
    global current_sentence
    while True:
        success, frame = camera.read()
        if not success:
            break

        image = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])

                if len(landmarks) == 63:
                    data = np.array(landmarks).reshape(1, -1)
                    prediction = model.predict(data)
                    index = np.argmax(prediction)
                    character = labels[index]

                    current_sentence += character

        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_sentence')
def get_sentence():
    return jsonify({"sentence": current_sentence})

@app.route('/clear')
def clear():
    global current_sentence
    current_sentence = ""
    return jsonify({"status": "cleared"})

@app.route('/speak')
def speak():
    speak_text(current_sentence)
    return jsonify({"status": "spoken"})

if __name__ == "__main__":
    app.run(debug=True)