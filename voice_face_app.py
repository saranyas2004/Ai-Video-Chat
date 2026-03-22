import threading
import cv2
import pyttsx3
import speech_recognition as sr
import requests

# ---------------- VOICE OUTPUT ----------------
def speak(text):
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

    print("AI:", text)

    engine.say(text)
    engine.runAndWait()

# ---------------- VOICE INPUT ----------------
def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text

    except sr.UnknownValueError:
        print("Could not understand audio")
        return None

    except sr.RequestError:
        print("Speech service error")
        return None

# ---------------- AI (OPENROUTER) ----------------
def get_ai_reply(user_text):
    API_KEY = ""   # 🔐 Replace with your new key

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a friendly AI companion. Speak like a supportive friend and help improve English."},
                    {"role": "user", "content": user_text}
                ]
            }
        )

        result = response.json()

        return result['choices'][0]['message']['content']

    except Exception as e:
        print("Error:", e)
        return "Connection error"

# ---------------- CHAT LOOP (THREAD) ----------------
def chat_loop():
    speak("Hello! How is your day?")

    while True:
        user_text = listen()

        if user_text is None:
            continue

        if user_text.lower() in ["exit", "bye", "stop"]:
            speak("Goodbye! Take care.")
            break

        reply = get_ai_reply(user_text)
        speak(reply)

# ---------------- FACE DETECTION ----------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

# ---------------- MAIN LOOP ----------------
chat_started = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw face box
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Face Detection", frame)

    # Start chat thread only once
    if len(faces) > 0 and not chat_started:
        chat_started = True
        threading.Thread(target=chat_loop, daemon=True).start()

    # Exit with ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# ---------------- CLEANUP ----------------
cap.release()
cv2.destroyAllWindows()