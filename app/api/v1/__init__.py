# empty
from fastapi import APIRouter
from app.api.v1 import sync, crm_info

router = APIRouter()
router.include_router(sync.router, prefix="/sync")
router.include_router(crm_info.router, prefix="/crms")
