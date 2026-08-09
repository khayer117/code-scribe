import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine
from app.routes import notes

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeScribe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/api")
