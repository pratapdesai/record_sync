import json
from app.systems.base import BaseSystem
from app.core.logger import logger
from typing import List, Dict
import os
import uuid
from datetime import datetime


class FileSource(BaseSystem):
    def __init__(self, path: str):
        self.path = path
        self.synced_ids = set()

    async def fetch_records(self) -> List[Dict]:
        logger.info(f"Reading from file: {self.path}")
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r") as f:
            return json.load(f)

    async def write_record(self, record: Dict):
        raise NotImplementedError("FileSource is read-only")

    async def fetch_new_records(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r") as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

        new = []
        for r in records:
            rid = r.get("record_id")
            if rid and rid not in self.synced_ids:
                self.synced_ids.add(rid)
                new.append(r)
        return new


class FileSink(BaseSystem):
    def __init__(self, path: str):
        self.path = path

    async def fetch_records(self) -> List[Dict]:
        raise NotImplementedError("FileSink is write-only")

    async def write_record(self, record: Dict, allow_duplicates: bool = False):
        existing = []
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []

        if not allow_duplicates:
            record_ids = {r.get("record_id") for r in existing if "record_id" in r}
            if record["record_id"] in record_ids:
                logger.info(f"[Dedup] Skipping already synced record {record['record_id']}")
                return

        existing.append(record)
        with open(self.path, "w") as f:
            json.dump(existing, f, indent=2)

        logger.info(f"Wrote record {record['record_id']} to {self.path}")
