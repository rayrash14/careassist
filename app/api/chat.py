from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_qa import get_answer

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    lang: str = "en"  # Default to English

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = get_answer(request.question, lang=request.lang)
        return response
    except Exception as e:
        return {"type": "text", "content": f"An error occurred: {str(e)}"}
