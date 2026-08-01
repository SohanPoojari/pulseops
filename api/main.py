from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
import uuid

app = FastAPI()

# Setup Redis connection and queue
redis_conn = Redis(host='redis', port=6379)
q = Queue('job_queue', connection=redis_conn)

class JobRequest(BaseModel):
    input_text: str

@app.get("/health/live")
def health_live():
    """Basic process health check."""
    return {"status": "alive"}

@app.get("/health/ready")
def health_ready():
    """Connectivity check for Redis."""
    try:
        redis_conn.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.post("/jobs")
def create_job(job: JobRequest):
    """Submit a job and enqueue work."""
    job_id = str(uuid.uuid4())
    
    # Enqueue the job and force RQ to use our generated job_id
    q.enqueue('worker.process_job', job_id, job.input_text, job_id=job_id)
    
    return {"job_id": job_id, "status": "QUEUED"}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """View status and result directly from Redis."""
    try:
        # Fetch the job from Redis using RQ
        job = Job.fetch(job_id, connection=redis_conn)
        
        status = "QUEUED"
        if job.is_started:
            status = "PROCESSING"
        elif job.is_finished:
            status = "COMPLETED"
        elif job.is_failed:
            status = "FAILED"
            
        return {
            "job_id": job_id,
            "status": status,
            "result": job.result
        }
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found")