from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import sys
import uvicorn

# Add project root to path to import from Phase 3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Phase_3_RAG_Core.rag_engine import NextLeapRAG

app = FastAPI(title="NextLeap RAG Chatbot API")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend UI
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Phase_5_Chatbot_Frontend_UI")
if os.path.exists(frontend_path):
    app.mount("/gui", StaticFiles(directory=frontend_path, html=True), name="gui")

rag = NextLeapRAG()


# Simple in-memory session management
# In production, this would use Redis or Postgres
sessions = {}

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
def read_root():
    return {"message": "NextLeap RAG Chatbot API is running."}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Legacy non-streaming endpoint for compatibility."""
    try:
        response_text = rag.generate_response(request.query)
        return ChatResponse(response=response_text, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """New streaming endpoint for faster performance."""
    def generate():
        try:
            for chunk in rag.generate_response_stream(request.query):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"
            
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/status")
def get_status():
    """Returns the last updated status of the knowledge base."""
    metadata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return {"last_updated": "Never", "status": "no_data"}

@app.get("/history/{session_id}")
def get_history(session_id: str):
    if session_id not in sessions:
        return {"history": []}
    return {"history": sessions[session_id]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
