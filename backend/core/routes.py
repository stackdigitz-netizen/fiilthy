from fastapi import APIRouter, HTTPException
from .models import projects, outputs, logs
from .autonomous_engine import run_autonomous_cycle
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/projects")
async def get_projects():
    """Get all projects"""
    try:
        project_list = await projects.find({}, {"_id": 1, "name": 1, "status": 1, "created_at": 1}).to_list(None)
        return project_list
    except Exception as e:
        logger.error(f"Database error fetching projects: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details with outputs and logs"""
    try:
        project = await projects.find_one({"_id": project_id})
        project_outputs = await outputs.find({"project_id": project_id}).to_list(None)
        project_logs = await logs.find({"project_id": project_id}).sort("time", 1).to_list(None)
        
        return {
            "project": project,
            "outputs": project_outputs,
            "logs": project_logs
        }
    except Exception as e:
        logger.error(f"Database error fetching project {project_id}: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")


@router.post("/run")
async def run():
    """Start autonomous cycle"""
    try:
        project = await run_autonomous_cycle()
        return {
            "status": "started",
            "project_id": project["_id"],
            "message": "Autonomous cycle running..."
        }
    except Exception as e:
        logger.error(f"Error running autonomous cycle: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")


@router.get("/health/core")
async def health_core():
    """Health check for core system"""
    return {
        "status": "healthy",
        "core_system": "operational"
    }
