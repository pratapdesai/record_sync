from collections import defaultdict, deque
from threading import Lock
from app.core.logger import logger
from app.services.status import status_tracker
from app.utils.rate_limiter import SlidingWindowRateLimiter

rate_limiter = SlidingWindowRateLimiter()
class QueueManager:
    def __init__(self):
        self.queues = defaultdict(deque)
        self.locks = defaultdict(Lock)

    def enqueue(self, crm: str, record: dict):
        if not rate_limiter.allow(crm):
            logger.warning(f"[RateLimiter] CRM '{crm}' rate limit exceeded. Skipping or delaying push.")
            # Optionally retry or delay
            return
        with self.locks[crm]:
            self.queues[crm].append(record)
            status_tracker.update_stat("queue_size", len(self.queues))
            logger.debug(f"Queued record for {crm}. Queue size: {len(self.queues[crm])}")

    def flush(self, crm: str, batch_size: int):
        with self.locks[crm]:
            batch = []
            while len(batch) and len(batch) < batch_size:
                batch.append(self.queues[crm].popleft())
            logger.info(f"Flushed batch of size {len(batch)} for CRM {crm}")
            return batch

    def get_pending(self, crm: str):
        with self.locks[crm]:
            return list(self.queues[crm])
