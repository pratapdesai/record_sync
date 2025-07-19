from fastapi import FastAPI
from app.api.v1 import sync, crm_info
from app.core.logger import logger
from app.services.poller import CommonCRMPoller
from app.services.sync_manager import SyncManager
import asyncio
from app.core.loader import load_systems_from_config
from app.services.pollers.sqlite_poller import SQLitePoller
from app.services.pollers.file_poller import FilePoller
from app.systems.sqlite_sink import SQLiteSink
from app.systems.file import FileSource, FileSink
from app.crms.salesforce import SalesforceCRM
from app.services.pollers.salesforce_poller import SalesforcePoller
from app.systems.sqlite import SQLiteSource

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
    sqlite_to_salesforce_bidirectional_sync()

    # Uncomment if needed -- Bi Directional syncing between File (System A) and File (System B)
    # file_to_file_bidirectional_sync()


def sqlite_to_file_bidirectional_sync():
    # Bi Directional syncing between sqlite (System A) and file (System B)
    source, sink = load_systems_from_config("sync_config_sqlite_file.json")

    sqlite_source = source
    file_sink = sink
    file_source = FileSource("data/sink.json")
    sqlite_sink = SQLiteSink("data/demo.sqlite", "users")

    # Poll both directions
    asyncio.create_task(SQLitePoller(sqlite_source, file_sink, 5, rules_path="rules_sqlite-file.json").poll_loop())
    asyncio.create_task(FilePoller(file_source, sqlite_sink, 5, rules_path="rules_file.json").poll_loop())


def sqlite_to_salesforce_bidirectional_sync():
    # Assume SalesforceCRM is System B
    salesforce = SalesforceCRM(config={})
    sqlite_sink = SQLiteSink("data/demo.sqlite", "users")
    sqlite_source = SQLiteSource("data/demo.sqlite", "users")

    logger.info("[Startup] SalesforcePoller launched")
    # Start Salesforce → SQLite poller
    asyncio.create_task(SQLitePoller(sqlite_source, salesforce).poll_loop())
    asyncio.create_task(SalesforcePoller(salesforce, sqlite_sink).poll_loop())


def file_to_file_bidirectional_sync():
    source, sink = load_systems_from_config("sync_config_file_file.json")

    # Poll both directions
    asyncio.create_task(FilePoller(source, sink, 5, rules_path="rules_file_file.json").poll_loop())

    source = FileSource("data/sink.json")
    sink = FileSink("data/source.json")

    asyncio.create_task(FilePoller(source, sink, 5, rules_path="rules_file_file.json").poll_loop())


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Record Sync Service is shutting down...")
