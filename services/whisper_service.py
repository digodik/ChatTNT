# services/whisper_service.py
import logging
import os
import time
from typing import Tuple, Optional
import tempfile
import subprocess
import asyncio
import whisper
import torch

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model_loading = False
        self.whisper_languages = {
            'auto': None,
            'en': 'en',
            'ru': 'ru',
            'pl': 'pl',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
        }

        # Detect device (GPU if available, otherwise CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        if self.device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Version: {torch.version.cuda}")

        logger.info(f"Loading Whisper model '{self.model_name}' into memory...")
        self.model = whisper.load_model(self.model_name, device=self.device)
        logger.info(f"Whisper model '{self.model_name}' loaded and ready in memory on {self.device}")


    async def _prepare_audio_file(self, audio_path: str) -> Tuple[str, bool]:
        try:
            file_size = os.path.getsize(audio_path)
            max_size = 100 * 1024 * 1024

            if file_size <= max_size:
                return audio_path, False

            temp_dir = tempfile.gettempdir()
            temp_filename = f"whisper_{int(time.time())}.mp3"
            temp_path = os.path.join(temp_dir, temp_filename)

            cmd = [
                'ffmpeg', '-i', audio_path,
                '-acodec', 'mp3', '-ab', '64k', '-ar', '16000',
                '-y', temp_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=300)

            if result.returncode != 0 or not os.path.exists(temp_path):
                return audio_path, False

            return temp_path, True

        except Exception as e:
            logger.error(f"Error preparing audio: {e}")
            return audio_path, False

    async def transcribe(self, audio_path: str, language_code: str = None, user_lang: str = "en",
                        get_string_func=None, enable_speaker_diarization: bool = False,
                        status_callback=None) -> Tuple[bool, str]:

        if enable_speaker_diarization:
            return False, "Speaker diarization not supported in Whisper"

        temp_file_path = None
        try:
            if status_callback:
                await status_callback("compressing")

            prepared_file, is_temp = await self._prepare_audio_file(audio_path)
            if is_temp:
                temp_file_path = prepared_file

            if status_callback:
                await status_callback("starting")

            language = None
            if language_code and language_code != "auto":
                language = self.whisper_languages.get(language_code, language_code)

            logger.info(f"Starting local Whisper transcription for: {prepared_file}")
            loop = asyncio.get_event_loop()

            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                prepared_file,
                language
            )

            detected_language = result.get('language', 'unknown')
            text = result.get('text', '')

            logger.info(f"Transcription completed. Detected language: {detected_language}")

            if status_callback:
                await status_callback("completed", detected_language)

            return True, text

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            if status_callback:
                await status_callback("error", str(e))
            return False, f"Whisper error: {str(e)}"

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

    def _transcribe_sync(self, audio_path: str, language: Optional[str]) -> dict:
        options = {}
        if language:
            options['language'] = language

        result = self.model.transcribe(audio_path, **options)
        return result

def create_whisper_service(model_name: str = "base") -> WhisperService:
    return WhisperService(model_name)
