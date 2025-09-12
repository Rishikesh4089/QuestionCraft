# No need for File or UploadFile imports here anymore
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import v1
from settings import settings

app = FastAPI(
    title="Mindblowing University Question Paper Generator",
    description="An advanced agent-based system using RAG and OpenAI to generate university-level examination papers.",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This line correctly includes your real endpoint from v1.py
# The final URL will be http://<your_server>/api/v1/generate-paper/
app.include_router(v1.router, prefix="/api/v1", tags=["Question Paper Generation"])

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the Question Paper Generator API",
        "documentation": "/docs"
    }

# A simple health check endpoint
@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok"}

# The placeholder endpoint that was here has been REMOVED.