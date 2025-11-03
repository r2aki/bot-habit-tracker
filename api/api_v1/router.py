from fastapi import APIRouter
from api.api_v1.endpoints import users, habits

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])