from fastapi import FastAPI
from app.api.v1 import sync, crm_info
from app.core.logger import logger
from app.services.poller import CommonCRMPoller
from app.services.sync_manager import SyncManager
import asyncio
from app.core.loader import load_systems_from_config
from app.services.orchestrator import SyncOrchestrator
from app.core.context import context
from app.services.pollers.sqlite_poller import SQLitePoller
from app.services.pollers.file_poller import FilePoller
from app.systems.sqlite_sink import SQLiteSink
from app.systems.file import FileSource

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

    # Set orchestrator for manual sync route
    source, sink = load_systems_from_config("sync_config.json")
    context.orchestrator = SyncOrchestrator(source, sink)

    # Run the CRM poller in background
    asyncio.create_task(poller.poll_loop())

    # Optionally trigger one sync at boot
    # asyncio.create_task(context.orchestrator.sync_all())

    # sqlPoller = SQLitePoller(source, sink, interval=2)
    # asyncio.create_task(sqlPoller.poll_loop())

    # Assume syncing between sqlite and file
    sqlite_source = source
    file_sink = sink
    file_source = FileSource("data/sink.json")
    sqlite_sink = SQLiteSink("data/demo.sqlite", "users")

    # Poll both directions
    asyncio.create_task(SQLitePoller(sqlite_source, file_sink).poll_loop())
    asyncio.create_task(FilePoller(file_source, sqlite_sink).poll_loop())


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Record Sync Service is shutting down...")
