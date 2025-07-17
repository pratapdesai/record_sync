import asyncio
from app.core.logger import logger
from app.services.rules_engine import RulesEngine
from app.services.status import status_tracker


class SalesforcePoller:
    def __init__(self, source_crm, sqlite_sink, interval=5, rules_path="rules.json"):
        self.source_crm = source_crm
        self.sqlite_sink = sqlite_sink
        self.rules = RulesEngine(rules_path)
        self.interval = interval
        self.synced_ids = set()

    async def poll_loop(self):
        status_tracker.stats["pollers_active"].append("salesforce")
        while True:
            try:
                records = await self.source_crm.pull()
                for record in records:
                    rid = record.get("record_id")
                    if rid in self.synced_ids:
                        continue
                    if not self.rules.match(record):
                        continue
                    transformed = self.rules.transform(record)
                    if not transformed:
                        logger.warning(f"[SalesforcePoller] Skipping empty transformed record: {record}")
                        continue
                    await self.sqlite_sink.write_record(transformed)
                    self.synced_ids.add(rid)
                    logger.info(f"[Salesforce → SQLite] Synced record_id {rid}")
            except Exception as e:
                logger.exception(f"[SalesforcePoller] Sync failed: {e}")
            await asyncio.sleep(self.interval)
