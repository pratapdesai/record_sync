import time
from threading import Lock

class CircuitBreaker:
    """
    A simple thread-safe circuit breaker
    """

    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = None
        self.lock = Lock()

    def allow_request(self) -> bool:
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    # move to half-open
                    self.state = "HALF-OPEN"
                    return True
                return False
            return True

    def record_success(self):
        with self.lock:
            if self.state in ["OPEN", "HALF-OPEN"]:
                self.state = "CLOSED"
            self.failure_count = 0
            self.last_failure_time = None

    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()
