from fastapi import FastAPI
from app.api.v1 import sync, crm_info
from app.core.logger import logger
from app.services.poller import CommonCRMPoller
from app.services.sync_manager import SyncManager

sync_manager = SyncManager()
poller = CommonCRMPoller(sync_manager)

app = FastAPI(
    title="Record Sync Service",
    version="1.0.0",
    description="Microservice to synchronize records between System A and CRMs"
)

# register the router
app.include_router(sync.router, prefix="/v1/sync", tags=["sync"])
app.include_router(crm_info.router, prefix="/v1/crms", tags=["crms"])


@app.on_event("startup")
async def startup_event():
    logger.info("Record Sync Service is starting up...")

    # Uncomment if needed -- Bi Directional syncing between sqlite (System A) and file (System B)
    # sqlite_to_file_bidirectional_sync()

    # Bi Directional syncing between sqlite (System A) and Salesforce CRM (System B)
    # sqlite_to_salesforce_bidirectional_sync(customer_id)

    # Uncomment if needed -- Bi Directional syncing between File (System A) and File (System B)
    # file_to_file_bidirectional_sync()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Record Sync Service is shutting down...")
