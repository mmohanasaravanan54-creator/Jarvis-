from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from ai import ask_jarvis
from config import HISTORY_LIMIT
from database import Base, engine, get_db

# Creates the tables if you did not run schema.sql (the database itself must exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jarvis AI Assistant", version="1.0.0")

# Lets the frontend call the API even if you open it from another port or file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Small built-in commands (answered without calling the AI) ----------
def local_command(text: str, db: Session):
    t = text.strip().lower()
    if t in ("what time is it", "time", "what is the time", "what's the time"):
        return "It is " + datetime.now().strftime("%I:%M %p") + "."
    if t in ("what is the date", "date", "what's the date", "what day is it"):
        return "Today is " + datetime.now().strftime("%A, %d %B %Y") + "."
    if t.startswith("remember "):
        note = text.strip()[len("remember "):].strip()
        if note:
            db.add(models.Note(content=note))
            db.commit()
            return f"Got it. I will remember: {note}"
    return None


# ---------- Chat ----------
@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    if req.conversation_id:
        convo = db.get(models.Conversation, req.conversation_id)
        if not convo:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        convo = models.Conversation(title=req.message[:60])
        db.add(convo)
        db.commit()
        db.refresh(convo)

    db.add(models.Message(conversation_id=convo.id, role="user", content=req.message))
    db.commit()

    reply = local_command(req.message, db)
    if reply is None:
        recent = (
            db.query(models.Message)
            .filter(models.Message.conversation_id == convo.id)
            .order_by(models.Message.id.desc())
            .limit(HISTORY_LIMIT)
            .all()
        )
        history = [{"role": m.role, "content": m.content} for m in reversed(recent)]
        notes = [n.content for n in db.query(models.Note).order_by(models.Note.id).all()]
        reply = ask_jarvis(history, notes)

    db.add(models.Message(conversation_id=convo.id, role="assistant", content=reply))
    db.commit()
    return schemas.ChatResponse(conversation_id=convo.id, reply=reply)


# ---------- Conversations ----------
@app.get("/api/conversations", response_model=List[schemas.ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    return db.query(models.Conversation).order_by(models.Conversation.id.desc()).all()


@app.get("/api/conversations/{convo_id}/messages", response_model=List[schemas.MessageOut])
def get_messages(convo_id: int, db: Session = Depends(get_db)):
    convo = db.get(models.Conversation, convo_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo.messages


@app.delete("/api/conversations/{convo_id}")
def delete_conversation(convo_id: int, db: Session = Depends(get_db)):
    convo = db.get(models.Conversation, convo_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(convo)
    db.commit()
    return {"deleted": convo_id}


# ---------- Notes (Jarvis memory) ----------
@app.get("/api/notes", response_model=List[schemas.NoteOut])
def list_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).order_by(models.Note.id.desc()).all()


@app.post("/api/notes", response_model=schemas.NoteOut, status_code=201)
def add_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    new_note = models.Note(content=note.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"deleted": note_id}


@app.get("/api/health")
def health():
    return {"status": "ok", "name": "Jarvis"}


# ---------- Frontend (served by the same server, so everything is joined) ----------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
