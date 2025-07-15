import asyncio
from app.core.logger import logger

class SQLitePoller:
    def __init__(self, source, sink, interval=5):
        self.source = source
        self.sink = sink
        self.interval = interval  # seconds

    async def poll_loop(self):
        while True:
            try:
                new_records = await self.source.fetch_new_records()
                for record in new_records:
                    await self.sink.write_record(record)
                    logger.info(f"[Realtime Sync] Record {record['record_id']} synced")
            except Exception as e:
                logger.exception(f"[Poller] Error syncing records: {e}")

            await asyncio.sleep(self.interval)
