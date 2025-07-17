from app.core.logger import logger


class SyncOrchestrator:
    def __init__(self, source, sink):
        self.source = source
        self.sink = sink

    async def sync_all(self, allow_duplicates: bool = False) -> int:
        logger.info("Starting record-to-record sync...")
        records = await self.source.fetch_records()
        synced = 0
        for record in records:
            await self.sink.write_record(record, allow_duplicates=allow_duplicates)
            synced += 1
        logger.info(f"Finished syncing {len(records)} records.")
        return synced
