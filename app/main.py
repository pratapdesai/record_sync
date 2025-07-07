from fastapi import FastAPI
from app.api.v1 import sync
from app.core.logger import logger
from app.services.poller import SalesforcePoller
from app.services.sync_manager import SyncManager
import asyncio

sync_manager = SyncManager()
poller = SalesforcePoller(sync_manager)

app = FastAPI(
    title="Record Sync Service",
    version="1.0.0",
    description="Microservice to synchronize records between System A and CRMs"
)

# register the router
app.include_router(sync.router, prefix="/v1/sync", tags=["sync"])

@app.on_event("startup")
async def startup_event():
    await asyncio.create_task(poller.poll_loop())
    logger.info("Record Sync Service is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Record Sync Service is shutting down...")
