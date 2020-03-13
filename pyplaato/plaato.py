"""Fetch data from Plaato Airlock and Keg"""
from datetime import datetime

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
        self.beer_left_unit = attrs[self.Pins.BEER_LEFT_UNIT] or None
        self.volume_unit = attrs[self.Pins.VOLUME_UNIT] or None
        self.measure_unit = attrs[self.Pins.MEASURE_UNIT] or None
        self.name = attrs[self.Pins.BEER_NAME] or "Beer"
        self.__percent_beer_left = attrs[self.Pins.PERCENT_BEER_LEFT] or None
        self.__pouring = attrs[self.Pins.POURING]
        self.__beer_left = attrs[self.Pins.BEER_LEFT] or None
        self.__temperature = attrs[self.Pins.TEMPERATURE] or None
        self.__unit_type = attrs[self.Pins.UNIT_TYPE]
        self.__last_pour = attrs[self.Pins.LAST_POUR] or None
        self.__date = attrs[self.Pins.DATE] or None

    @property
    def date(self):
        if self.__date is not None:
            date = datetime.strptime(self.__date, "%m/%d/%Y")
            return datetime.timestamp(date)
        return None

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(self.__temperature, 2)

    @property
    def beer_left(self):
        if self.__beer_left is not None:
            return round(self.__beer_left, 2)

    @property
    def percent_beer_left(self):
        if self.__percent_beer_left is not None:
            return round(self.__percent_beer_left, 2)

    @property
    def last_pour(self):
        if self.__last_pour is not None:
            return round(self.__last_pour, 2)

    @property
    def pouring(self):
        """
        1 = Pouring
        255 = Not Pouring
        :return: True if 1 = Pouring else False
        """
        return self.__pouring is "1"

    class Pins(Enum):
        BEER_NAME = "v64"
        PERCENT_BEER_LEFT = "v48"
        POURING = "v49"
        BEER_LEFT = "v51"
        BEER_LEFT_UNIT = "v74"
        TEMPERATURE = "v56"
        UNIT_TYPE = "v71"
        MEASURE_UNIT = "v75"
        VOLUME_UNIT = "v82"
        LAST_POUR = "v59"
        DATE = "v67"


@dataclass
class PlaatoAirlock:
    """Class for holding a Plaato Keg"""

    def __init__(self, attrs):
        self.bmp = attrs[self.Pins.BPM] or None
        self.__temperature = float(attrs[self.Pins.TEMPERATURE]) or None

    def __repr__(self):
        return f"Plaato Airlock -> BMP: {self.bmp}, Temp: {self.temperature}"

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(self.__temperature, 2)

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
