from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine(url="sqlite:///requests.db")

session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(default="Новый чат")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatRequests(Base):
    __tablename__ = "chat_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(index=True)
    prompt: Mapped[str]
    response: Mapped[str]
    chat_id: Mapped[int | None] = mapped_column(ForeignKey("chats.id"), nullable=True)


def get_user_requests(ip_address: str):
    with session() as new_session:
        query = select(ChatRequests).filter_by(ip_address=ip_address)
        result = new_session.execute(query)
        return result.scalars().all()


def get_user_chats(ip_address: str) -> list[dict]:
    with session() as s:
        query = select(Chat).filter_by(ip_address=ip_address).order_by(Chat.created_at.desc())
        chats = s.execute(query).scalars().all()
        return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in chats]


def create_chat(ip_address: str, title: str = "Новый чат") -> dict:
    with session() as s:
        chat = Chat(ip_address=ip_address, title=title)
        s.add(chat)
        s.commit()
        s.refresh(chat)
        return {"id": chat.id, "title": chat.title}


def get_chat_requests(chat_id: int) -> list[dict]:
    with session() as s:
        query = select(ChatRequests).filter_by(chat_id=chat_id)
        messages = s.execute(query).scalars().all()
        return [{"id": m.id, "prompt": m.prompt, "response": m.response} for m in messages]


def update_chat_title(chat_id: int, new_title: str) -> str | None:
    with session() as s:
        chat = s.get(Chat, chat_id)
        if chat and chat.title == "Новый чат":
            chat.title = new_title
            s.commit()
            return new_title
    return None


def add_request_data(ip_address: str, prompt: str, response: str, chat_id: int | None = None) -> None:
    with session() as new_session:
        new_requests = ChatRequests(
            ip_address=ip_address,
            prompt=prompt,
            response=response,
            chat_id=chat_id,
        )
        new_session.add(new_requests)
        new_session.commit()
