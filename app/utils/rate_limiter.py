import time
from collections import defaultdict
from threading import Lock


class SlidingWindowRateLimiter:
    max_requests = 0
    window = 0

    def __init__(self):
        self.timestamps = defaultdict(list)
        self.lock = Lock()

    def allow(self, key: str):
        now = time.time()
        with self.lock:
            timestamps = self.timestamps[key]
            # remove timestamps outside window
            self.timestamps[key] = [ts for ts in timestamps if now - ts <= SlidingWindowRateLimiter.window]
            if len(self.timestamps[key]) < SlidingWindowRateLimiter.max_requests:
                self.timestamps[key].append(now)
                return True
            else:
                return False
