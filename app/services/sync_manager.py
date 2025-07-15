from app.services.queue import QueueManager
from app.crms.salesforce import SalesforceCRM
from app.services.status_manager import StatusManager
from app.services.rules_engine import RulesEngine
from app.core.logger import logger
from app.core.constants import DEFAULT_BATCH_SIZE
import asyncio
from app.crms.outreach import OutreachCRM


class SyncManager:
    def __init__(self):
        self.queue = QueueManager()
        self.status = StatusManager()
        self.rules = RulesEngine()
        self.crm_plugins = {
            "salesforce": SalesforceCRM(config={}),
            "outreach": OutreachCRM(config={})
        }

    async def enqueue_sync(self, crm: str, record: dict):
        if crm not in self.crm_plugins:
            raise ValueError("Unsupported CRM")
        if not self.rules.should_sync(crm, record):
            logger.info(f"Skipping sync of {record['record_id']} due to rule evaluation.")
            self.status.set_status(record['record_id'], "skipped_by_rule")
            return
        self.queue.enqueue(crm, record)
        self.status.set_status(record['record_id'], "queued")
        await self.try_flush(crm)

    async def try_flush(self, crm: str):
        # in production, you'd use a timer or background thread
        batch = self.queue.flush(crm, DEFAULT_BATCH_SIZE)
        if not batch:
            return
        for record in batch:
            plugin = self.crm_plugins[crm]
            try:
                transformed = plugin.transform(record)
                await plugin.push(transformed)
                self.status.set_status(record['record_id'], "synced")
            except Exception as e:
                self.status.set_status(record['record_id'], "failed")
                logger.error(f"Failed to push record to {crm}: {e}")

    async def manual_retry(self, record_id: str):
        # for demonstration only
        logger.info(f"Manual retry triggered for record {record_id}")
