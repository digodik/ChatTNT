# services/transcription_service.py
import logging
from typing import Tuple, Optional
from services.assemblyai_service import AssemblyAIService
from services.whisper_service import WhisperService
from utils import get_user_lang, set_state
from strings import ASSEMBLYAI_LANGUAGES, get_string
from utils import get_state, set_state
from menus import show_transcription_actions_menu
from database import log_request

logger = logging.getLogger(__name__)

class TranscriptionManager:
    def __init__(self, assemblyai_api_key: str = None, whisper_service: WhisperService = None):
        self.assemblyai_api_key = assemblyai_api_key
        self.whisper_service = whisper_service

    def create_status_callback(self, user_id: str, status_msg, target_language: str):
        user_lang = get_user_lang(user_id)
        
        async def status_callback(status_type, data=None):
            if not status_msg:
                return
                
            if status_type == "compressing":
                await status_msg.edit_text(get_string("processing_file", user_lang))
            elif status_type == "uploading":
                await status_msg.edit_text(get_string("uploading_file", user_lang))
            elif status_type == "starting":
                if target_language is None:
                    await status_msg.edit_text(get_string("starting_auto_detection", user_lang))
                else:
                    target_lang_name = ASSEMBLYAI_LANGUAGES.get(target_language, target_language)
                    await status_msg.edit_text(get_string("starting_transcription", user_lang, lang_name=target_lang_name))
            elif status_type == "transcribing":
                elapsed_time = data
                await status_msg.edit_text(get_string("transcribing_status", user_lang, elapsed_time=elapsed_time))
            elif status_type == "completed":
                detected_language = data
                set_state(user_id, "detected_language", detected_language)
                detected_lang_name = ASSEMBLYAI_LANGUAGES.get(detected_language, detected_language)
                await status_msg.edit_text(get_string("transcription_completed", user_lang, detected_lang=detected_lang_name))
            elif status_type == "error":
                error_msg = data
                await status_msg.edit_text(get_string("transcription_error", user_lang, error=error_msg))
        
        return status_callback

    async def transcribe_with_assemblyai(self, audio_path: str, message, status_msg=None, 
                                       target_language: str = None, enable_speakers: bool = False) -> Tuple[bool, str]:
        if not self.assemblyai_api_key:
            return False, "AssemblyAI API не настроен"
        
        user_id = str(message.from_user.id)
        user_lang = get_user_lang(user_id)
        
        async def status_callback(status_type, data=None):
            if not status_msg:
                return
                
            if status_type == "compressing":
                await status_msg.edit_text(get_string("processing_file", user_lang))
            elif status_type == "uploading":
                await status_msg.edit_text(get_string("uploading_file", user_lang))
            elif status_type == "starting":
                if enable_speakers:
                    await status_msg.edit_text("🎭 Starting transcription with speaker separation...")
                elif target_language is None:
                    await status_msg.edit_text(get_string("starting_auto_detection", user_lang))
                else:
                    target_lang_name = ASSEMBLYAI_LANGUAGES.get(target_language, target_language)
                    await status_msg.edit_text(get_string("starting_transcription", user_lang, lang_name=target_lang_name))
            elif status_type == "transcribing":
                elapsed_time = data
                if enable_speakers:
                    await status_msg.edit_text(f"🎭 Processing different speakers... ({elapsed_time:.0f}s)")
                else:
                    await status_msg.edit_text(get_string("transcribing_status", user_lang, elapsed_time=elapsed_time))
            elif status_type == "completed":
                detected_language = data
                set_state(user_id, "detected_language", detected_language)
                
                detected_lang_name = ASSEMBLYAI_LANGUAGES.get(detected_language, detected_language)
                if enable_speakers:
                    await status_msg.edit_text(f"✅ Transcription with speaker separation completed! Language: {detected_lang_name}")
                else:
                    await status_msg.edit_text(get_string("transcription_completed", user_lang, detected_lang=detected_lang_name))
            elif status_type == "error":
                error_msg = data
                await status_msg.edit_text(get_string("transcription_error", user_lang, error=error_msg))
        
        try:
            async with AssemblyAIService(self.assemblyai_api_key) as service:
                success, result = await service.transcribe(
                    audio_path=audio_path,
                    language_code=target_language,
                    user_lang=user_lang,
                    get_string_func=get_string,
                    enable_speaker_diarization=enable_speakers,
                    status_callback=status_callback
                )
            
            if success:
                log_request(user_id, "assemblyai_transcription")
            
            return success, result
        
        except Exception as e:
            logger.error(f"Error during AssemblyAI transcription: {e}", exc_info=True)
            if status_msg:
                await status_msg.edit_text(get_string("error_occurred", user_lang, error=str(e)))
            else:
                await message.reply(get_string("error_occurred", user_lang, error=str(e)))
            return False, f"Error during AssemblyAI transcription: {str(e)}"

    async def transcribe_audio(self, audio_path: str, message, status_msg=None, 
                             target_language: str = None, enable_speakers: bool = False) -> Tuple[bool, str]:

        user_id = str(message.from_user.id)
        user_lang = get_user_lang(user_id)
        
        if enable_speakers:
            if not self.assemblyai_api_key:
                return False, "AssemblyAI API не настроен"
            
            return await self.transcribe_with_assemblyai(
                audio_path, message, status_msg, target_language, enable_speakers=True
            )
        
        if self.whisper_service:
            try:
                success, result = await self.whisper_service.transcribe(
                    audio_path=audio_path,
                    language_code=target_language,
                    user_lang=user_lang,
                    get_string_func=get_string,
                    enable_speaker_diarization=False,
                    status_callback=status_msg and self.create_status_callback(user_id, status_msg, target_language) or None
                )
                
                if success:
                    log_request(user_id, "whisper_transcription")
                    logger.info(f"Whisper transcription successful for user {user_id}")
                    return success, result
                else:
                    logger.warning(f"Whisper failed for user {user_id}: {result}")
            except Exception as e:
                logger.error(f"Whisper error for user {user_id}: {e}")
        
        if self.assemblyai_api_key:
            logger.info(f"Using AssemblyAI fallback for user {user_id}")
            return await self.transcribe_with_assemblyai(
                audio_path, message, status_msg, target_language, enable_speakers=False
            )
        
        return False, "Нет доступных сервисов транскрипции"

    async def process_retranscription(self, user_id: str, file_path: str, message, status_msg, 
                                    language_code: str, lang_name: str):
        
        try:
            user_lang = get_user_lang(user_id)
            
            original_transcription = get_state(user_id).get("transcription", "")
            enable_speakers = ("Speaker" in original_transcription or 
                             "Спикер" in original_transcription or 
                             "Mówca" in original_transcription)
            
            success, result = await self.transcribe_audio(
                file_path, message, status_msg, language_code, enable_speakers
            )
            
            if success:
                set_state(user_id, "transcription", result)
                set_state(user_id, "detected_language", language_code)
                
                await status_msg.edit_text(
                    get_string("language_changed_success", user_lang, lang_name=lang_name)
                )
                
                import asyncio
                await asyncio.sleep(1)
                await show_transcription_actions_menu(status_msg, user_id)
            else:
                await status_msg.edit_text(
                    get_string("transcription_error", user_lang, error=result)
                )
            
        except Exception as e:
            logger.error(f"Ошибка в process_retranscription: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await status_msg.edit_text(get_string("error_occurred", user_lang, error=str(e)))