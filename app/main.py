from fastapi import FastAPI

from app.api import tasks

app = FastAPI()

app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
