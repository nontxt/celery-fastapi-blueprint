# Create network
docker network create celery-network

# Build the Worker image **celery_worker**
docker build -t celery_worker -f Dockerfile.worker .

# Run the docker-compose file
docker compose up --build -d

# Run manager
sh scripts/run_manager.sh

# Check the logs
docker logs -f fastapi_app

# Check the worker logs
docker logs -f celery_worker

# Send task via FastAPI
curl -X POST http://localhost:8000/tasks/run-task/

# Load test
for i in {1..50}; do curl -X POST http://localhost:8000/tasks/run-task/; done