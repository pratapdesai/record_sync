import asyncio
from app.core.logger import logger
from app.services.rules_engine import RulesEngine

class SQLitePoller:
    def __init__(self, source, sink, interval=5, rules_path="rules.json"):
        self.source = source
        self.sink = sink
        self.interval = interval  # seconds
        self.rules = RulesEngine(rules_path)

    async def poll_loop(self):
        while True:
            try:
                new_records = await self.source.fetch_new_records()
                for record in new_records:
                    if not self.rules.match(record):
                        continue
                    transformed = self.rules.transform(record)
                    await self.sink.push(transformed)
                    logger.info(f"[Realtime Sync] Record {record['record_id']} synced")
            except Exception as e:
                logger.exception(f"[Poller] Error syncing records: {e}")

            await asyncio.sleep(self.interval)
