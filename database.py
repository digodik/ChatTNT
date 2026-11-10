#database.py
import sqlite3
import logging
from typing import List, Optional, Tuple
import os

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.getcwd(), "db", "users.db")

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT PRIMARY KEY,
                total_transcriptions INTEGER DEFAULT 0,
                total_gpt_requests INTEGER DEFAULT 0,
                last_transcription TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                prompt_text TEXT,
                usage_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS current_prompts (
                user_id TEXT PRIMARY KEY,
                prompt_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
             CREATE TABLE IF NOT EXISTS request_logs (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id TEXT,
                 request_type TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (user_id)
             )
         ''')
       
        conn.commit()
        conn.close()
       
        logger.info("База данных успешно инициализирована")
       
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise

def log_request(user_id: str, request_type: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO request_logs (user_id, request_type)
            VALUES (?, ?)
        ''', (user_id, request_type))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Logged request: user_id={user_id}, type={request_type}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging request for user {user_id}: {e}")
        return False

def get_user_language(user_id: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
       
        conn.close()
       
        return result[0] if result else None
       
    except Exception as e:
        logger.error(f"Ошибка при получении языка пользователя {user_id}: {e}")
        return None

def set_user_language(user_id: str, language: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language, last_activity)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, language))
       
        conn.commit()
        conn.close()
       
        logger.info(f"Язык пользователя {user_id} установлен на {language}")
        return True
       
    except Exception as e:
        logger.error(f"Ошибка при установке языка для пользователя {user_id}: {e}")
        return False

def update_user_stats(user_id: str, username: str = None, transcription: bool = False, gpt_request: bool = False) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if username in [None, "", "None"]:
            username = None
        
        if 'last_activity' in columns:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, last_activity)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            if username:
                cursor.execute('''
                    UPDATE users SET username = ?, last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (username, user_id))
            else:
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
        else:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id)
                VALUES (?)
            ''', (user_id,))
            
            if username:
                cursor.execute('''
                    UPDATE users SET username = ?
                    WHERE user_id = ?
                ''', (username, user_id))
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_stats (user_id, total_transcriptions, total_gpt_requests)
            VALUES (?, 0, 0)
        ''', (user_id,))
        
        if transcription:
            cursor.execute('''
                UPDATE user_stats 
                SET total_transcriptions = total_transcriptions + 1,
                    last_transcription = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
        
        if gpt_request:
            cursor.execute('''
                UPDATE user_stats 
                SET total_gpt_requests = total_gpt_requests + 1
                WHERE user_id = ?
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении статистики пользователя {user_id}: {e}")
        return False

def get_predefined_prompts(user_id: str) -> List[str]:
    lang = get_user_language(user_id) or "en"
   
    prompts = {
        "en": [
            "Provide a quick summary of the main points discussed in this transcription.",
            "Fix grammar and improve clarity while maintaining the original meaning and tone.",
            "Prepare this content for email format - make it professional and well-structured.",
            "Convert this into organized notes with clear headings and bullet points."
        ],
        "ru": [
            "Предоставь краткое резюме основных пунктов, обсуждаемых в этой транскрипции.",
            "Исправь грамматику и улучши ясность, сохраняя оригинальный смысл и тон.",
            "Подготовь этот контент для формата email - сделай его профессиональным и хорошо структурированным.",
            "Преобразуй это в организованные заметки с четкими заголовками и пунктами."
        ],
        "pl": [
            "Przedstaw krótkie podsumowanie głównych punktów omówionych w tej transkrypcji.",
            "Popraw gramatykę i zwiększ jasność, zachowując oryginalny sens i ton.",
            "Przygotuj tę treść do formatu email - uczyń ją profesjonalną i dobrze ustrukturyzowaną.",
            "Przekształć to w zorganizowane notatki z wyraźnymi nagłówkami i punktami."
        ]
    }
   
    return prompts.get(lang, prompts["en"])

def add_custom_prompt(user_id: str, prompt_text: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute('''
            SELECT id, usage_count FROM custom_prompts 
            WHERE user_id = ? AND prompt_text = ?
        ''', (user_id, prompt_text))
       
        existing = cursor.fetchone()
       
        if existing:
            cursor.execute('''
                UPDATE custom_prompts 
                SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (existing[0],))
        else:
            cursor.execute('''
                INSERT INTO custom_prompts (user_id, prompt_text, usage_count, last_used)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', (user_id, prompt_text))
       
        conn.commit()
        conn.close()
       
        logger.info(f"Кастомный промпт добавлен для пользователя {user_id}")
        return True
       
    except Exception as e:
        logger.error(f"Ошибка при добавлении кастомного промпта для пользователя {user_id}: {e}")
        return False

def get_recent_custom_prompts(user_id: str, limit: int = 5) -> List[str]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute('''
           SELECT prompt_text FROM custom_prompts 
           WHERE user_id = ? 
           ORDER BY usage_count DESC, last_used DESC 
           LIMIT ?
        ''', (user_id, limit))
         
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
        
    except Exception as e:
        logger.error(f"Ошибка при получении недавних промптов для пользователя {user_id}: {e}")
        return []

def update_prompt_usage(user_id: str, prompt_text: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE custom_prompts 
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
            WHERE user_id = ? AND prompt_text = ?
        ''', (user_id, prompt_text))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении использования промпта для пользователя {user_id}: {e}")
        return False

def get_current_prompt(user_id: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT prompt_text FROM current_prompts WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Ошибка при получении текущего промпта для пользователя {user_id}: {e}")
        return None

def set_current_prompt(user_id: str, prompt_text: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO current_prompts (user_id, prompt_text)
            VALUES (?, ?)
        ''', (user_id, prompt_text))
        
        conn.commit()
        conn.close()
        
        return True
       
    except Exception as e:
        logger.error(f"Ошибка при установке текущего промпта для пользователя {user_id}: {e}")
        return False

def clear_current_prompt(user_id: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM current_prompts WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return True
       
    except Exception as e:
        logger.error(f"Ошибка при очистке текущего промпта для пользователя {user_id}: {e}")
        return False

def get_user_stats(user_id: str) -> Optional[Tuple[int, int, str]]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute('''
            SELECT total_transcriptions, total_gpt_requests, last_transcription
            FROM user_stats WHERE user_id = ?
        ''', (user_id,))
       
        result = cursor.fetchone()
        conn.close()
       
        return result if result else (0, 0, None)
       
    except Exception as e:
        logger.error(f"Ошибка при получении статистики пользователя {user_id}: {e}")
        return None

def get_all_users_count() -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else 0
       
    except Exception as e:
        logger.error(f"Ошибка при подсчете пользователей: {e}")
        return 0

def get_total_transcriptions() -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(total_transcriptions) FROM user_stats")
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result and result[0] else 0
       
    except Exception as e:
        logger.error(f"Ошибка при подсчете транскрипций: {e}")
        return 0

def cleanup_old_prompts(days: int = 30) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
       
        cursor.execute('''
            DELETE FROM custom_prompts 
            WHERE usage_count = 1 
            AND datetime(created_at) < datetime('now', '-{} days')
        '''.format(days))
       
        deleted = cursor.rowcount
       
        conn.commit()
        conn.close()
       
        logger.info(f"Удалено {deleted} старых неиспользуемых промптов")
        return True
       
    except Exception as e:
        logger.error(f"Ошибка при очистке старых промптов: {e}")
        return False

def migrate_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations = []
        
        if 'language' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
        
        if 'username' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN username TEXT")
        
        if 'created_at' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'last_activity' not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        for migration in migrations:
            logger.info(f"Выполняем миграцию: {migration}")
            cursor.execute(migration)
        
        conn.commit()
        conn.close()
        
        if migrations:
            logger.info(f"Выполнено {len(migrations)} миграций")
        else:
            logger.info("Миграции не требуются")
            
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при миграции базы данных: {e}")
        return False