import asyncpg


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_data(self, user_id, **kwargs):
        keys = ''
        values = ''
        update = ''

        for k, v in kwargs.items():
            keys += f"{k}, "
            values += f"'{v}', "
            update += f"{k} = '{v}', "
        print(13, keys.rstrip(', '))
        query = (f"INSERT INTO salesfunnel (user_id, {keys.rstrip(', ')}) VALUES ('{user_id}', {values.rstrip(', ')})"
                 f" ON CONFLICT (user_id) DO UPDATE SET {update.rstrip(', ')}")
        return await self.connector.execute(query)
