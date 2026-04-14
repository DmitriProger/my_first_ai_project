from contextlib import asynccontextmanager
from typing import Optional

import sqlalchemy
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import (
    Base,
    Chat,
    ChatRequests,
    add_request_data,
    create_chat,
    engine,
    get_chat_requests,
    get_user_chats,
    get_user_requests,
    session,
    update_chat_title,
)
from gemini_client import get_answer_from_gemeni


class SendPromptBody(BaseModel):
    prompt: str
    chat_id: Optional[int] = None


def migrate_orphan_requests() -> None:
    """Assign chat_requests without chat_id to a per-user default chat."""
    from sqlalchemy import select

    with session() as s:
        orphans = s.execute(
            select(ChatRequests).where(ChatRequests.chat_id.is_(None))
        ).scalars().all()
        if not orphans:
            return
        ips = {r.ip_address for r in orphans}
        for ip in ips:
            chat = Chat(ip_address=ip, title="История чатов")
            s.add(chat)
            s.flush()
            for req in orphans:
                if req.ip_address == ip:
                    req.chat_id = chat.id
        s.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    # Add chat_id column to existing chat_requests table if missing
    with engine.connect() as conn:
        try:
            conn.execute(sqlalchemy.text(
                "ALTER TABLE chat_requests ADD COLUMN chat_id INTEGER REFERENCES chats(id)"
            ))
            conn.commit()
        except Exception:
            pass  # Column already exists
    migrate_orphan_requests()
    print("Все таблицы созданы")
    yield


app = FastAPI(lifespan=lifespan, title="ValoriumGPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chats")
def get_chats(request: Request):
    user_ip = request.client.host
    return get_user_chats(ip_address=user_ip)


@app.post("/chats")
def create_new_chat(request: Request):
    user_ip = request.client.host
    return create_chat(ip_address=user_ip)


@app.get("/chats/{chat_id}/requests")
def get_chat_messages(chat_id: int):
    return get_chat_requests(chat_id=chat_id)


@app.get("/requests")
def get_my_requests(request: Request):
    user_ip_address = request.client.host
    print(user_ip_address)
    user_requests = get_user_requests(ip_address=user_ip_address)
    return user_requests


@app.post("/requests")
def send_prompt(request: Request, body: SendPromptBody):
    user_ip_address = request.client.host
    chat_id = body.chat_id

    # Auto-create a chat if none was specified
    if chat_id is None:
        chat = create_chat(ip_address=user_ip_address)
        chat_id = chat["id"]

    answer = get_answer_from_gemeni(body.prompt)
    add_request_data(
        ip_address=user_ip_address,
        prompt=body.prompt,
        response=answer,
        chat_id=chat_id,
    )

    # Set chat title from first message
    short_title = body.prompt[:40] + ("..." if len(body.prompt) > 40 else "")
    new_title = update_chat_title(chat_id, short_title)

    return {"answer": answer, "chat_id": chat_id, "chat_title": new_title}
