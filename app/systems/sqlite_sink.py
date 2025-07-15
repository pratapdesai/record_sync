import aiosqlite

class SQLiteSink:
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name

    async def write_record(self, record: dict):
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?'] * len(record))
        values = list(record.values())

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"INSERT OR IGNORE INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                values
            )
            await db.commit()
