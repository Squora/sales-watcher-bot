import os
import tempfile
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from handlers.conversation import chat
import soundfile as sf
import numpy as np
import wave

def ogg_to_wav(ogg_path, wav_path):
    data, samplerate = sf.read(ogg_path)

    with wave.open(wav_path, 'w') as wf:
        wf.setnchannels(data.shape[1] if len(data.shape) > 1 else 1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)

        int_data = (data * 32767).astype(np.int16)
        wf.writeframes(int_data.tobytes())

async def handle_voice(update, context):
    voice = update.message.voice
    if not voice:
        return

    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_file:
        file = await voice.get_file()
        await file.download_to_drive(ogg_file.name)
        ogg_path = ogg_file.name

    wav_path = ogg_path.replace('.ogg', '.wav')
    ogg_to_wav(ogg_path, wav_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='ru-RU')
        await update.message.reply_text(f"Вы сказали: {text}")

        # Вместо изменения update.message.text, передаем текст напрямую в chat
        await chat(update, context, recognized_text=text)

    except sr.UnknownValueError:
        await update.message.reply_text("Не удалось распознать речь 😔")
    except sr.RequestError:
        await update.message.reply_text("Ошибка сервиса распознавания.")

    os.remove(ogg_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)


async def send_voice_response(update, context, message_text):
    tts = gTTS(text=message_text, lang='ru')
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
        temp_path = f.name
        tts.save(temp_path)

    with open(temp_path, 'rb') as voice_file:
        await update.message.reply_voice(voice_file)

    os.remove(temp_path)