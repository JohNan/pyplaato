"""Fetch data from Plaato Airlock and Keg"""
from aiohttp import ClientSession
from dataclasses import dataclass
from enum import Enum
import logging

PERCENT_BEER_LEFT = "v48"
POURING = "v49"
BEER_LEFT = "v51"
TEMPERATURE = "v56"
UNIT_TYPE = "v71"

KEG_PINS = [PERCENT_BEER_LEFT, POURING, BEER_LEFT, TEMPERATURE, UNIT_TYPE]
URL = "http://plaato.blynk.cc/{auth_token}/get"


class PlaatoType(Enum):
    Airlock = 1
    Keg = 2


@dataclass
class PlaatoKeg:
    """Class for holding a Plaato Keg"""

    def __init__(self, attrs):
        self.__percent_beer_left = attrs[self.Pins.PERCENT_BEER_LEFT]
        self.__pouring = attrs[self.Pins.POURING]
        self.__beer_left = attrs[self.Pins.BEER_LEFT]
        self.__temperature = attrs[self.Pins.TEMPERATURE]
        self.__unit_type = attrs[self.Pins.UNIT_TYPE]

    class Pins(Enum):
        PERCENT_BEER_LEFT = "v48"
        POURING = "v49"
        BEER_LEFT = "v51"
        TEMPERATURE = "v56"
        UNIT_TYPE = "v71"


@dataclass
class PlaatoAirlock:
    """Class for holding a Plaato Keg"""

    def __init__(self, attrs):
        self.__bmp = attrs[self.Pins.BPM] or None
        self.__temperature = float(attrs[self.Pins.TEMPERATURE]) or None

    def __repr__(self):
        return f"Plaato Airlock -> BMP: {self.bmp}, Temp: {self.temperature}"

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(self.__temperature, 2)

    @property
    def bmp(self):
        return self.__bmp

    class Pins(Enum):
        BPM = "v102"
        TEMPERATURE = "v103"


async def get_keg_data(session: ClientSession, auth_token: str):
    """Fetch values for each pin"""
    # url = URL.replace('{auth_token}', auth_token)
    url = "https://plaato.free.beeceptor.com"
    result = {}
    for pin in PlaatoKeg.Pins:
        result[pin] = await fetch_data(session, url, pin.value)

    return PlaatoKeg(result)


async def get_airlock_data(session: ClientSession, auth_token: str):
    """Fetch values for each pin"""
    # url = URL.replace('{auth_token}', auth_token)
    url = "https://plaato.free.beeceptor.com"
    result = {}
    for pin in PlaatoAirlock.Pins:
        result[pin] = await fetch_data(session, url, pin.value)

    return PlaatoAirlock(result)


async def fetch_data(session: ClientSession, url: str, pin: str):
    async with session.get(f"{url}/{pin}") as resp:
        data = await resp.json(content_type=None)
        return data[0] or None





