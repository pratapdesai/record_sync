from typing import List, Dict


class SQLiteSource:
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name
        self.synced_ids = set()

    async def fetch_records(self) -> List[Dict]:
        # Dummy stub for testing
        return [
            {"record_id": 1, "name": "Alice"},
            {"record_id": 2, "name": "Bob"}
        ]

    async def fetch_new_records(self) -> List[Dict]:
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"SELECT * FROM {self.table_name}")
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        new_records = []
        for row in rows:
            record = dict(zip(columns, row))
            rid = record.get("record_id")
            if rid and rid not in self.synced_ids:
                new_records.append(record)
                self.synced_ids.add(rid)

        return new_records
