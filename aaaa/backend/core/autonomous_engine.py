from datetime import datetime
import uuid

from .models import projects, logs
from .save_output import save_output

# IMPORT YOUR REAL AGENTS HERE
from ai_services.opportunity_scout import OpportunityScout
# add others:
# from ai_services.product_generator import ProductGenerator
# from ai_services.social_media_ai import SocialMediaAI
# from ai_services.revenue_maximizer import RevenueMaximizer

opportunity_scout = OpportunityScout()
# product_generator = ProductGenerator()
# social_media_ai = SocialMediaAI()
# revenue_agent = RevenueMaximizer()


async def create_project(name="Auto Project"):
    project = {
        "_id": str(uuid.uuid4()),
        "name": name,
        "status": "running",
        "created_at": datetime.utcnow()
    }
    await projects.insert_one(project)
    return project


async def log_action(project_id, message):
    await logs.insert_one({
        "project_id": project_id,
        "message": message,
        "time": datetime.utcnow()
    })


async def run_autonomous_cycle():
    project = await create_project()

    await log_action(project["_id"], "🚀 Starting autonomous project")

    try:
        # 1. Opportunity Scout
        await log_action(project["_id"], "🔍 Scouting opportunities...")
        opportunity = await opportunity_scout.scout_opportunities()
        if opportunity:
            await save_output(project["_id"], opportunity[0], "opportunity", "scout")
            await log_action(project["_id"], f"✅ Opportunity found: {opportunity[0].get('niche', 'Unknown')}")
        else:
            await log_action(project["_id"], "⚠️  No opportunities found")

        # 🔥 ADD THESE WHEN READY
        # await log_action(project["_id"], "📦 Generating product...")
        # product = await product_generator.run(opportunity)
        # await save_output(project["_id"], product, "product", "builder")
        # await log_action(project["_id"], "✅ Product created")

        # await log_action(project["_id"], "📱 Creating marketing content...")
        # marketing = await social_media_ai.run(product)
        # await save_output(project["_id"], marketing, "marketing", "marketing")
        # await log_action(project["_id"], "✅ Marketing created")

        # await log_action(project["_id"], "💰 Setting up revenue...")
        # revenue = await revenue_agent.run(product)
        # await save_output(project["_id"], revenue, "revenue", "money")
        # await log_action(project["_id"], "✅ Revenue setup complete")

        await projects.update_one(
            {"_id": project["_id"]},
            {"$set": {"status": "completed"}}
        )
        await log_action(project["_id"], "🎉 Project completed successfully")

        return project

    except Exception as e:
        await log_action(project["_id"], f"❌ Error: {str(e)}")
        await projects.update_one(
            {"_id": project["_id"]},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        return project
