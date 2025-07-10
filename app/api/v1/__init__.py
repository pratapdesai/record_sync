# empty
from fastapi import APIRouter
from app.api.v1 import sync

router = APIRouter()
router.include_router(sync.router, prefix="/sync")

