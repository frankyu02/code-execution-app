# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import docker
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware

SQLALCHEMY_DATABASE_URL = "sqlite:///./storage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CodeSubmission(Base):
    __tablename__ = 'code_submissions'
    id = Column(String, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    output = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],  # Add other allowed methods if needed
    allow_headers=["*"],
)
client = docker.from_env()

class Code(BaseModel):
    code: str

@app.post("/api/test")
async def test_code(code: Code):
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "python:3.11", "python", "-c", code.code],
            capture_output=True, text=True, timeout=5
        )
        return {"output": result.stdout}
    except subprocess.TimeoutExpired:
        return {"output": "Execution timed out"}

@app.post("/api/submit")
async def submit_code(code: Code):
    db = SessionLocal()
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "python:3.11", "python", "-c", code.code],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout
        submission_id = str(uuid.uuid4())
        submission = CodeSubmission(id=submission_id, code=code.code, output=output)
        db.add(submission)
        db.commit()
        return {"success": True, "id": submission_id}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out"}
    finally:
        db.close()
