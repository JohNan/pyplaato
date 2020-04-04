import argparse
import sys

import aiohttp
import asyncio

from pyplaato.plaato import Plaato


async def go(args):
    headers = {}
    if args.api_key:
        headers["x-api-key"] = args.api_key
    plaato = Plaato(args.auth_token, args.url, headers)

    async with aiohttp.ClientSession() as session:
        if args.device == 'keg':
            keg = await plaato.get_keg_data(session)
            for key, attr in keg.get_attrs().items():
                print(f"{key.name} -> {attr}")
        if args.device == 'airlock':
            airlock = await plaato.get_airlock_data(session)
            for key, attr in airlock.get_attrs().items():
                print(f"{key.name} -> {attr}")


def main():
    parser = argparse.ArgumentParser()
    required_argument = parser.add_argument_group('required arguments')
    optional_argument = parser.add_argument_group('optional arguments')
    required_argument.add_argument('-t', dest='auth_token',
                                   help='Auth token received from Plaato',
                                   required=True)
    required_argument.add_argument('-d',
                                   action='store',
                                   dest='device',
                                   choices=['keg', 'airlock'],
                                   required=True)
    optional_argument.add_argument('-u', dest='url',
                                   help='Mock url')
    optional_argument.add_argument('-k', dest='api_key',
                                   help='Header key for mock url')

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go(args))
    loop.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborting..')
        sys.exit(1)
