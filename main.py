import argparse
import aiohttp
import asyncio

from pyplaato.plaato import (
    PlaatoType,
    get_airlock_data,
    get_keg_data
)


async def go():
    async with aiohttp.ClientSession() as session:
        device = await get_airlock_data(session, "")
        keg = await get_keg_data(session, "")
        print(device)


loop = asyncio.get_event_loop()
loop.run_until_complete(go())
loop.close()
