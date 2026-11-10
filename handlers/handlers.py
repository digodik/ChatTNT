# handlers/handlers.py
import logging
from handlers.command_handlers import CommandHandlers
from handlers.media_handlers import MediaHandlers
from handlers.callback_handlers import CallbackHandlers
from handlers.navigation_handlers import NavigationHandlers

logger = logging.getLogger(__name__)

class BotHandlers:
    
    def __init__(self, app, chatgpt_service, transcription_manager, audio_files_dir):
        self.app = app
        self.chatgpt_service = chatgpt_service
        self.transcription_manager = transcription_manager
        self.audio_files_dir = audio_files_dir
        
        self.command_handlers = CommandHandlers(app)
        self.media_handlers = MediaHandlers(app, transcription_manager, audio_files_dir, chatgpt_service)
        self.callback_handlers = CallbackHandlers(app, chatgpt_service, transcription_manager)
        self.navigation_handlers = NavigationHandlers(app)
        
        logger.info("Все обработчики зарегистрированы")