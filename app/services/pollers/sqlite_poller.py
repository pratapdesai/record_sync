import asyncio
from app.core.logger import logger
from app.services.rules_engine import RulesEngine
from app.services.status import status_tracker

class SQLitePoller:
    def __init__(self, source, sink, interval=5, rules_path="rules.json"):
        self.source = source
        self.sink = sink
        self.interval = interval  # seconds
        self.rules = RulesEngine(rules_path)

    async def poll_loop(self):
        status_tracker.stats["pollers_active"].append("sqlite")
        while True:
            try:
                new_records = await self.source.fetch_new_records()
                for record in new_records:
                    if not self.rules.match(record):
                        continue
                    transformed = self.rules.transform(record)
                    if hasattr(self.sink, "push"):
                        await self.sink.push(transformed)
                    elif hasattr(self.sink, "write_record"):
                        await self.sink.write_record(transformed)
                    else:
                        raise Exception(f"Unsupported sink type: {type(self.sink)}")
                    logger.info(f"[Realtime Sync] Record {record['record_id']} synced")
            except Exception as e:
                logger.exception(f"[Poller] Error syncing records: {e}")

            await asyncio.sleep(self.interval)
