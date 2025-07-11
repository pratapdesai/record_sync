from typing import List, Dict

class SQLiteSource:
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name

    async def fetch_records(self) -> List[Dict]:
        # Dummy stub for testing
        return [
            {"record_id": 1, "name": "Alice"},
            {"record_id": 2, "name": "Bob"}
        ]
