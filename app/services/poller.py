import asyncio
from datetime import datetime, timedelta
from app.core.logger import logger
from app.services.sync_manager import SyncManager
from app.crms.salesforce import SalesforceCRM
from app.crms.outreach import OutreachCRM


class CommonCRMPoller:
    def __init__(self, sync_manager: SyncManager):
        self.sync_manager = sync_manager
        self.poll_interval = 300  # 5 minutes
        self.last_synced = {}  # per-CRM watermark
        self.crm_plugins = {
            "salesforce": SalesforceCRM(config={}),
            "outreach": OutreachCRM(config={}),
        }

    async def poll_loop(self):
        while True:
            await self.poll_all_crms()
            await asyncio.sleep(self.poll_interval)

    async def poll_all_crms(self):
        for crm_name, crm_plugin in self.crm_plugins.items():
            try:
                await self.poll_crm(crm_name, crm_plugin)
            except NotImplementedError:
                logger.warning(f"{crm_name} does not support polling.")
            except Exception as e:
                logger.error(f"Polling error for {crm_name}: {e}")

    async def poll_crm(self, crm_name, crm_plugin):
        logger.info(f"Polling {crm_name} for recent changes...")

        since = self.last_synced.get(crm_name)
        if since is None:
            since = datetime.utcnow() - timedelta(minutes=10)

        records = await crm_plugin.fetch_recent_changes(since)
        for record in records:
            await self.sync_manager.enqueue_sync(crm_name, record)

        self.last_synced[crm_name] = datetime.utcnow()
        logger.info(f"{crm_name} poller processed {len(records)} records.")

    async def poll_once(self, crm_name: str):
        crm_plugin = self.crm_plugins.get(crm_name)
        if not crm_plugin:
            raise Exception(f"CRM {crm_name} not found.")
        await self.poll_crm(crm_name, crm_plugin)
