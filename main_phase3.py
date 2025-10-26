from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from router_phase3 import route_message, initialize_model  

app = FastAPI(
    title="UnityToServe Chatbot API",
    description="Smart chatbot backend using spaCy + PhraseMatcher + Rule-Based Engine",
    version="1.0"
)

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # update this if frontend domain changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str

# Load SentenceTransformer on startup
@app.on_event("startup")
def load_dependencies():
    initialize_model()

# ✅ Main chatbot endpoint
@app.post("/chat")
async def chat_handler(request: MessageRequest):
    user_msg = request.message
    return route_message(user_msg)  # ✅ FIXED: return structured response directly

@app.get("/")
def root():
    return {"status": "Chatbot API is running"}
