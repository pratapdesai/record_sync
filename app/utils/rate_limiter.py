import time
from collections import defaultdict
from threading import Lock

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.timestamps = defaultdict(list)
        self.lock = Lock()

    def allow(self, key: str):
        now = time.time()
        with self.lock:
            timestamps = self.timestamps[key]
            # remove timestamps outside window
            self.timestamps[key] = [ts for ts in timestamps if now - ts <= self.window]
            if len(self.timestamps[key]) < self.max_requests:
                self.timestamps[key].append(now)
                return True
            else:
                return False
