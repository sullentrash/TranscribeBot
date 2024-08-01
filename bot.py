import os
import asyncio
from aiogram import Bot, Dispatcher
from pathlib import Path
from aiogram.filters import Command
from aiogram import F
from aiogram import types
from aiogram.types import ContentType, File, Message
import time
import logging
import json
from pydub import AudioSegment

from handlers import resp

import wave
import sys

from vosk import Model, KaldiRecognizer, SetLogLevel

logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%d/%m/%Y %H:%M:%S',
    force=True
)

bot = Bot(token = '6867613375:AAH0toLnIeVzQfSUtATWwdaXM6c-SPuFW6E')
dp = Dispatcher()

# Запуск бота
async def bot_task(_token):
    """Main file to execute bot pulling engine

    Args:
        _token (str): bot token for telegram API
    """
    #dp.include_routers(resp.router)
    logging.info("Bot started")
    await bot.delete_webhook(drop_pending_updates = True)
    await dp.start_polling(bot)

def transcribe_audio(file_path):
    '''
    # Load MP3 file
    audio = AudioSegment.from_mp3("output_audio.mp3")
    # Convert to WAV
    audio.export("output_audio.wav", format="wav")
    audio = AudioSegment.from_wav(file_path)
    # Convert to mono
    audio = audio.set_channels(1)
    # Set frame rate
    audio = audio.set_frame_rate(16000)

    # Save new audio
    audio.export("english_mono.wav", format="wav")
    '''
    # Initialize model and recognizer
    model = Model("model/vosk-model-en-us-0.42-gigaspeech")
    rec = KaldiRecognizer(model, 16000)

    # Open WAV file
    wf = wave.open("english_mono.wav", "rb")

    # List to hold all text segments
    transcribed_text_list = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            transcribed_text_list.append(result['text'])

    # Handle last part of audio
    final_result = json.loads(rec.FinalResult())
    transcribed_text_list.append(final_result['text'])

    # Concatenate all text segments
    complete_text = ' '.join(transcribed_text_list)

    # Write the complete transcribed text to a text file
    with open('transcribed_text.txt', 'w') as f:
        f.write(complete_text)

    print("Transcription complete. Output written to transcribed_text.txt.")

@dp.message_handler(content_types=[types.ContentType.VOICE,types.ContentType.AUDIO,types.ContentType.DOCUMENT])
async def voice_message_handler(message: types.Message):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"
    await message.answer(text)

    os.remove(file_on_disk)
    
@dp.message(F.text, Command('start'))
async def start_command(message: Message):
    await bot.send_message(message.chat.id, 'Hello hello hello')

if __name__ == "__main__":
    asyncio.run(bot_task('6867613375:AAH0toLnIeVzQfSUtATWwdaXM6c-SPuFW6E'))
    #transcribe_audio('english.wav')