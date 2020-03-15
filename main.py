import argparse
import sys

import aiohttp
import asyncio

from pyplaato.plaato import Plaato


async def go(args):
    plaato = Plaato(args)
    headers = {}
    if args.api_key:
        headers["x-api-key"] = args.api_key

    async with aiohttp.ClientSession(headers=headers) as session:
        if args.device == 'keg' or args.device == 'both':
            keg = await plaato.get_keg_data(session)
            print(keg)
        if args.device == 'airlock' or args.device == 'both':
            airlock = await plaato.get_airlock_data(session)
            print(airlock)


def main():
    parser = argparse.ArgumentParser()
    required_argument = parser.add_argument_group('required arguments')
    required_argument.add_argument('-t', dest='auth_token',
                                   help='Auth token received from Plaato',
                                   required=True)
    required_argument.add_argument('-d',
                                   action='store',
                                   dest='device',
                                   choices=['keg','airlock', 'both'],
                                   required=True)
    required_argument.add_argument('-u', dest='url',
                                   help='Optional mock url')
    required_argument.add_argument('-k', dest='api_key',
                                   help='Optional header key for mock url')

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
