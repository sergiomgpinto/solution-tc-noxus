from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..db.database import db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_tables()
    print("Database tables created/verified")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Adaptive Chatbot API",
    description="An intelligent chatbot that learns from user feedback",
    version="0.1.0-dev",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Adaptive Chatbot API",
        "version": "0.1.0-dev",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(router, prefix="/api/v1")
