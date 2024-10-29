from fastapi import APIRouter

from app.comfyui.router import router as comfyui_router
from app.health.router import router as health_router

router = APIRouter()

# /health
router.include_router(health_router)

# /comfyui
router.include_router(comfyui_router)
