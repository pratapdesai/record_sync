import asyncio
from app.crms.salesforce import SalesforceCRM
from app.services.sync_manager import SyncManager
from app.core.logger import logger
from datetime import datetime, timedelta

class SalesforcePoller:
    """
    Periodically pulls recent changes from Salesforce and enqueues them
    for bi-directional sync.
    """

    def __init__(self, sync_manager: SyncManager):
        self.crm = SalesforceCRM(config={})
        self.sync_manager = sync_manager
        self.poll_interval = 300  # 5 min
        self.last_synced = datetime.utcnow() - timedelta(minutes=10)

    async def poll_loop(self):
        while True:
            await self.poll_once()
            await asyncio.sleep(self.poll_interval)

    async def poll_once(self):
        try:
            logger.info("Polling Salesforce for recent changes...")
            changed_records = await self.crm.fetch_recent_changes(self.last_synced)
            for record in changed_records:
                await self.sync_manager.enqueue_sync("salesforce", record)
            self.last_synced = datetime.utcnow()
            logger.info(f"Salesforce poller processed {len(changed_records)} records.")
        except Exception as e:
            logger.error(f"Salesforce poller failed: {e}")
