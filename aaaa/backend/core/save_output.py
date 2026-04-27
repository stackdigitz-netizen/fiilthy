from datetime import datetime
from .models import outputs

async def save_output(project_id, data, type, agent):
    await outputs.insert_one({
        "project_id": project_id,
        "type": type,
        "data": data,
        "agent": agent,
        "created_at": datetime.utcnow()
    })
