# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import docker
import tempfile
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from typing import List

SQLALCHEMY_DATABASE_URL = "sqlite:///./storage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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

class CodeSubmissionResponse(BaseModel):
    id: str
    code: str
    output: str
#Create a docker container that has numpy and scipy
def create_and_run_container(code: str):
    dockerfile_content = """
    FROM python:3.11
    RUN pip install numpy scipy

    # Set the default command to python3
    CMD ["python3"]
    """

    with tempfile.TemporaryDirectory() as tmpdirname:
        dockerfile_path = os.path.join(tmpdirname, 'Dockerfile')
        
        # Write the Dockerfile content to the file
        with open(dockerfile_path, 'w') as dockerfile:
            dockerfile.write(dockerfile_content)
        
        # Build the Docker image
        image_name = 'python-execution-environment:3.11'
        build_result = subprocess.run(
            ['docker', 'build', '-t', image_name, tmpdirname],
            capture_output=True, text=True
        )
        
        if build_result.returncode != 0:
            raise Exception(f"Docker image build failed: {build_result.stdout}\n{build_result.stderr}")
        
        # Run the Docker container
        result = subprocess.run(
            ["docker", "run", "--rm", image_name, "python", "-c", code],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout, result.stderr

@app.post("/api/test")
async def test_code(code: Code):
    try:
        stdout, stderr = create_and_run_container(code.code)
        return {"output": stdout, "error": stderr}
    except subprocess.TimeoutExpired:
        return {"output": "Execution timed out"}
    except Exception as e:
        return {"output": str(e)}

@app.post("/api/submit")
async def submit_code(code: Code):
    db = SessionLocal()
    try:
        stdout, stderr = create_and_run_container(code.code)
        if stderr != '':
            raise Exception(f"Could not submit code due to error: {stderr}")
        output = stdout
        submission_id = str(uuid.uuid4())
        submission = CodeSubmission(id=submission_id, code=code.code, output=output)
        db.add(submission)
        db.commit()
        return {"success": True, "id": submission_id, "output": output}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@app.get("/api/submissions", response_model=List[CodeSubmissionResponse])
async def get_submissions():
    db = SessionLocal()
    try:
        submissions = db.query(CodeSubmission).all()
        # if not submissions:
        #     raise HTTPException(status_code=404, detail="No code submissions found")
        return submissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving submissions: {str(e)}")
    finally:
        db.close()