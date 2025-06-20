import speech_recognition as sr
from pydub import AudioSegment

def recognize_speech(voice_path):
    sound = AudioSegment.from_file(voice_path)
    wav_path = "voice.wav"
    sound.export(wav_path, format="wav")

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)

    try:
        return r.recognize_google(audio, language="ru-RU")
    except sr.UnknownValueError:
        return "Не удалось распознать голос."
    except Exception as e:
        return f"Ошибка распознавания: {str(e)}"
