import requests
import pyttsx3
import pyaudio
import json
import os
from vosk import Model, KaldiRecognizer

class VoiceAssistant:
    def __init__(self):
        # Инициализация голосового движка
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Скорость речи
        self.engine.setProperty('volume', 1.0)  # Громкость (0-1)
        
        # Инициализация модели Vosk для распознавания речи
        if not os.path.exists("vosk-model-small-ru-0.22"):
            print("Пожалуйста, скачайте модель с https://alphacephei.com/vosk/models и распакуйте в папку с программой")
            exit(1)
            
        self.model = Model("vosk-model-small-ru-0.22")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        # Инициализация PyAudio для записи звука
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, 
                                 channels=1, 
                                 rate=16000, 
                                 input=True, 
                                 frames_per_buffer=8000)
        
        # Данные текущего пользователя
        self.current_user = None
        
        # Доступные команды
        self.commands = {
            "создать": self.create_user,
            "имя": self.get_name,
            "страна": self.get_country,
            "анкета": self.get_profile,
            "сохранить": self.save_photo,
            "помощь": self.help_command
        }
    
    def speak(self, text):
        """Произносит переданный текст"""
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Слушает и распознает голосовые команды"""
        print("Слушаю...")
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                command = result.get("text", "").lower()
                if command:
                    print(f"Вы сказали: {command}")
                    return command
        return ""
    
    def create_user(self):
        """Создает нового случайного пользователя"""
        try:
            response = requests.get("https://randomuser.me/api/")
            if response.status_code == 200:
                data = response.json()
                self.current_user = data["results"][0]
                self.speak("Новый пользователь создан.")
            else:
                self.speak("Ошибка при создании пользователя. Попробуйте снова.")
        except Exception as e:
            self.speak("Произошла ошибка при подключении к интернету.")
            print(f"Error: {e}")
    
    def get_name(self):
        """Произносит имя текущего пользователя"""
        if self.current_user:
            first_name = self.current_user["name"]["first"]
            last_name = self.current_user["name"]["last"]
            self.speak(f"Имя пользователя: {first_name} {last_name}")
        else:
            self.speak("Сначала создайте пользователя командой 'создать'.")
    
    def get_country(self):
        """Произносит страну текущего пользователя"""
        if self.current_user:
            country = self.current_user["location"]["country"]
            self.speak(f"Страна пользователя: {country}")
        else:
            self.speak("Сначала создайте пользователя командой 'создать'.")
    
    def get_profile(self):
        """Формирует анкету пользователя"""
        if self.current_user:
            user = self.current_user
            profile = (
                f"Анкета пользователя. "
                f"Имя: {user['name']['title']} {user['name']['first']} {user['name']['last']}. "
                f"Пол: {'мужской' if user['gender'] == 'male' else 'женский'}. "
                f"Дата рождения: {user['dob']['date'][:10]}. "
                f"Возраст: {user['dob']['age']} лет. "
                f"Страна: {user['location']['country']}. "
                f"Город: {user['location']['city']}. "
                f"Email: {user['email']}. "
                f"Телефон: {user['phone']}."
            )
            self.speak(profile)
        else:
            self.speak("Сначала создайте пользователя командой 'создать'.")
    
    def save_photo(self):
        """Сохраняет фотографию пользователя"""
        if self.current_user:
            photo_url = self.current_user["picture"]["large"]
            try:
                response = requests.get(photo_url)
                if response.status_code == 200:
                    with open("user_photo.jpg", "wb") as f:
                        f.write(response.content)
                    self.speak("Фотография пользователя сохранена в файл user_photo.jpg")
                else:
                    self.speak("Не удалось загрузить фотографию.")
            except Exception as e:
                self.speak("Произошла ошибка при сохранении фотографии.")
                print(f"Error: {e}")
        else:
            self.speak("Сначала создайте пользователя командой 'создать'.")
    
    def help_command(self):
        """Произносит список доступных команд"""
        commands_list = ", ".join(self.commands.keys())
        self.speak(f"Доступные команды: {commands_list}")
    
    def process_command(self, command):
        """Обрабатывает распознанную команду"""
        for cmd in self.commands:
            if cmd in command:
                self.commands[cmd]()
                return
        
        # Если команда не распознана
        self.speak("Я не понял команду. Попробуйте сказать 'помощь' для списка команд.")
    
    def run(self):
        """Основной цикл работы ассистента"""
        self.speak("Голосовой ассистент запущен. Скажите 'помощь' для списка команд.")
        
        while True:
            try:
                command = self.listen()
                if command:
                    if "стоп" in command or "выход" in command:
                        self.speak("До свидания!")
                        break
                    self.process_command(command)
            except KeyboardInterrupt:
                self.speak("До свидания!")
                break
        
        # Очистка ресурсов
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()