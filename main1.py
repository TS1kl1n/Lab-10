import requests
import pyttsx3
import pyaudio
import json
import os
from vosk import Model, KaldiRecognizer

# Инициализация синтезатора речи
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Инициализация распознавания речи
if not os.path.exists("model"):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)

model = Model("model")
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Функции для обработки команд
def generate_joke():
    response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
    if response.status_code == 200:
        joke = response.json()
        if joke["type"] == "single":
            return joke["joke"]
        else:
            return f"{joke['setup']} ... {joke['delivery']}"
    else:
        return "Не удалось получить шутку."

def joke_type():
    return "Команды: 'создать' - генерация новой шутки, 'тип' - тип шутки, 'прочесть' - прочитать шутку, 'категория' - категория шутки, 'записать' - записать шутку."

def joke_category():
    response = requests.get("https://v2.jokeapi.dev/joke/Any?safe-mode")
    if response.status_code == 200:
        joke = response.json()
        return joke["category"]
    else:
        return "Не удалось получить категорию."

def save_joke(joke):
    with open("jokes.txt", "a") as file:
        file.write(joke + "\n")
    return "Шутка сохранена."

# Основной цикл для распознавания команд
print("Голосовой ассистент запущен...")

while True:
    data = stream.read(4000)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        command = result.get("text", "").lower()
        
        if "создать" in command:
            joke = generate_joke()
            speak(joke)
        elif "тип" in command:
            response = joke_type()
            speak(response)
        elif "категория" in command:
            category = joke_category()
            speak(category)
        elif "записать" in command:
            joke = generate_joke()
            response = save_joke(joke)
            speak(response)
        else:
            speak("Команда не распознана. Попробуйте еще раз.")
