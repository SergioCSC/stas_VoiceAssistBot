# import io
import asyncio

import openai.error
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, Text
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import LEXICON
from services import convert_audio, ai_service, other_services
from aiogram.types.input_file import FSInputFile

from keyboards import keyboards

from config_data import config

# Initialise router by module level
router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON['/start'])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON['/help'])


# Second version func for download sound with read binary and convert to text
# @router.callback_query(lambda c: True)
@router.message(F.voice | F.audio)
async def process_audio_to_text(message: Message, bot: Bot):
    try:
        file = message.voice if message.voice else message.audio
        file_name = f"{message.voice.file_size}.ogg" if message.voice else message.audio.file_name

        sound_bytes_io = await bot.download(file)
        sound_bytes = sound_bytes_io.read()
        answer_message = await message.reply(
            text=f"File downloaded successfully: \n{file_name}\n Text decoding in progress",
            disable_notification=True)

        file_bytes = convert_audio.convert_audio_to_mp3(file_bytes=sound_bytes, file_name=file_name)

        text_path = ai_service.transcribe_audio_to_text(file_bytes, file_name)
        send_doc = FSInputFile(text_path)

        await bot.delete_message(message.chat.id, answer_message.message_id)
        await message.answer_document(send_doc,
                                      reply_markup=keyboards.create_inline_kb())

        other_services.delete_temp_files()
    except openai.error.InvalidRequestError as e:
        if "Invalid file format" in str(e):
            try:
                file_bytes = convert_audio.convert_audio_to_mp3(file_bytes=file_bytes, file_name=file_name, speed=1)
                text_path = ai_service.transcribe_audio_to_text(file_bytes, file_name)
                send_doc = FSInputFile(text_path)
                await message.answer_document(send_doc,
                                              reply_markup=keyboards.create_inline_kb())
            except BaseException as e:
                await message.reply(text=f"Exception: \n{e}")

    except BaseException as e:
        alert_message = await message.reply(text=f"Exception: \n{e}")
        await asyncio.sleep(60)
        await bot.delete_message(alert_message.chat.id, alert_message.message_id)


@router.callback_query(Text(text=['read_text_button_pressed']))
async def button_read_text_press(callback: CallbackQuery, bot: Bot):
    await callback.answer()

    file = callback.message.document
    file_bytes_io = await bot.download(file)
    text_str = file_bytes_io.read().decode('utf-8')

    split_text = other_services.split_text(text_str)
    for chunk_text in split_text:
        await callback.message.answer(text=chunk_text)

    await callback.answer()
