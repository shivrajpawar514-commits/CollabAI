from fastapi import APIRouter
from app.api.v1 import auth, users, skills, projects, teams, tasks, chat, notifications, ws, ai, rag, ml, advanced_ai, system

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(skills.router)
api_router.include_router(projects.router)
api_router.include_router(teams.router)
api_router.include_router(tasks.router)
api_router.include_router(chat.router)
api_router.include_router(notifications.router)
api_router.include_router(ws.router)
api_router.include_router(ai.router)
api_router.include_router(rag.router)
api_router.include_router(ml.router)
api_router.include_router(advanced_ai.router)
api_router.include_router(system.router)



