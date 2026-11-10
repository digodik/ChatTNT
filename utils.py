# utils.py
import os
import time
import logging
import shutil
from typing import Dict, Any
from database import get_user_language

logger = logging.getLogger(__name__)

user_states = {}

def get_state(user_id: str) -> Dict[str, Any]:
    if user_id not in user_states:
        user_states[user_id] = {}
    return user_states[user_id]

def set_state(user_id: str, key: str, value: Any) -> None:
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id][key] = value

def clear_state(user_id: str, key: str = None) -> None:
    if user_id in user_states:
        if key and key in user_states[user_id]:
            del user_states[user_id][key]
        else:
            user_states[user_id] = {}

def get_user_lang(user_id: str) -> str:
    lang = get_state(user_id).get("language")
    if not lang:
        lang = get_user_language(user_id)
        if lang:
            set_state(user_id, "language", lang)
        else:
            lang = "en"
    return lang

async def clean_cache(audio_files_dir: str, all_files=False, age_threshold=24*60*60):
    try:
        now = time.time()
        for filename in os.listdir(audio_files_dir):
            file_path = os.path.join(audio_files_dir, filename)
            if os.path.isfile(file_path):
                if all_files or (now - os.path.getmtime(file_path) > age_threshold):
                    os.remove(file_path)
                    logger.info(f"Удален файл: {file_path}")
            elif os.path.isdir(file_path) and all_files:
                shutil.rmtree(file_path)
        
        if all_files:
            for user_id in user_states:
                if "original_file_path" in user_states[user_id]:
                    del user_states[user_id]["original_file_path"]
            logger.info("Кэш полностью очищен")
        else:
            for user_id in list(user_states.keys()):
                if "original_file_path" in user_states[user_id]:
                    file_path = user_states[user_id]["original_file_path"]
                    if not os.path.exists(file_path):
                        del user_states[user_id]["original_file_path"]
            logger.info("Старые файлы удалены")
    except Exception as e:
        logger.error(f"Ошибка при очистке файлов: {e}")

async def cleanup_resources(aiohttp_session=None):
    logger.info("Закрытие ресурсов...")
    
    if aiohttp_session is not None:
        await aiohttp_session.close()
        logger.info("aiohttp сессия закрыта")
    
    logger.info("Ресурсы успешно закрыты")