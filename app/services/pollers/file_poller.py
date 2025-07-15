import asyncio
from app.core.logger import logger
from app.services.rules_engine import RulesEngine

class FilePoller:
    def __init__(self, source, sink, interval=5, rules_path="rules.json"):
        self.source = source
        self.sink = sink
        self.rules = RulesEngine(rules_path)
        self.interval = interval

    async def poll_loop(self):
        while True:
            try:
                records = await self.source.fetch_new_records()
                for r in records:
                    if not self.rules.match(r):
                        continue
                    transformed = self.rules.transform(r)
                    await self.sink.write_record(transformed)
                    logger.info(f"[File → SQLite] Synced {transformed.get('record_id')}")
            except Exception as e:
                logger.exception(f"[FilePoller] Sync failed: {e}")
            await asyncio.sleep(self.interval)
