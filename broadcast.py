#broadcast.py
import os
import asyncio
import sqlite3
import logging
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

load_dotenv()

TEAM_URL = "https://github.com/digodik/"
DONATE_URL = "https://buy.stripe.com/dRmfZi5VU3e80wpfT21Fe02"

# Set to your Telegram user_id (as string) to send ONLY to yourself for testing.
# Set back to None to broadcast to everyone in the DB.
TEST_USER_ID = 6623572855

MESSAGES = {
    "ru": (
        "🎉 <b>Обновление ChatTNT</b>\n\n"
        "Теперь бот умеет транскрибировать <b>видео-кружочки</b> и <b>видео-сообщения</b> — "
        "просто отправьте их в чат, и мы расшифруем звук как обычно.\n\n"
        "💬 Нам важна ваша обратная связь — оставить её можно через форму "
        "<b>Contact Us</b> на нашем сайте: {team_url}\n\n"
        "❤️ Если хотите поддержать проект, это можно сделать здесь: {donate_url}\n\n"
        "Спасибо, что вы с нами!"
    ),
    "en": (
        "🎉 <b>ChatTNT update</b>\n\n"
        "The bot now can transcribe <b>video notes</b> (round videos) and <b>video messages</b> — "
        "just send them to the chat and we'll transcribe the audio as usual.\n\n"
        "💬 Your feedback matters — you can leave it via the "
        "<b>Contact Us</b> form on our website: {team_url}\n\n"
        "❤️ If you'd like to support the project, you can do it here: {donate_url}\n\n"
        "Thanks for being with us!"
    ),
    "pl": (
        "🎉 <b>Aktualizacja ChatTNT</b>\n\n"
        "Bot może teraz transkrybować <b>wiadomości wideo</b> i <b>kółeczka wideo</b> — "
        "po prostu wyślij je na czat, a my jak zwykle przepiszemy dźwięk.\n\n"
        "💬 Twoja opinia jest dla nas ważna — możesz ją zostawić przez formularz "
        "<b>Contact Us</b> na naszej stronie: {team_url}\n\n"
        "❤️ Jeśli chcesz wesprzeć projekt, możesz to zrobić tutaj: {donate_url}\n\n"
        "Dziękujemy, że jesteś z nami!"
    ),
}

DB_PATH = os.path.join(os.getcwd(), "db", "users.db")
SESSION_DIR = os.path.join(os.getcwd(), "cache", "sessions")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("broadcast")


def load_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, language FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows


async def send_to_user(app, user_id, lang):
    text = MESSAGES.get(lang or "en", MESSAGES["en"]).format(
        team_url=TEAM_URL, donate_url=DONATE_URL
    )
    try:
        await app.send_message(
            int(user_id),
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return "ok"
    except FloodWait as e:
        logger.warning(f"FloodWait {e.value}s for {user_id}, sleeping")
        await asyncio.sleep(e.value)
        return await send_to_user(app, user_id, lang)
    except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid) as e:
        logger.info(f"Skip {user_id}: {type(e).__name__}")
        return "skipped"
    except Exception as e:
        logger.error(f"Failed {user_id}: {e}")
        return "failed"


async def main():
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        raise SystemExit("Missing API_ID / API_HASH / BOT_TOKEN in .env")

    if "YOUR-TEAM-URL" in TEAM_URL:
        raise SystemExit("Set TEAM_URL in broadcast.py before running")
    if "YOUR-STRIPE-DONATE-LINK" in DONATE_URL:
        raise SystemExit("Set DONATE_URL in broadcast.py before running")

    users = load_users()

    if TEST_USER_ID is not None:
        users = [(uid, lang) for uid, lang in users if str(uid) == str(TEST_USER_ID)]
        if not users:
            users = [(str(TEST_USER_ID), "ru")]
        logger.warning(f"TEST MODE — sending only to {TEST_USER_ID}")

    total = len(users)
    logger.info(f"Broadcasting to {total} users")

    os.makedirs(SESSION_DIR, exist_ok=True)
    app = Client(
        "broadcast_sender",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workdir=SESSION_DIR,
    )

    stats = {"ok": 0, "skipped": 0, "failed": 0}
    await app.start()
    try:
        for i, (user_id, lang) in enumerate(users, 1):
            result = await send_to_user(app, user_id, lang)
            stats[result] += 1
            if i % 20 == 0 or i == total:
                logger.info(f"Progress: {i}/{total} — {stats}")
            await asyncio.sleep(0.05)
    finally:
        await app.stop()

    logger.info(f"Done. Delivered: {stats['ok']}, skipped: {stats['skipped']}, failed: {stats['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
