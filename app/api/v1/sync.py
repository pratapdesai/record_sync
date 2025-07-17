from fastapi import APIRouter, HTTPException, status, Body, Request
from app.services.sync_manager import SyncManager
from app.services.config_manager import ConfigService
from app.core.logger import logger
from app.models.config import ConfigOverride
from pydantic import BaseModel
from typing import Literal
from app.services.poller import CommonCRMPoller
from app.core.context import context
from fastapi import Query
from app.services.rules_engine import RulesEngine
from app.services.status import status_tracker

router = APIRouter()
sync_manager = SyncManager()
config_service = ConfigService()
poller = CommonCRMPoller(sync_manager)


class SyncRequest(BaseModel):
    operation: Literal["create", "read", "update", "delete"]
    record_id: str
    data: dict
    crm: str


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def sync_record(request: SyncRequest):
    try:
        logger.info(f"Received sync request: {request}")
        await sync_manager.enqueue_sync(request.crm, request.dict())
        return {"message": "Sync request accepted"}
    except Exception as e:
        logger.exception("Error accepting sync request")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retry/{record_id}")
async def manual_retry(record_id: str):
    try:
        await sync_manager.manual_retry(record_id)
        return {"message": f"Retry triggered for {record_id}"}
    except Exception as e:
        logger.exception("Error retrying")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config-override")
async def override_config(payload: ConfigOverride):
    try:
        config_service.override_crm_config(payload)
        return {"message": "Configuration overridden successfully"}
    except Exception as e:
        logger.exception("Error overriding config")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_sync_status():
    return status_tracker.get_status()


@router.get("/status/{record_id}")
async def get_status(record_id: str):
    try:
        status = sync_manager.status.get_status(record_id)
        return {"record_id": record_id, "status": status}
    except Exception as e:
        logger.exception("Error fetching status")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules")
async def update_rules(request: Request):
    try:
        payload = await request.json()
        sync_manager.rules.update_rules(payload)
        return {"message": "Rules updated successfully."}
    except Exception as e:
        logger.exception("Error updating rules")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_rules():
    """
    Returns the currently loaded rules.json config.
    """
    rules_engine = RulesEngine()
    return rules_engine.rules


@router.post("/poll/{crm}")
async def manual_poll_crm(crm: str):
    try:
        await poller.poll_once(crm)
        return {"message": f"{crm} poll manually triggered."}
    except Exception as e:
        logger.error(f"Manual poll failed for {crm}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual")
async def trigger_full_config_sync(allow_duplicates: bool = Query(False, description="Allow duplicate records")):
    if context.orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized.")
    count = await context.orchestrator.sync_all(allow_duplicates=allow_duplicates)
    return {"message": f"Manually synced {count} records from System A to System B."}
