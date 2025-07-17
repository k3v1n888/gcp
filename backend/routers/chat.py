from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from ..correlation_service import call_your_llm_api # Reuse the LLM function

router = APIRouter()

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    threat_context: dict
    history: List[ChatMessage]

@router.post("/api/chat")
def handle_chat(request: ChatRequest):
    """Handles a chat conversation about a specific threat."""
    
    # Build a prompt that includes the conversation history
    prompt = f"You are a helpful cybersecurity assistant. A user is asking about the following threat:\n{request.threat_context}\n\nConversation History:\n"
    for message in request.history:
        prompt += f"{message.role}: {message.content}\n"
    prompt += "user: " # Ready for the new question, which is the last item in history.

    # Get the AI's response
    ai_response = call_your_llm_api(prompt)
    
    return {"role": "assistant", "content": ai_response}
