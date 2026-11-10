# ChatTNT — AI-Powered Audio/Video Transcription Bot

A Telegram bot designed for automatic transcription and summarization of voice messages, audio, and video files.

## 🚀 Features
- **Speech-to-Text**: Converts voice messages, audio, and video to formatted text using OpenAI Whisper & AssemblyAI.
- **AI Summarization**: Generates quick summaries, key notes, and action items via ChatGPT.
- **Custom Prompts**: Flexible text processing based on user-defined prompts.

## 🛠 Tech Stack
- **Language**: Python 3.x
- **Database**: SQLite
- **Containerization**: Docker, Docker Compose
- **APIs**: OpenAI API (Whisper & ChatGPT), AssemblyAI API, Telegram Bot API

## 📁 Project Structure
```text
ChatTNT/
├── handlers/                  # Bot event and command handlers
│   ├── callback_handlers.py
│   ├── command_handlers.py
│   ├── media_handlers.py
│   └── navigation_handlers.py
├── services/                  # External service integrations
│   ├── assemblyai_service.py
│   ├── chatgpt_service.py
│   ├── transcription_service.py
│   └── whisper_service.py
├── database.py                # Database connection & models
├── main.py                    # Application entry point
├── menus.py                   # Telegram UI menus & keyboards
├── strings.py                 # Text templates & prompt strings
├── utils.py                   # Helper utilities
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Container orchestration configuration
├── .env.example               # Template for environment variables
├── .gitignore                 # Files excluded from version control
└── requirements.txt           # Python package dependencies
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional, for containerized run)
- OpenAI API Key & Telegram Bot Token

### 1. Clone the Repository
```bash
git clone https://github.com/digodik/ChatTNT.git
cd ChatTNT
```

### 2. Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```bash
cp .env.example .env
```
Fill in your API keys in `.env`.

### 3. Run Locally
```bash
pip install -r requirements.txt
python main.py
```

### 4. Run with Docker
```bash
docker-compose up -d --build
```
