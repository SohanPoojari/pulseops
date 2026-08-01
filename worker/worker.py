import time
from redis import Redis

# This is a simplified worker logic. 
# In production, use the 'rq worker' command line tool.
def process_job(job_id, input_text):
    """Background worker processing."""
    # 1. Update status to PROCESSING
    # (Simulating database update)
    print(f"Processing job {job_id}: {input_text}")
    
    # 2. Perform logic
    time.sleep(5)  # Simulate heavy work
    result = input_text.upper()
    
    # 3. Update result and status to COMPLETED
    print(f"Job {job_id} completed: {result}")
    return result

if __name__ == "__main__":
    from rq import Worker, Connection
    redis_conn = Redis(host='redis', port=6379)
    with Connection(redis_conn):
        worker = Worker(['job_queue'])
        worker.work()