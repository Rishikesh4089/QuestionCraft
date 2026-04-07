# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.v1 import router as v1_router

app = FastAPI(
    title="QuestionCraft API",
    description="A FastAPI + RAG-powered backend for university-level question paper generation.",
    version="3.0.0",
)

# ✅ Enable CORS for your frontend (TalkNotes/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register API routes
app.include_router(v1_router, prefix="/api/v1")

# ✅ Health route
@app.get("/")
def root():
    return {"status": "ok", "service": "QuestionCraft API", "version": "3.0.0"}
