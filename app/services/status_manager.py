from threading import Lock

class StatusManager:
    def __init__(self):
        self.status_store = {}
        self.lock = Lock()

    def set_status(self, record_id: str, status: str):
        with self.lock:
            self.status_store[record_id] = status

    def get_status(self, record_id: str) -> str:
        with self.lock:
            return self.status_store.get(record_id, "unknown")
