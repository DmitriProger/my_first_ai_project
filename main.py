from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Request

from db import Base, add_request_data, engine, get_user_requests
from gemini_client import get_answer_from_gemeni


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    print("Все таблицы созданы")
    yield


app = FastAPI(lifespan=lifespan, title="ValoriumGPT")


@app.get("/requests")
def get_my_requests(request: Request):
    user_ip_address = request.client.host
    print(user_ip_address)
    user_requests = get_user_requests(ip_address=user_ip_address)
    return user_requests


@app.post("/requests")
def send_prompt(
    request: Request,
    prompt: str = Body(embed=True),
):
    user_ip_address = request.client.host
    answer = get_answer_from_gemeni(prompt)
    add_request_data(ip_address=user_ip_address, prompt=prompt, response=answer)
    return {"answer": answer}
