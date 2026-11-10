# handlers/media_handlers.py
import os
import asyncio
import time
import logging
from typing import Tuple
from pyrogram import filters
from pyrogram.types import Message
from database import update_user_stats, add_custom_prompt, log_request
from strings import get_string
from utils import get_state, set_state, clear_state, get_user_lang
from menus import show_transcription_actions_menu, create_pagination_keyboard
from services.transcription_service import TranscriptionManager
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class MediaHandlers:
    def __init__(self, app, transcription_manager: TranscriptionManager, audio_files_dir: str, chatgpt_service=None):
        self.app = app
        self.transcription_manager = transcription_manager
        self.audio_files_dir = audio_files_dir
        self.chatgpt_service = chatgpt_service
        self.register_handlers()
    
    def register_handlers(self):
        self.app.on_message(filters.audio | filters.voice | filters.document | filters.video | filters.video_note)(self.handle_audio)
        self.app.on_message(filters.text)(self.handle_text)

    async def handle_audio(self, client, message):
        try:
            user_id = str(message.from_user.id)
            user_lang = get_user_lang(user_id)

            update_user_stats(
                user_id=user_id,
                username=message.from_user.username or message.from_user.first_name or f"User_{user_id}",
                transcription=True
            )
            
            old_file_path = get_state(user_id).get("original_file_path")
            if old_file_path and os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    logger.info(f"Удален старый файл пользователя {user_id}: {old_file_path}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить старый файл {old_file_path}: {e}")
            
            clear_state(user_id)
                
            if message.document and not message.document.mime_type.startswith("audio/") and not message.document.mime_type.startswith("video/"):
                file_ext = os.path.splitext(message.document.file_name)[1].lower() if message.document.file_name else ""
                if file_ext not in [".mp3", ".ogg", ".wav", ".flac", ".m4a", ".aac", ".mp4", ".mov", ".avi", ".mkv", ".webm"]:
                    await message.reply(get_string("not_audio_file", user_lang))
                    return
            
            if get_state(user_id).get("transcribing", False):
                await message.reply(get_string("transcription_in_progress", user_lang))
                return
            
            set_state(user_id, "transcribing", True)
            
            file_id, file_name = self._get_file_info(message)
            if not file_id:
                await message.reply(get_string("please_send_audio", user_lang))
                set_state(user_id, "transcribing", False)
                return
            
            file_name = f"{int(time.time())}_{file_name}"
            save_path = os.path.join(self.audio_files_dir, file_name)
            
            success, result = await self._download_file(message, file_id, save_path)
                    
            if success:
                set_state(user_id, "file_path", save_path)

                status_msg = get_state(user_id).get("status_message")
                asyncio.create_task(self._process_transcription(user_id, save_path, message, status_msg))
            else:
                await message.reply(get_string("error_occurred", user_lang, error=result))
                set_state(user_id, "transcribing", False)
        
        except Exception as e:
            logger.error(f"Ошибка обработки аудиофайла: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await message.reply(get_string("error_occurred", user_lang, error=str(e)))
            set_state(user_id, "transcribing", False)

    async def handle_text(self, client, message):
        if message.text.startswith('/'):
            return
        
        user_id = str(message.from_user.id)
        user_lang = get_user_lang(user_id)
        transcription = get_state(user_id).get("transcription")
        if transcription:
            custom_prompt = message.text
            add_custom_prompt(user_id, custom_prompt)
            status_msg = await message.reply(
                get_string("processing_with_prompt", user_lang, prompt=custom_prompt[:50] + "...")
            )
            asyncio.create_task(self._process_gpt_background(user_id, transcription, custom_prompt, message, status_msg))
            return
        
        await message.reply(get_string("please_send_audio_or_use_help", user_lang))

    def _get_file_info(self, message) -> Tuple[str, str]:
        if message.audio:
            return message.audio.file_id, message.audio.file_name or f"audio_{message.id}.mp3"
        elif message.voice:
            return message.voice.file_id, f"voice_{message.id}.ogg"
        elif message.video:
            return message.video.file_id, f"video_{message.id}.mp4"
        elif message.video_note:
            return message.video_note.file_id, f"video_note_{message.id}.mp4"
        elif message.document:
            return message.document.file_id, message.document.file_name or f"document_{message.id}"
        return None, None

    async def _download_file(self, message: Message, file_id: str, save_path: str) -> Tuple[bool, str]:
        try:
            user_id = str(message.from_user.id)
            user_lang = get_user_lang(user_id)

            status_msg = await message.reply(get_string("processing_file", user_lang))
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            await self.app.download_media(message=file_id, file_name=save_path)

            if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
                await status_msg.edit_text(get_string("file_download_error", user_lang))
                return False, get_string("file_download_error", user_lang)

            set_state(user_id, "status_message", status_msg)

            return True, save_path

        except Exception as e:
            logger.error(f"Ошибка при скачивании файла: {e}", exc_info=True)
            try:
                await status_msg.edit_text(f"{get_string('error_occurred', user_lang, error=str(e))}")
            except:
                await message.reply(f"{get_string('error_occurred', user_lang, error=str(e))}")
            return False, str(e)

    async def _process_transcription(self, user_id: str, file_path: str, message, status_msg, target_language: str = None):
        try:
            user_lang = get_user_lang(user_id)

            set_state(user_id, "original_file_path", file_path)

            lang_code = None if target_language == "auto" else target_language

            success, result = await self.transcription_manager.transcribe_audio(
                file_path, message, None, lang_code, enable_speakers=False
            )

            if success:
                set_state(user_id, "transcription", result)
                await show_transcription_actions_menu(status_msg, user_id)
            else:
                await status_msg.edit_text(get_string("transcription_error", user_lang, error=result))

        except Exception as e:
            logger.error(f"Error in process_transcription: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await status_msg.edit_text(get_string("error_occurred", user_lang, error=str(e)))
        finally:
            set_state(user_id, "transcribing", False)

    async def _process_gpt_background(self, user_id, transcription, prompt, message, status_msg):
        try:
            user_lang = get_user_lang(user_id)

            success, response = await self._process_with_chatgpt(transcription, prompt, message)

            if success:
                log_request(user_id, "chatgpt_request")
                update_user_stats(user_id, gpt_request=True)

            await status_msg.edit_text(get_string("gpt_processing_completed", user_lang))

            if not success:
                await message.reply(
                    f"❌ {response}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_string("back_button", user_lang), callback_data="back_to_transcription_actions")]
                    ])
                )
                return

            page_size = 3000
            pages = [response[i:i+page_size] for i in range(0, len(response), page_size)]
            total_pages = len(pages)

            set_state(user_id, "gpt_pages", pages)
            set_state(user_id, "current_gpt_page", 0)

            keyboard = create_pagination_keyboard(0, total_pages, "gpt", "back_to_transcription_actions", user_lang)

            if total_pages > 1:
                message_text = get_string("gpt_result_page_header", user_lang, page=1, total=total_pages) + pages[0]
            else:
                message_text = pages[0]

            await message.reply(
                message_text,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Ошибка при обработке текста через ChatGPT: {e}", exc_info=True)
            try:
                await status_msg.edit_text(
                    get_string("error_occurred", user_lang, error=str(e)),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(get_string("back_button", user_lang), callback_data="back_to_transcription_actions")]
                    ])
                )
            except Exception:
                pass

    async def _process_with_chatgpt(self, text, prompt, message):
        if not self.chatgpt_service:
            user_lang = get_user_lang(str(message.from_user.id))
            return False, get_string("chatgpt_api_not_configured", user_lang)

        try:
            success, result = await self.chatgpt_service.summarize(
                text=text,
                prompt=prompt
            )
            return success, result
        except Exception as e:
            user_lang = get_user_lang(str(message.from_user.id))
            logger.error(f"Ошибка при вызове ChatGPT API: {e}", exc_info=True)
            return False, get_string("error_occurred", user_lang, error=str(e))