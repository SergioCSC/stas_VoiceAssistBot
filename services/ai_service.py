import io
import openai
from config_data import config
from datetime import datetime
from services import convert_audio

openai.api_key = config.OPENAI_API_KEY_FROM_HRY


def transcribe_audio_to_text(file_bytes: bytes = None,
                             file_name: str = 'default_name',
                             path: str = None) -> str:
    """Decode audio and save to txt file"""

    path_save_txt = f"temp/{file_name.split('.')[0]}.txt"
    if path and not file_bytes:
        with open(path, "rb") as audio_file_binary:
            file_bytes = audio_file_binary.read()

    def send_request(sound_bytes, name):
        transcript = openai.Audio.transcribe_raw("whisper-1", sound_bytes, f"{name}.mp3")
        with open(path_save_txt, 'w', encoding="utf-8") as f:
            f.write(transcript["text"])
        return path_save_txt

    try:
        return send_request(file_bytes, file_name)

    except openai.error.InvalidRequestError as e:
        if "Invalid file format" in str(e):
            file_bytes = convert_audio.convert_audio_to_mp3(file_bytes=file_bytes, speed=1)
            return send_request(file_bytes, file_name)

    except openai.error.APIConnectionError:
        return send_request(file_bytes, file_name)


def text_request_to_open_ai(text: str = "Hello!") -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Краткое содержание этого текста {text}"}
        ]
    )
    return completion.choices[0].message["content"]

# text_file = f"../tests/load_files/19537079.txt"
# with open(text_file, "r", encoding="utf-8") as f:
#     print(text_request_to_open_ai(f.read()))
