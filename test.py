import asyncio

loop = asyncio.get_event_loop()


async def count():
    for i in range(10):
        print(i)
        yield
