from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .supervisor_agent import supervisor_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/chat")
async def chat_response(request: Request):
    data = await request.json()
    user_message = data.get("prompt")
    output = supervisor_agent(user_message)

    return {"response": output}