#main.py
import os
import asyncio
import signal
import sys
import logging
import aiohttp
import concurrent.futures
from dotenv import load_dotenv
from pyrogram import Client

from services.chatgpt_service import ChatGPTService
from services.whisper_service import create_whisper_service
from services.transcription_service import TranscriptionManager
from handlers.handlers import BotHandlers
from database import init_db, migrate_database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger("assemblyai_bot")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

DB_DIR = os.path.join(os.getcwd(), "db")
CACHE_DIR = os.path.join(os.getcwd(), "cache")
AUDIO_FILES_DIR = os.path.join(CACHE_DIR, "audio_files")
SESSION_DIR = os.path.join(CACHE_DIR, "sessions")

for directory in [DB_DIR, CACHE_DIR, AUDIO_FILES_DIR, SESSION_DIR]:
    os.makedirs(directory, exist_ok=True)

thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=100)
aiohttp_session = None
bot_handlers = None
app = None
cleanup_task = None
shutdown_event = asyncio.Event()

async def clean_cache(directory, all_files=False):
    try:
        if not os.path.exists(directory):
            return
            
        import time
        current_time = time.time()
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if all_files:
                os.remove(filepath)
                logger.info(f"Удален файл: {filename}")
            else:
                if os.path.getmtime(filepath) < current_time - 3600:
                    os.remove(filepath)
                    logger.info(f"Удален старый файл: {filename}")
                    
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")

async def cleanup_resources(session):
    try:
        if session and not session.closed:
            await session.close()
            logger.info("HTTP сессия закрыта")
    except Exception as e:
        logger.error(f"Ошибка закрытия HTTP сессии: {e}")

async def setup_services():
    global aiohttp_session
    aiohttp_session = aiohttp.ClientSession()
    chatgpt_service = None
    if OPENAI_API_KEY:
        chatgpt_service = ChatGPTService(
            api_key=OPENAI_API_KEY,
            model="gpt-4o-mini"
        )

    logger.info(f"Loading Whisper model '{WHISPER_MODEL}' into memory...")
    loop = asyncio.get_event_loop()
    whisper_service = await loop.run_in_executor(
        None,
        create_whisper_service,
        WHISPER_MODEL
    )
    logger.info(f"Whisper model '{WHISPER_MODEL}' ready in memory")

    transcription_manager = TranscriptionManager(
        assemblyai_api_key=ASSEMBLYAI_API_KEY,
        whisper_service=whisper_service
    )
    return chatgpt_service, transcription_manager

async def scheduled_cleanup():
    try:
        while not shutdown_event.is_set():
            await clean_cache(AUDIO_FILES_DIR)
            
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=3600)
                break
            except asyncio.TimeoutError:
                continue
                
    except Exception as e:
        logger.error(f"Ошибка в задаче очистки: {e}")

def signal_handler(sig, frame):
    print(f"\nПолучен сигнал {sig}, завершение работы...")
    shutdown_event.set()
    
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(graceful_shutdown())
    except RuntimeError:
        asyncio.run(graceful_shutdown())

async def graceful_shutdown():
    global app, cleanup_task, aiohttp_session, thread_pool
    
    logger.info("Начинаем корректное завершение...")
    
    try:
        if cleanup_task and not cleanup_task.done():
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
        
        await clean_cache(AUDIO_FILES_DIR, all_files=True)
        await cleanup_resources(aiohttp_session)
        
        if thread_pool:
            thread_pool.shutdown(wait=False)
        
        if app and app.is_connected:
            await app.stop()
            logger.info("Pyrogram клиент остановлен")
        
        logger.info("Корректное завершение завершено")
        
    except Exception as e:
        logger.error(f"Ошибка при корректном завершении: {e}")
    finally:
        os._exit(0)

async def initialize_bot():
    global bot_handlers
    
    try:
        chatgpt_service, transcription_manager = await setup_services()
        
        bot_handlers = BotHandlers(
            app=app,
            chatgpt_service=chatgpt_service,
            transcription_manager=transcription_manager,
            audio_files_dir=AUDIO_FILES_DIR
        )
        
        cleanup_task = asyncio.create_task(scheduled_cleanup())
        
        logger.info("Все сервисы инициализированы успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise

def main():
    global app
    
    required_vars = ["API_ID", "API_HASH", "BOT_TOKEN", "ASSEMBLYAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Отсутствуют переменные окружения: {missing_vars}")
        sys.exit(1)
    
    try:
        print("Запуск бота...")
        
        init_db()
        migrate_database()
        
        app = Client(
            "assemblyai_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workdir=SESSION_DIR,
        )
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("Бот запущен и готов к работе")
        logger.info("Бот запущен")
        
        async def setup():
            await initialize_bot()
        
        asyncio.get_event_loop().run_until_complete(setup())
        app.run()
        
    except KeyboardInterrupt:
        print("\nПолучено прерывание с клавиатуры...")
        shutdown_event.set()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        print("Завершение работы бота...")
        
        try:
            asyncio.run(graceful_shutdown())
        except Exception as e:
            logger.error(f"Ошибка при финальном завершении: {e}")

if __name__ == "__main__":
    main()