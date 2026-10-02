import datetime
import os
import subprocess
import webbrowser
import pyttsx3
import requests
import speech_recognition as sr

# ================= CONFIGURATION =================
# Gemini API Key (User apni key environment variable ya yahan daal sakta hai)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6L_3yj4XpzRr6ql2bwv4LnvwhJEKWSX2rm3ZuD948nf9g")
WAKE_WORDS = ["wake up jarvis", "hey jarvis", "jarvis", "wake up"]
# =================================================

# 1. Offline Speech Engine (Local TTS)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if voices:
  engine.setProperty("voice", voices[0].id)  # Male voice
engine.setProperty("rate", 175)


def speak(text):
  print(f"\n[JARVIS]: {text}")
  engine.say(text)
  engine.runAndWait()


# 2. Network Status Check
def is_online():
  try:
    requests.get("https://www.google.com", timeout=3)
    return True
  except Exception:
    return False


# 3. Audio Listener
recognizer = sr.Recognizer()


def listen(timeout=5, phrase_limit=6):
  with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=0.6)
    try:
      audio = recognizer.listen(
          source, timeout=timeout, phrase_time_limit=phrase_limit
      )
      query = recognizer.recognize_google(audio, language="en-IN")
      return query.lower()
    except Exception:
      return ""


# 4. Offline Actions Handler (Local Machine / OS Controls)
def execute_offline_tasks(command):
  # Current Time
  if "time" in command:
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}, Sir."

  # Current Date
  if "date" in command or "day" in command:
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")
    return f"Today is {today}."

  # Open Core Tools
  if "open youtube" in command or "play youtube" in command:
    webbrowser.open("https://youtube.com")
    return "Opening YouTube, Sir."

  if "open google" in command:
    webbrowser.open("https://google.com")
    return "Opening Google."

  if "open calculator" in command:
    os.system("calc" if os.name == "nt" else "gnome-calculator")
    return "Launching Calculator."

  if "open notepad" in command:
    os.system("notepad" if os.name == "nt" else "gedit")
    return "Opening Notepad."

  return None


# 5. Online AI Engine (Google Gemini REST API)
def query_gemini(prompt):
  if not is_online():
    return (
        "Sir, we are currently offline and no local matching command was found."
    )

  if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    return "Please set your Gemini API key in the configuration or environment variables."

  url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
  headers = {"Content-Type": "application/json"}
  payload = {
      "contents": [{
          "parts": [{
              "text": (
                  "You are JARVIS, a highly efficient personal AI assistant."
                  " Answer concisely in 1 to 2 spoken sentences without"
                  f" markdown formatting: {prompt}"
              )
          }]
      }]
  }

  try:
    res = requests.post(url, headers=headers, json=payload, timeout=10)
    data = res.json()
    if "candidates" in data:
      return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return "Sir, I could not retrieve data from the central servers."
  except Exception:
    return "Network connection timed out."


# 6. Main Voice Loop
def main():
  speak("Jarvis initialized. Standing by for your command, Sir.")
  is_active = False

  while True:
    print(
        "\r[Standby] Listening for wake word ('Wake up Jarvis')...",
        end="",
        flush=True,
    )
    user_input = listen(timeout=4, phrase_limit=4)

    if not user_input:
      continue

    print(f"\n[Detected]: {user_input}")

    # Wake Word Detection
    if not is_active:
      if any(wake in user_input for wake in WAKE_WORDS):
        is_active = True
        speak("Yes Sir? Systems active.")
      continue

    # Standby / Shutdown Commands
    if any(
        w in user_input
        for w in ["sleep", "go to sleep", "sleep jarvis", "standby"]
    ):
      speak("Entering standby mode, Sir.")
      is_active = False
      continue

    if any(w in user_input for w in ["exit", "shutdown", "quit", "power down"]):
      speak("Shutting down core systems. Goodbye, Sir.")
      break

    # 1st Priority: Check Offline Actions
    offline_reply = execute_offline_tasks(user_input)
    if offline_reply:
      speak(offline_reply)
      continue

    # 2nd Priority: Online Gemini AI Query
    ai_reply = query_gemini(user_input)
    speak(ai_reply)


if __name__ == "__main__":
  main()
