from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from spellcheck import correct_text

app = FastAPI(title="Spelling Correction API", version="1.0.1")

# Allow frontend origins (you can add more later)
origins = [
    "http://localhost:5173",  # React/Vue frontend
    "https://spell-checker-lhl0.onrender.com"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # allow specific origins
    allow_credentials=True,
    allow_methods=["*"],             # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # allow all headers
)
class TextRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "Spelling Correction API is running 🚀"}

@app.post("/correct")
def correct_spelling(req: TextRequest):
    result = correct_text(req.text)
    return result
