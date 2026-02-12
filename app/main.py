from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Nexus Meta-Agent Orchestrator",
    version="0.1"
)

app.include_router(router)
