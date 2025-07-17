import datetime


class StatusTracker:
    def __init__(self):
        self.start_time = datetime.datetime.utcnow()
        self.stats = {
            "queue_size": 0,
            "retries_pending": 0,
            "last_sync_success": None,
            "last_sync_failed": None,
            "total_synced": 0,
            "pollers_active": [],
        }

    def update_stat(self, key, value):
        self.stats[key] = value

    def increment(self, key, by=1):
        self.stats[key] += by

    def get_status(self):
        return {
            "uptime": str(datetime.datetime.utcnow() - self.start_time),
            "stats": self.stats,
        }


status_tracker = StatusTracker()
