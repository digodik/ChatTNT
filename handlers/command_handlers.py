# handlers/command_handlers.py
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user_language
from strings import AVAILABLE_LANGUAGES
from utils import get_user_lang
from menus import show_main_menu, show_help_menu
from pyrogram import filters
logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, app):
        self.app = app
        self.register_handlers()
    
    def register_handlers(self):
        self.app.on_message(filters.command("start"))(self.start_command)
        self.app.on_message(filters.command("help"))(self.help_command)

    async def start_command(self, client, message):
        user_id = str(message.from_user.id)
        
        user_lang = get_user_language(user_id)
        if not user_lang:
            keyboard = []
            for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
                keyboard.append([
                    InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
                ])
            
            await message.reply(
                "🌐 Choose your interface language / Выберите язык интерфейса / Wybierz język interfejsu:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await show_main_menu(client, message, user_id)

    async def help_command(self, client, message):
        user_id = str(message.from_user.id)
        user_lang = get_user_lang(user_id)
        
        keyboard, message_text = await show_help_menu(message, user_id)
        await message.reply(message_text)