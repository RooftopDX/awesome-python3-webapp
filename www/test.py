import asyncio
import orm as orm
from models import User, Blog, Comment

async def test():
    await orm.create_pool(user='root', password='root', db='awesome', loop=loop)

    u = User()

    result = await u.findAll()
    for r in result:
        print(r)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())