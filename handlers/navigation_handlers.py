# handlers/navigation_handlers.py
import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from strings import get_string
from utils import get_state, set_state, clear_state, get_user_lang
from menus import show_main_menu, show_transcription_actions_menu, create_pagination_keyboard

logger = logging.getLogger(__name__)

class NavigationHandlers:
    def __init__(self, app):
        self.app = app
        self.register_handlers()
    
    def register_handlers(self):
        self.app.on_callback_query(filters.regex(r"^prev_page$"))(self.navigate_pages)
        self.app.on_callback_query(filters.regex(r"^next_page$"))(self.navigate_pages)
        self.app.on_callback_query(filters.regex(r"^prev_gpt_page$"))(self.navigate_gpt_pages)
        self.app.on_callback_query(filters.regex(r"^next_gpt_page$"))(self.navigate_gpt_pages)
        self.app.on_callback_query(filters.regex(r"^page_info$"))(self.page_info)
        self.app.on_callback_query(filters.regex(r"^gpt_page_info$"))(self.gpt_page_info)
        self.app.on_callback_query(filters.regex(r"^back_to_menu$"))(self.back_to_menu)
        self.app.on_callback_query(filters.regex(r"^back_to_transcription_actions$"))(self.back_to_transcription_actions)
        self.app.on_callback_query(filters.regex(r"^cancel_transcription$"))(self.cancel_transcription)

    async def navigate_pages(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            
            action = callback_query.data.split("_")[0]
            
            pages = get_state(user_id).get("pages", [])
            current_page = get_state(user_id).get("current_page", 0)
            total_pages = len(pages)
            
            if not pages:
                await callback_query.answer(get_string("pages_not_found", user_lang))
                return
                
            if action == "prev":
                if current_page > 0:
                    current_page -= 1
                    set_state(user_id, "current_page", current_page)
                else:
                    await callback_query.answer("You are already on the first page")
                    return
            elif action == "next":
                if current_page < total_pages - 1:
                    current_page += 1
                    set_state(user_id, "current_page", current_page)
                else:
                    await callback_query.answer("You are already on the last page")
                    return
                
            keyboard = create_pagination_keyboard(current_page, total_pages, "", "back_to_transcription_actions", user_lang)
            
            await callback_query.message.edit_text(
                get_string("transcription_page_header", user_lang, page=current_page + 1, total=total_pages) + pages[current_page],
                reply_markup=keyboard
            )
            
            await callback_query.answer(f"Page {current_page + 1} of {total_pages}")
        
        except Exception as e:
            logger.error(f"Ошибка при навигации по страницам: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def navigate_gpt_pages(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            
            action = callback_query.data.split("_")[0] 
            
            pages = get_state(user_id).get("gpt_pages", [])
            current_page = get_state(user_id).get("current_gpt_page", 0)
            total_pages = len(pages)
            
            if not pages:
                await callback_query.answer(get_string("pages_not_found", user_lang))
                return
                
            if action == "prev":
                if current_page > 0:
                    current_page -= 1
                    set_state(user_id, "current_gpt_page", current_page)
                else:
                    await callback_query.answer("You are already on the first page")
                    return
            elif action == "next":
                if current_page < total_pages - 1:
                    current_page += 1
                    set_state(user_id, "current_gpt_page", current_page)
                else:
                    await callback_query.answer("You are already on the last page")
                    return
                
            keyboard = create_pagination_keyboard(current_page, total_pages, "gpt", "back_to_transcription_actions", user_lang)
            
            await callback_query.message.edit_text(
                get_string("gpt_result_page_header", user_lang, page=current_page + 1, total=total_pages) + pages[current_page],
                reply_markup=keyboard
            )
            
            await callback_query.answer(f"Page {current_page + 1} of {total_pages}")
        
        except Exception as e:
            logger.error(f"Ошибка при навигации по страницам ChatGPT: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def page_info(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            
            pages = get_state(user_id).get("pages", [])
            current_page = get_state(user_id).get("current_page", 0)
            total_pages = len(pages)
            
            await callback_query.answer(f"Page {current_page + 1} / {total_pages}")
        except Exception as e:
            logger.error(f"Ошибка при показе информации о странице: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def gpt_page_info(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            
            pages = get_state(user_id).get("gpt_pages", [])
            current_page = get_state(user_id).get("current_gpt_page", 0)
            total_pages = len(pages)
            
            await callback_query.answer(f"Page {current_page + 1} / {total_pages}")
        except Exception as e:
            logger.error(f"Ошибка при показе информации о странице: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def back_to_menu(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            clear_state(user_id)
            
            await show_main_menu(client, callback_query.message, user_id)
            await callback_query.answer()
            
        except Exception as e:
            logger.error(f"Ошибка при возврате в меню: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))
            
            await show_main_menu(client, callback_query.message, user_id)

    async def back_to_transcription_actions(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            
            set_state(user_id, "awaiting_custom_prompt", False)
            
            transcription = get_state(user_id).get("transcription")
            if not transcription:
                await callback_query.answer(get_string("transcription_not_found", user_lang))
                return await self.back_to_menu(client, callback_query)
            
            await show_transcription_actions_menu(callback_query.message, user_id)
            await callback_query.answer("Возврат к меню действий")
            
        except Exception as e:
            logger.error(f"Ошибка при возврате к действиям транскрипции: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))

    async def cancel_transcription(self, client, callback_query):
        try:
            user_id = str(callback_query.from_user.id)
            user_lang = get_user_lang(user_id)
            
            clear_state(user_id)
            
            await show_main_menu(client, callback_query.message, user_id)
            
            await callback_query.answer(get_string("transcription_canceled", user_lang))
            
        except Exception as e:
            logger.error(f"Ошибка при отмене транскрипции: {e}", exc_info=True)
            user_lang = get_user_lang(user_id)
            await callback_query.answer(get_string("error_occurred", user_lang, error=str(e)))