from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, voice, chat  
from app.services.rag_qa import get_answer  

app = FastAPI(title="CareAssist API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(voice.router, prefix="/api/voice")
app.include_router(chat.router, prefix="/api") 

@app.on_event("startup")
async def warm_up_model():
    print("[Startup] Warming up LLM and RAG...")
    get_answer("Hello", lang="en")
