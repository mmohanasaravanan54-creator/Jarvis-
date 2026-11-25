# JARVIS AI Assistant

Chat and voice assistant. Frontend (HTML/CSS/JS) + Python API (FastAPI) + MySQL, all served from one server.

```
jarvis/
  backend/    main.py (API + serves frontend), ai.py (AI brain), models.py, schemas.py, database.py, config.py
  frontend/   index.html, style.css, app.js
  database/   schema.sql
```

## How the parts join together

Browser (app.js) -> `POST /api/chat` -> FastAPI (main.py) -> saves the message in MySQL -> ai.py asks the AI with recent history + saved notes -> reply saved in MySQL -> reply returned to the browser, which shows and speaks it.

## Setup

1. Install Python 3.10+ and MySQL.
2. Create the database and tables:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Create your settings file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`: set your MySQL password and `ANTHROPIC_API_KEY` (from console.anthropic.com).
   Without a key Jarvis runs in demo mode.
5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
6. Open **http://127.0.0.1:8000** (API docs at `/docs`).

## Features

- Chat with memory of the current conversation (stored in MySQL)
- Voice input (mic button) and spoken replies (Chrome or Edge)
- Say "remember my exam is on Friday" to save a note; Jarvis uses notes in later answers
- Built-in commands: "what time is it", "what is the date"
- History sidebar: reopen or delete old chats

## Ideas to extend

- Login with JWT so each user has their own history
- Tools: weather, web search, reminders, controlling apps
- Streaming replies, wake word ("Hey Jarvis")
