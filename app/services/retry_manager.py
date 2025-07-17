from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.logger import logger
from app.services.status import status_tracker
from datetime import datetime

class RetryManager:
    def __init__(self):
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def retry_push(self, crm_plugin, record):
        try:
            transformed = crm_plugin.transform(record)
            status_tracker.update_stat("last_sync_failed", datetime.utcnow().isoformat())
            status_tracker.increment("retries_pending")
            await crm_plugin.push(transformed)
            logger.info(f"Successfully retried record {record['record_id']}")
        except Exception as e:
            logger.error(f"Retry failed for record {record['record_id']}: {e}")
            raise e
