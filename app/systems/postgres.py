class PostgresSource:
    def __init__(self, dsn: str, table: str):
        self.dsn = dsn
        self.table = table

    async def fetch_records(self):
        # Dummy implementation for now
        return []
