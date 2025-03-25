import logging
import os
import subprocess
import time

import redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
WORKER_TIMEOUT = int(os.getenv("WORKER_TIMEOUT", 10))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
MAX_QUEUE_LENGTH = int(os.getenv("MAX_QUEUE_LENGTH", 10))
WAIT_TIME = int(os.getenv("WAIT_TIME", 10))

DOCKER_IMAGE = os.getenv("WORKER_DOCKER_IMAGE", "celery_worker:latest")
NETWORK_NAME = os.getenv("DOCKER_NETWORK", "celery-network")
WORKER_PREFIX = "celery-worker"

redis_client = redis.Redis.from_url(REDIS_URL)


def get_task_queue_length():
    return redis_client.llen("celery")


def get_running_workers():
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", f"name={WORKER_PREFIX}"],
        stdout=subprocess.PIPE,
        text=True,
    )
    return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0


def run_worker_container():
    worker_name = f"{WORKER_PREFIX}-extra-{int(time.time())}"
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            worker_name,
            "--network",
            "celery-network",
            DOCKER_IMAGE,
            "celery",
            "-A",
            "celery_app.celery",
            "worker",
            "--loglevel=info",
            "--concurrency=5",
            "-n",
            f"{worker_name}",
        ]
    )
    logger.info(f"Scaling up: worker {worker_name} started")


def stop_workers():
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", f"name={WORKER_PREFIX}-extra"],
        stdout=subprocess.PIPE,
        text=True,
    )
    workers = result.stdout.strip().split("\n")

    for worker in workers:
        subprocess.run(["docker", "stop", worker])
        logger.info(f"Scaling down: worker {worker} stopped")


def scale_workers_docker():
    while True:
        queue_length = get_task_queue_length()
        current_workers = get_running_workers()
        logger.info(f"Queue length: {queue_length}, running workers: {current_workers}")

        if queue_length > MAX_QUEUE_LENGTH and current_workers < MAX_WORKERS:
            run_worker_container()

        elif queue_length == 0 and current_workers > 1:
            time.sleep(WORKER_TIMEOUT)
            if get_task_queue_length() != 0:
                continue

            stop_workers()

        time.sleep(WAIT_TIME)


if __name__ == "__main__":
    scale_workers_docker()
