# menus.py
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_user_lang, get_state
from database import get_predefined_prompts, get_recent_custom_prompts
from strings import ASSEMBLYAI_LANGUAGES, AVAILABLE_LANGUAGES, get_string, get_supported_languages_list

logger = logging.getLogger(__name__)

async def show_main_menu(client, message, user_id):
    user_lang = get_user_lang(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_string("help_button", user_lang), callback_data="show_help")],
        [InlineKeyboardButton(get_string("change_language_button", user_lang), callback_data="change_language")]
    ]
    
    try:
        await message.edit_text(
            get_string("welcome_message", user_lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        await message.reply(
            get_string("welcome_message", user_lang),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_transcription_actions_menu(message, user_id):
    user_lang = get_user_lang(user_id)
    
    detected_language = get_state(user_id).get("detected_language", "unknown")
    detected_lang_name = ASSEMBLYAI_LANGUAGES.get(detected_language, detected_language)
    
    predefined_prompts = get_predefined_prompts(user_id)
    recent_custom = get_recent_custom_prompts(user_id, 2)
    
    keyboard = []
    
    if detected_language and detected_language != "unknown":
        keyboard.append([
            InlineKeyboardButton(
                get_string("change_detected_language_button", user_lang), 
                callback_data="change_detected_language"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton(get_string("show_transcription_button", user_lang), callback_data="show_transcription")],
        [InlineKeyboardButton(get_string("transcribe_with_speakers_button", user_lang), callback_data="transcribe_with_speakers")]
    ])
    
    prompt_buttons = []
    for i, prompt in enumerate(predefined_prompts[:4]):
        if i == 0:
            button_text = get_string("quick_summary", user_lang)
        elif i == 1:
            button_text = get_string("fix_grammar", user_lang)
        elif i == 2:
            button_text = get_string("prepare_email", user_lang)
        elif i == 3:
            button_text = get_string("convert_to_notes", user_lang)
        else:
            button_text = prompt[:20] + "..." if len(prompt) > 20 else prompt
        
        prompt_buttons.append(
            InlineKeyboardButton(button_text, callback_data=f"quick_prompt_{i}")
        )
    
    for i in range(0, len(prompt_buttons), 2):
        row = prompt_buttons[i:i+2]
        keyboard.append(row)
    
    for i, prompt in enumerate(recent_custom):
        short_prompt = prompt[:30] + "..." if len(prompt) > 30 else prompt
        keyboard.append([
            InlineKeyboardButton(f"💡 {short_prompt}", callback_data=f"recent_prompt_{i}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(get_string("main_menu_button", user_lang), callback_data="back_to_menu")
    ])
    
    message_text = get_string("awaiting_custom_request", user_lang)
    if detected_language and detected_language != "unknown":
        language_info = get_string("language_detection_info", user_lang, detected_lang=detected_lang_name)
        message_text = language_info + "\n\n" + message_text
    
    try:
        await message.edit_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception:
        await message.reply(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_language_selection_menu(message, user_id, current_detected_lang=None):
    user_lang = get_user_lang(user_id)
    
    detected_lang_name = ASSEMBLYAI_LANGUAGES.get(current_detected_lang, current_detected_lang) if current_detected_lang else "unknown"
    
    keyboard = []
    
    popular_languages = ["en", "ru", "pl", "es", "fr", "de", "it", "pt"]
    other_languages = [lang for lang in ASSEMBLYAI_LANGUAGES.keys() if lang not in popular_languages]
    
    for lang_code in popular_languages:
        if lang_code in ASSEMBLYAI_LANGUAGES:
            lang_name = ASSEMBLYAI_LANGUAGES[lang_code]
            if lang_code == current_detected_lang:
                button_text = f"✅ {lang_name}"
            else:
                button_text = lang_name
            
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f"retranscribe_{lang_code}")
            ])
    
    for i in range(0, len(other_languages), 2):
        row = []
        for j in range(2):
            if i + j < len(other_languages):
                lang_code = other_languages[i + j]
                lang_name = ASSEMBLYAI_LANGUAGES[lang_code]
                if lang_code == current_detected_lang:
                    button_text = f"✅ {lang_name}"
                else:
                    button_text = lang_name
                
                row.append(InlineKeyboardButton(button_text, callback_data=f"retranscribe_{lang_code}"))
        
        if row:
            keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton(get_string("back_button", user_lang), callback_data="back_to_transcription_actions")
    ])
    
    message_text = get_string("select_correct_language", user_lang, current_lang=detected_lang_name)
    
    return keyboard, message_text

async def show_interface_language_menu(message, user_id):
    user_lang = get_user_lang(user_id)
    
    keyboard = []
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        if lang_code == user_lang:
            button_text = f"✅ {lang_name}"
        else:
            button_text = lang_name
        
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"lang_{lang_code}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(get_string("back_button", user_lang), callback_data="back_to_menu")
    ])
    
    message_text = get_string("language_selection", user_lang)
    
    return keyboard, message_text

def create_pagination_keyboard(current_page: int, total_pages: int, prefix: str, back_callback: str, user_lang: str):
    keyboard = []
    
    if total_pages > 1:
        nav_buttons = []
        
        if prefix == "gpt":
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data="prev_gpt_page"))
            nav_buttons.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="gpt_page_info"))
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data="next_gpt_page"))
        else:
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data="prev_page"))
            nav_buttons.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="page_info"))
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data="next_page"))
            
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton(get_string("back_button", user_lang), callback_data=back_callback)])
    
    return InlineKeyboardMarkup(keyboard)

async def show_help_menu(message, user_id):
    user_lang = get_user_lang(user_id)
    
    languages_list = get_supported_languages_list(user_lang)
    
    keyboard = [
        [InlineKeyboardButton(get_string("back_button", user_lang), callback_data="back_to_menu")]
    ]
    
    message_text = get_string("help_content", user_lang, languages_list=languages_list)
    
    return keyboard, message_text