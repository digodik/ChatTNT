# handlers/callback_handlers.py
import os
import asyncio
import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    get_predefined_prompts, get_recent_custom_prompts, update_prompt_usage,
    set_user_language, update_user_stats, log_request
)
from strings import ASSEMBLYAI_LANGUAGES, get_string
from utils import get_state, set_state, clear_state, get_user_lang
from menus import (
    show_main_menu, show_transcription_actions_menu, show_language_selection_menu,
    show_interface_language_menu, create_pagination_keyboard, show_help_menu
)
from services.chatgpt_service import ChatGPTService
from services.transcription_service import TranscriptionManager

logger = logging.getLogger(__name__)

class CallbackHandlers:
    def __init__(self, app, chatgpt_service: ChatGPTService, transcription_manager: TranscriptionManager):
        self.app = app
        self.chatgpt_service = chatgpt_service
        self.transcription_manager = transcription_manager
        self.register_handlers()
    
    def register_handlers(self):
        self.app.on_callback_query(filters.regex(r"^show_transcription$"))(self.show_transcription)
        self.app.on_callback_query(filters.regex(r"^transcribe_with_speakers$"))(self.transcribe_with_speakers)
        self.app.on_callback_query(filters.regex(r"^quick_prompt_(\d+)$"))(self.handle_quick_prompt)
        self.app.on_callback_query(filters.regex(r"^recent_prompt_(\d+)$"))(self.handle_recent_prompt)
        self.app.on_callback_query(filters.regex(r"^change_detected_language$"))(self.change_detected_language)
        self.app.on_callback_query(filters.regex(r"^retranscribe_(.+)$"))(self.retranscribe_with_language)
        self.app.on_callback_query(filters.regex(r"^change_language$"))(self.change_language)
        self.app.on_callback_query(filters.regex(r"^lang_(.+)$"))(self.handle_language_selection)
        self.app.on_callback_query(filters.regex(r"^show_help$"))(self.show_help)

    async def show_transcription(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            
            transcription = get_state(user_id).get("transcription")
            if not transcription:
                await callback_query.answer(get_string("transcription_not_found", user_lang))
                return
            
            page_size = 3000
            pages = [transcription[i:i+page_size] for i in range(0, len(transcription), page_size)]
            total_pages = len(pages)
            
            set_state(user_id, "pages", pages)
            set_state(user_id, "current_page", 0)
            
            keyboard = create_pagination_keyboard(0, total_pages, "", "back_to_transcription_actions", user_lang)
            
            if total_pages > 1:
                message_text = get_string("transcription_page_header", user_lang, page=1, total=total_pages) + pages[0]
            else:
                message_text = pages[0]
            
            await callback_query.message.edit_text(message_text, reply_markup=keyboard)
            await callback_query.answer(get_string("show_transcription_button", user_lang))
            
        except Exception as e:
            logger.error(f"Ошибка при показе транскрипции: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def transcribe_with_speakers(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            
            original_file_path = get_state(user_id).get("original_file_path")
            if not original_file_path or not os.path.exists(original_file_path):
                await callback_query.answer("Original file not found", show_alert=True)
                return
            
            status_msg = await callback_query.message.edit_text(
                "🎭 Starting transcription with speaker separation...",
                reply_markup=None
            )
            
            success, result = await self.transcription_manager.transcribe_audio(
                original_file_path, callback_query.message, status_msg, None, enable_speakers=True
            )
            
            if success:
                set_state(user_id, "transcription", result)
                await show_transcription_actions_menu(status_msg, user_id)
            else:
                user_lang = get_user_lang(user_id)
                await status_msg.edit_text(get_string("transcription_error", user_lang, error=result))
            
            await callback_query.answer("Speaker separation completed")
            
        except Exception as e:
            logger.error(f"Error in speaker transcription: {e}", exc_info=True)
            await callback_query.answer(f"Error: {str(e)}")

    async def handle_quick_prompt(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            prompt_index = int(callback_query.data.split("_")[-1])
            
            predefined_prompts = get_predefined_prompts(user_id)
            
            if 0 <= prompt_index < len(predefined_prompts):
                selected_prompt = predefined_prompts[prompt_index]
                
                update_prompt_usage(user_id, selected_prompt)
                
                transcription = get_state(user_id).get("transcription")
                if not transcription:
                    await callback_query.answer(get_string("transcription_not_found", user_lang))
                    return
                
                status_msg = await callback_query.message.edit_text(
                    get_string("processing_with_prompt", user_lang, prompt=selected_prompt[:50] + "..."),
                    reply_markup=None
                )
                
                asyncio.create_task(self._process_gpt_background(user_id, transcription, selected_prompt, callback_query.message, status_msg))
                
                await callback_query.answer(f"Выбран: {selected_prompt[:30]}...")
            else:
                await callback_query.answer("Промпт не найден")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке быстрого промпта: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def handle_recent_prompt(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            prompt_index = int(callback_query.data.split("_")[-1])
            
            recent_prompts = get_recent_custom_prompts(user_id, 5)
            
            if 0 <= prompt_index < len(recent_prompts):
                selected_prompt = recent_prompts[prompt_index]
                
                update_prompt_usage(user_id, selected_prompt)
                
                transcription = get_state(user_id).get("transcription")
                if not transcription:
                    await callback_query.answer(get_string("transcription_not_found", user_lang))
                    return
                
                status_msg = await callback_query.message.edit_text(
                    get_string("processing_with_prompt", user_lang, prompt=selected_prompt[:50] + "..."),
                    reply_markup=None
                )
                
                asyncio.create_task(self._process_gpt_background(user_id, transcription, selected_prompt, callback_query.message, status_msg))
                
                await callback_query.answer(f"Выбран: {selected_prompt[:30]}...")
            else:
                await callback_query.answer("Промпт не найден")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке недавнего промпта: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def change_detected_language(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            detected_language = get_state(user_id).get("detected_language", "unknown")
            
            keyboard, message_text = await show_language_selection_menu(callback_query.message, user_id, detected_language)
            
            await callback_query.message.edit_text(
                message_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            await callback_query.answer()
            
        except Exception as e:
            logger.error(f"Ошибка при смене определённого языка: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def retranscribe_with_language(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            language_code = callback_query.data.split("_", 1)[1]
            
            original_file_path = get_state(user_id).get("original_file_path")
            if not original_file_path or not os.path.exists(original_file_path):
                await callback_query.answer(get_string("original_file_not_found", user_lang), show_alert=True)
                return
            
            lang_name = ASSEMBLYAI_LANGUAGES.get(language_code, language_code)
            
            status_msg = await callback_query.message.edit_text(
                get_string("retranscribing_with_language", user_lang, lang_name=lang_name),
                reply_markup=None
            )
            
            asyncio.create_task(
                self.transcription_manager.process_retranscription(user_id, original_file_path, callback_query.message, status_msg, language_code, lang_name)
            )
            
            await callback_query.answer(f"Перезапуск с языком: {lang_name}")
            
        except Exception as e:
            logger.error(f"Ошибка при повторной транскрипции: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def change_language(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            
            keyboard, message_text = await show_interface_language_menu(callback_query.message, user_id)
            
            await callback_query.message.edit_text(
                message_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            await callback_query.answer()
            
        except Exception as e:
            logger.error(f"Ошибка при смене языка: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def handle_language_selection(self, client, callback_query):
        try:
            language_code = callback_query.data.split("_")[1]
            user_id = str(callback_query.from_user.id)
            
            set_state(user_id, "language", language_code)
            set_user_language(user_id, language_code)
            
            await callback_query.answer(get_string("language_changed", language_code))
            
            await show_main_menu(client, callback_query.message, user_id)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора языка: {e}", exc_info=True)
            await callback_query.answer("Language selection error")

    async def show_help(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            
            keyboard, message_text = await show_help_menu(callback_query.message, user_id)
            
            await callback_query.message.edit_text(
                message_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await callback_query.answer()
        except Exception as e:
            logger.error(f"Error showing help: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

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