from datetime import datetime
import datetime


class Request:
    def __init__(self, conn):
        self.conn = conn

    async def db_get_categories(self):
        query = "SELECT DISTINCT category FROM table_market ORDER BY category ASC"

        rows = await self.conn.execute(query)
        results = await rows.fetchall()
        lst = [result[0] for result in results]
        return lst
