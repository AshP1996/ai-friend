from fastapi import APIRouter
from utils.logger import Logger

router = APIRouter()
logger = Logger("AgentsRoute")

@router.get("/status")
async def get_agents_status():
    return {
        "agents": [
            {"type": "emotion", "status": "active"},
            {"type": "context", "status": "active"},
            {"type": "task", "status": "active"}
        ]
    }