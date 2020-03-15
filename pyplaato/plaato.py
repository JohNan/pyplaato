"""Fetch data from Plaato Airlock and Keg"""
from datetime import datetime
from json import JSONDecodeError

from aiohttp import ClientSession
from dataclasses import dataclass
from enum import Enum
import logging

URL = "http://plaato.blynk.cc/{auth_token}/get"

# Temperature units
TEMP_CELSIUS = "°C"
TEMP_FAHRENHEIT = "°F"


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

    def __repr__(self):
        return f"{self.__class__.__name__} -> " \
               f"Bear Left: {self.beer_left}, " \
               f"Temp: {self.temperature}, " \
               f"Pouring: {self.pouring}"

    @property
    def date(self):
        if self.__date is not None:
            date = datetime.strptime(self.__date, "%m/%d/%Y")
            return datetime.timestamp(date)
        return None

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(float(self.__temperature), 1)

    @property
    def temperature_unit(self):
        if self.__unit_type is "1":
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def beer_left(self):
        if self.__beer_left is not None:
            return round(float(self.__beer_left), 2)

    @property
    def percent_beer_left(self):
        if self.__percent_beer_left is not None:
            return round(self.__percent_beer_left, 2)

    @property
    def last_pour(self):
        if self.__last_pour is not None:
            return round(float(self.__last_pour), 2)

    @property
    def pouring(self):
        """
        0 = Pouring
        255 = Not Pouring
        :return: True if 1 = Pouring else False
        """
        return self.__pouring is "0"

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
    """Class for holding a Plaato Airlock"""

    def __init__(self, attrs):
        self.bmp = attrs[self.Pins.BPM] or None
        self.temperature_unit = attrs[self.Pins.TEMPERATURE_UNIT]
        self.volume_unit = attrs[self.Pins.VOLUME_UNIT]
        self.bubbles = attrs[self.Pins.BUBBLES]
        self.batch_volume = attrs[self.Pins.BATCH_VOLUME]
        self.__sg = attrs[self.Pins.ABV] or None
        self.__og = attrs[self.Pins.ABV] or None
        self.__abv = attrs[self.Pins.ABV] or None
        self.__co2_volume = attrs[self.Pins.ABV] or None
        self.__temperature = attrs[self.Pins.TEMPERATURE] or None

    def __repr__(self):
        return f"{self.__class__.__name__} -> BMP: {self.bmp}, Temp: {self.temperature}"

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(float(self.__temperature), 1)

    @property
    def abv(self):
        if self.__abv is not None:
            return round(float(self.__abv), 2)

    @property
    def sg(self):
        if self.__sg is not None:
            return round(float(self.__sg), 2)

    @property
    def og(self):
        if self.__og is not None:
            return round(float(self.__og), 2)

    @property
    def co2_volume(self):
        if self.__co2_volume is not None:
            return round(float(self.__co2_volume), 2)

    class Pins(Enum):
        BPM = "v102"
        TEMPERATURE = "v103"
        BATCH_VOLUME = "v104"
        OG = "v105"
        SG = "v106"
        ABV = "107"
        TEMPERATURE_UNIT = "v108"
        VOLUME_UNIT = "v109"
        BUBBLES = "v110"
        CO2_VOLUME = "v119"


class Plaato(object):
    """Represents a Plaato device"""

    def __init__(self, args):
        self.__url = (args.url or URL)\
            .replace('{auth_token}', (args.auth_token or "NO_AUTH_TOKEN"))

    async def get_keg_data(self, session: ClientSession):
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoKeg.Pins:
            result[pin] = await self.fetch_data(session, pin.value)

        return PlaatoKeg(result)

    async def get_airlock_data(self, session: ClientSession):
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoAirlock.Pins:
            result[pin] = await self.fetch_data(session, pin.value)

        return PlaatoAirlock(result)

    async def fetch_data(self, session: ClientSession, pin: str):
        """Fetches the data for a specific pin"""
        async with session.get(f"{self.__url}/{pin}") as resp:
            result = None
            try:
                data = await resp.json(content_type=None)
                if "error" in data:
                    logging.getLogger(__name__) \
                        .error(f"Pin {pin} not found")
                elif len(data) == 1:
                    result = data[0]

            except JSONDecodeError as e:
                logging.getLogger(__name__)\
                    .error(f"Failed to decode json for pin {pin}")
            return result or None
