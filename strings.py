#strings.py
AVAILABLE_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "pl": "Polski",
}

ASSEMBLYAI_LANGUAGES = {
    "en": "English",
    "ru": "Russian", 
    "pl": "Polish",
}

STRINGS = {
    "language_selection": {
        "ru": "Выберите язык интерфейса:",
        "en": "Choose your language:",
        "pl": "Wybierz język interfejsu:",
    },
    "language_changed": {
        "ru": "✅ Язык изменен на Русский",
        "en": "✅ Language changed to English",
        "pl": "✅ Język zmieniony na Polski",
    },
    
    "welcome_message": {
        "ru": "👋 Привет! Я бот для транскрипции аудио с возможностью обработки результата через ChatGPT.\n\n"
              "📱 **Что я умею:**\n"
              "• Автоматически определять язык аудио\n"
              "• Переводить текст на разные языки\n"
              "• Обрабатывать полученный текст через ChatGPT\n\n"
              "🎧 Отправьте мне голосовое сообщение или аудиофайл, чтобы начать.\n\n"
              "🌐 Больше о нас: https://github.com/digodik",
        "en": "👋 Hello! I'm a bot for audio transcription with the ability to process the result through ChatGPT.\n\n"
              "📱 **What I can do:**\n"
              "• Automatically detect audio language\n"
              "• Translate text to different languages\n"
              "• Process the resulting text through ChatGPT\n\n"
              "🎧 Send me a voice message or audio file to start.\n\n"
              "🌐 More about us: https://github.com/digodik",
        "pl": "👋 Cześć! Jestem botem do transkrypcji audio z możliwością przetwarzania wyniku przez ChatGPT.\n\n"
              "📱 **Co potrafię:**\n"
              "• Automatycznie wykrywać język audio\n"
              "• Tłumaczyć tekst na różne języki\n"
              "• Przetwarzać otrzymany tekst przez ChatGPT\n\n"
              "🎧 Wyślij mi wiadomość głosową lub plik audio, aby rozpocząć.\n\n"
              "🌐 Więcej o nas: https://github.com/digodik",
    },
    
    "help_button": {
        "ru": "❓ Помощь",
        "en": "❓ Help",
        "pl": "❓ Pomoc",
    },
    
    "change_language_button": {
        "ru": "🌐 Изменить язык",
        "en": "🌐 Change language",
        "pl": "🌐 Zmień język",
    },
    
    "help_content": {
        "ru": "📋 **Как пользоваться этим ботом:**\n\n"
              "1. Отправьте голосовое сообщение или аудиофайл (MP3, OGG, WAV и др.)\n"
              "2. Выберите язык для транскрипции\n"
              "3. После обработки вы сможете:\n"
              "   - Просто получить текст транскрипции\n"
              "   - Отправить текст в ChatGPT с готовыми или своими промптами\n\n"
              "**Команды бота:**\n"
              "/start - начать работу с ботом\n"
              "/help - показать эту справку\n\n"
              "**Поддерживаемые языки для транскрипции:**\n"
              "{languages_list}",
        "en": "📋 **How to use this bot:**\n\n"
              "1. Send a voice message or audio file (MP3, OGG, WAV, etc.)\n"
              "2. Select the language for transcription\n"
              "3. After processing, you can:\n"
              "   - Simply get the transcription text\n"
              "   - Send the text to ChatGPT with ready-made or custom prompts\n\n"
              "**Bot commands:**\n"
              "/start - start working with the bot\n"
              "/help - show this help\n\n"
              "**Supported languages for transcription:**\n"
              "{languages_list}",
        "pl": "📋 **Jak korzystać z tego bota:**\n\n"
              "1. Wyślij wiadomość głosową lub plik audio (MP3, OGG, WAV, itp.)\n"
              "2. Wybierz język do transkrypcji\n"
              "3. Po przetworzeniu możesz:\n"
              "   - Po prostu otrzymać tekst transkrypcji\n"
              "   - Wysłać tekst do ChatGPT z gotowymi lub własnymi promptami\n\n"
              "**Komendy bota:**\n"
              "/start - rozpocznij pracę z botem\n"
              "/help - pokaż tę pomoc\n\n"
              "**Obsługiwane języki do transkrypcji:**\n"
              "{languages_list}",
    },
    
    "back_button": {
        "ru": "🔙 Назад",
        "en": "🔙 Back",
        "pl": "🔙 Powrót",
    },
    
    "processing_file": {
        "ru": "⏳ Обрабатываю файл...",
        "en": "⏳ Processing file...",
        "pl": "⏳ Przetwarzanie pliku...",
    },
    
    "file_download_error": {
        "ru": "❌ Ошибка: файл не скачался или пустой",
        "en": "❌ Error: file didn't download or is empty",
        "pl": "❌ Błąd: plik nie został pobrany lub jest pusty",
    },
    
    "file_uploaded": {
        "ru": "✅ Файл успешно обработан. Выберите язык для транскрипции:",
        "en": "✅ File successfully processed. Select language for transcription:",
        "pl": "✅ Plik został pomyślnie przesłany. Wybierz język do transkrypcji:",
    },
    
    "select_transcription_language": {
        "ru": "Выберите язык для транскрипции:",
        "en": "Select language for transcription:",
        "pl": "Wybierz język do transkrypcji:",
    },
    
    "cancel_button": {
        "ru": "🔙 Отмена",
        "en": "🔙 Cancel",
        "pl": "🔙 Anuluj",
    },
    
    "processing_audio": {
        "ru": "🔄 Обработка файла...",
        "en": "🔄 Processing file...",
        "pl": "🔄 Przetwarzanie pliku...",
    },
    
    "starting_transcription": {
        "ru": "⏳ Файл обработан. Начинаю транскрипцию на {lang_name}...",
        "en": "⏳ File processed. Starting transcription in {lang_name}...",
        "pl": "⏳ Plik przetworzony. Rozpoczynam transkrypcję w języku {lang_name}...",
    },
    
    "transcribing_status": {
        "ru": "⏳ Транскрибирую аудио... ({elapsed_time:.0f}с)",
        "en": "⏳ Transcribing audio... ({elapsed_time:.0f}s)",
        "pl": "⏳ Transkrybuję audio... ({elapsed_time:.0f}s)",
    },
    
    "transcription_completed": {
        "ru": "✅ Транскрипция завершена!\n👂 Исходный язык аудио: {detected_lang}",
        "en": "✅ Transcription completed!\n👂 Original audio language: {detected_lang}",
        "pl": "✅ Transkrypcja zakończona!\n👂 Oryginalny język audio: {detected_lang}",
    },
    
    "transcription_error": {
        "ru": "❌ Ошибка при транскрипции: {error}",
        "en": "❌ Error during transcription: {error}",
        "pl": "❌ Błąd podczas transkrypcji: {error}",
    },
    
    "transcription_actions_menu": {
        "ru": "✅ Выберите действие с полученным текстом:",
        "en": "✅ Choose an action with the resulting text:",
        "pl": "✅ Wybierz działanie z otrzymanym tekstem:",
    },
    
    "show_transcription_button": {
        "ru": "📝 Показать транскрипцию",
        "en": "📝 Show transcription",
        "pl": "📝 Pokaż transkrypcję",
    },
    
    "quick_summary": {
        "ru": "📋 Краткий пересказ",
        "en": "📋 Quick Summary",
        "pl": "📋 Szybkie podsumowanie",
    },
    
    "extract_tasks": {
        "ru": "📝 Извлечь задачи",
        "en": "📝 Extract Tasks",
        "pl": "📝 Wyodrębnij zadania",
    },
    
    "structured_notes": {
        "ru": "📚 Структурированный конспект",
        "en": "📚 Structured Notes",
        "pl": "📚 Uporządkowany konspekt",
    },
    
    "key_facts": {
        "ru": "🔢 Ключевые факты",
        "en": "🔢 Key Facts",
        "pl": "🔢 Kluczowe fakty",
    },
    
    "custom_prompt_button": {
        "ru": "✏️ Другой запрос",
        "en": "✏️ Custom Request",
        "pl": "✏️ Inne żądanie",
    },
    
    "main_menu_button": {
        "ru": "🔙 В главное меню",
        "en": "🔙 To main menu",
        "pl": "🔙 Do menu głównego",
    },
    
    "enter_custom_prompt": {
        "ru": "📝 **Введите ваш запрос**\n\n"
              "Опишите, как именно вы хотите обработать текст транскрипции.\n\n"
              "Примеры:\n"
              "• Переведи на английский язык\n"
              "• Найди все упоминания дат и событий\n"
              "• Создай список вопросов по тексту",
        "en": "📝 **Enter your request**\n\n"
              "Describe exactly how you want to process the transcription text.\n\n"
              "Examples:\n"
              "• Translate to French\n"
              "• Find all mentions of dates and events\n"
              "• Create a list of questions about the text",
        "pl": "📝 **Wprowadź swoje żądanie**\n\n"
              "Opisz dokładnie, jak chcesz przetworzyć tekst transkrypcji.\n\n"
              "Przykłady:\n"
              "• Przetłumacz na niemiecki\n"
              "• Znajdź wszystkie wzmianki o datach i wydarzeniach\n"
              "• Stwórz listę pytań o tekście",
    },
    
    "processing_with_prompt": {
        "ru": "🧠 Обрабатываю аудио с запросом: {prompt}",
        "en": "🧠 Processing your audio with the prompt: {prompt}",
        "pl": "🧠 Przetwarzanie twojego audio z zapytaniem: {prompt}",
    },
    
    "gpt_processing_completed": {
        "ru": "✅ Обработка через ChatGPT завершена!",
        "en": "✅ Processing with ChatGPT completed!",
        "pl": "✅ Przetwarzanie przez ChatGPT zakończone!",
    },
    
    "transcription_page_header": {
        "ru": "📝 **Результат транскрипции** (страница {page}/{total}):\n\n",
        "en": "📝 **Transcription result** (page {page}/{total}):\n\n",
        "pl": "📝 **Wynik transkrypcji** (strona {page}/{total}):\n\n",
    },
    
    "gpt_result_page_header": {
        "ru": "🧠 **Результат обработки ChatGPT** (страница {page}/{total}):\n\n",
        "en": "🧠 **ChatGPT processing result** (page {page}/{total}):\n\n",
        "pl": "🧠 **Wynik przetwarzania ChatGPT** (strona {page}/{total}):\n\n",
    },
    
    "transcription_in_progress": {
       "ru": "У вас уже есть активная задача транскрипции. "
             "Дождитесь ее завершения или отмените текущую задачу и попробуйте снова.",
       "en": "You already have an active transcription task. "
             "Wait for it to complete or cancel the current task and try again.",
       "pl": "Masz już aktywne zadanie transkrypcji. "
             "Poczekaj na jego zakończenie lub anuluj bieżące zadanie i spróbuj ponownie.",
   },
   
   "not_audio_file": {
       "ru": "Этот документ не похож на аудио или видеофайл. Отправьте аудио или видеофайл для транскрипции.",
       "en": "This document doesn't look like an audio or video file. Send an audio or video file for transcription.",
       "pl": "Ten dokument nie wygląda na plik audio lub wideo. Wyślij plik audio lub wideo do transkrypcji.",
   },

   "please_send_audio": {
       "ru": "Пожалуйста, отправьте аудио или видеофайл.",
       "en": "Please send an audio or video file.",
       "pl": "Proszę wysłać plik audio lub wideo.",
   },

   "please_send_audio_or_use_help": {
       "ru": "Пожалуйста, отправьте мне голосовое сообщение, аудио или видеофайл для транскрипции.\n"
             "Используйте /help для получения справки.",
       "en": "Please send me a voice message, audio or video file for transcription.\n"
             "Use /help to get assistance.",
       "pl": "Proszę wysłać mi wiadomość głosową, plik audio lub wideo do transkrypcji.\n"
             "Użyj /help, aby uzyskać pomoc.",
   },
   
   "transcription_canceled": {
       "ru": "Транскрипция отменена",
       "en": "Transcription canceled",
       "pl": "Transkrypcja anulowana",
   },
   
   "error_occurred": {
       "ru": "Произошла ошибка: {error}",
       "en": "An error occurred: {error}",
       "pl": "Wystąpił błąd: {error}",
   },
   
   "file_not_found": {
       "ru": "Файл не найден, отправьте файл заново",
       "en": "File not found, please send the file again",
       "pl": "Nie znaleziono pliku, wyślij plik ponownie",
   },
   
   "pages_not_found": {
       "ru": "Информация о страницах не найдена",
       "en": "Page information not found",
       "pl": "Nie znaleziono informacji o stronach",
   },
   
   "transcription_not_found": {
       "ru": "Транскрипция не найдена",
       "en": "Transcription not found",
       "pl": "Nie znaleziono transkrypcji",
   },
   
   "transcription_language_selected": {
       "ru": "🔤 Выбран язык: {lang_name}\n⏳ Начинаю транскрипцию...",
       "en": "🔤 Selected language: {lang_name}\n⏳ Starting transcription...",
       "pl": "🔤 Wybrany język: {lang_name}\n⏳ Rozpoczynam transkrypcję...",
   },
   
   "chatgpt_unavailable": {
       "ru": "ChatGPT недоступен",
       "en": "ChatGPT unavailable",
       "pl": "ChatGPT niedostępny",
   },

   "starting_auto_transcription": {
        "ru": "🎧 Файл обработан! Начинаю автоматическое определение языка и транскрипцию...",
        "en": "🎧 File processed! Starting automatic language detection and transcription...",
        "pl": "🎧 Plik przesłany! Rozpoczynam automatyczne wykrywanie języka i transkrypcję...",
    },

    "file_ready_for_transcription": {
        "ru": "✅ Файл готов к обработке",
        "en": "✅ File ready for processing",
        "pl": "✅ Plik gotowy do przetwarzania",
    },

    "uploading_file": {
        "ru": "📤 Обрабатываю файл ...",
        "en": "📤 Processing file...",
        "pl": "📤 Przesyłanie pliku...",
    },

    "starting_auto_detection": {
        "ru": "🔍 Определяю язык аудио и начинаю транскрипцию...",
        "en": "🔍 Detecting audio language and starting transcription...",
        "pl": "🔍 Wykrywam język audio i rozpoczynam transkrypcję...",
    },

    "fix_grammar": {
        "ru": "📝 Исправить грамматику",
        "en": "📝 Fix Grammar",
        "pl": "📝 Popraw gramatykę",
    },

    "prepare_email": {
        "ru": "📧 Подготовить для email",
        "en": "📧 Prepare for Email", 
        "pl": "📧 Przygotuj do emaila",
    },

    "convert_to_notes": {
        "ru": "📋 Конвертировать в заметки",
        "en": "📋 Convert to Notes",
        "pl": "📋 Konwertuj na notatki",
    },

    "awaiting_custom_request": {
        "ru": "✏️ **Напишите ваш запрос**\n\n"
            "Просто отправьте сообщение с описанием того, как вы хотите обработать текст транскрипции.\n\n"
            "Примеры:\n"
            "• Переведи на английский язык\n"
            "• Найди все упоминания дат и событий\n"
            "• Создай список вопросов по тексту",
        "en": "✏️ **Write your request**\n\n"
            "Just send a message describing how you want to process the transcription text.\n\n"
            "Examples:\n"
            "• Translate to French\n"
            "• Find all mentions of dates and events\n"
            "• Create a list of questions about the text",
        "pl": "✏️ **Napisz swoje żądanie**\n\n"
            "Po prostu wyślij wiadomość opisującą, jak chcesz przetworzyć tekst transkrypcji.\n\n"
            "Przykłady:\n"
            "• Przetłumacz na niemiecki\n"
            "• Znajdź wszystkie wzmianki o datach i wydarzeniach\n"
            "• Stwórz listę pytań o tekście",
    },
   
   "chatgpt_api_not_configured": {
       "ru": "❌ Обработка через ChatGPT недоступна: API ключ не настроен.\n"
             "Обратитесь к администратору бота.",
       "en": "❌ Processing with ChatGPT is unavailable: API key not configured.\n"
             "Contact the bot administrator.",
       "pl": "❌ Przetwarzanie przez ChatGPT jest niedostępne: klucz API nie skonfigurowany.\n"
             "Skontaktuj się z administratorem bota.",
   },

    "language_detection_info": {
        "ru": "🎯 **Определённый язык:** {detected_lang}",
        "en": "🎯 **Detected language:** {detected_lang}",
        "pl": "🎯 **Wykryty język:** {detected_lang}",
    },

    "change_detected_language_button": {
        "ru": "🔄 Неверно определился язык? Изменить",
        "en": "🔄 Wrong language detected? Change",
        "pl": "🔄 Źle wykryty język? Zmień",
    },

    "select_correct_language": {
        "ru": "🌐 **Выберите правильный язык:**\n\n"
              "Текущий определённый язык: {current_lang}",
        "en": "🌐 **Select the correct language:**\n\n"
              "Currently detected language: {current_lang}",
        "pl": "🌐 **Wybierz właściwy język:**\n\n"
              "Aktualnie wykryty język: {current_lang}",
    },

    "retranscribing_with_language": {
        "ru": "🔄 Повторяю транскрипцию с языком: {lang_name}...",
        "en": "🔄 Re-transcribing with language: {lang_name}...",
        "pl": "🔄 Ponawianie transkrypcji z językiem: {lang_name}...",
    },

    "language_changed_success": {
        "ru": "✅ Язык изменён на {lang_name}. Транскрипция обновлена!",
        "en": "✅ Language changed to {lang_name}. Transcription updated!",
        "pl": "✅ Język zmieniony na {lang_name}. Transkrypcja zaktualizowana!",
    },

    "original_file_not_found": {
        "ru": "❌ Исходный файл не найден. Загрузите файл заново.",
        "en": "❌ Original file not found. Please upload the file again.",
        "pl": "❌ Nie znaleziono oryginalnego pliku. Prześlij plik ponownie.",
    },

    "speaker_label": {
        "ru": "Спикер",
        "en": "Speaker",
        "pl": "Mówca",
    },

    "transcribe_with_speakers_button": {
        "ru": "🎭 Разделить по спикерам",
        "en": "🎭 Separate by speakers",
        "pl": "🎭 Podziel na mówców",
    },
}

def get_string(key, lang, **kwargs):
   if key not in STRINGS:
       return f"[Missing string: {key}]"
   
   if lang not in STRINGS[key]:
       lang = "en" if "en" in STRINGS[key] else list(STRINGS[key].keys())[0]
   
   localized_string = STRINGS[key][lang]
   
   if kwargs:
       try:
           return localized_string.format(**kwargs)
       except KeyError as e:
           return f"[Format error in {key}: {e}]"
   
   return localized_string

def get_supported_languages_list(lang):
   languages = []
   for code, name in AVAILABLE_LANGUAGES.items():
       languages.append(f"• {name}")
   return "\n".join(languages)