"""Fetch data from Plaato Airlock and Keg"""
from datetime import datetime
from json import JSONDecodeError
from typing import Any

from aiohttp import ClientSession
from enum import Enum

import logging

URL = "http://plaato.blynk.cc/{auth_token}/get"

# Temperature units
TEMP_CELSIUS = "°C"
TEMP_FAHRENHEIT = "°F"


class _PinsBase(str, Enum):
    """Base class"""


class PlaatoDevice(str, Enum):
    Airlock = "Airlock"
    Keg = "Keg"


class PlaatoKeg:
    """Class for holding a Plaato Keg"""

    def __init__(self, attrs):
        self.beer_left_unit = attrs.get(self.Pins.BEER_LEFT_UNIT, None)
        self.volume_unit = attrs.get(self.Pins.VOLUME_UNIT, None)
        self.measure_unit = attrs.get(self.Pins.MEASURE_UNIT, None)
        self.name = attrs.get(self.Pins.BEER_NAME, "Beer")
        self.__percent_beer_left = attrs.get(self.Pins.PERCENT_BEER_LEFT, None)
        self.__pouring = attrs.get(self.Pins.POURING, False)
        self.__beer_left = attrs.get(self.Pins.BEER_LEFT, None)
        self.__temperature = attrs.get(self.Pins.TEMPERATURE, None)
        self.__temperature_unit = attrs.get(self.Pins.TEMPERATURE_UNIT, None)
        self.__last_pour = attrs.get(self.Pins.LAST_POUR, None)
        self.__date = attrs.get(self.Pins.DATE, None)

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
        if self.__temperature_unit is "1":
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

    def get_attrs(self):
        """Convenience method for Home Assistant"""
        return {
            self.Pins.BEER_NAME: self.name,
            self.Pins.PERCENT_BEER_LEFT: self.percent_beer_left,
            self.Pins.POURING: self.pouring,
            self.Pins.BEER_LEFT: self.beer_left,
            self.Pins.BEER_LEFT_UNIT: self.beer_left_unit,
            self.Pins.TEMPERATURE: self.temperature,
            self.Pins.TEMPERATURE_UNIT: self.temperature_unit,
            self.Pins.MEASURE_UNIT: self.measure_unit,
            self.Pins.VOLUME_UNIT: self.volume_unit,
            self.Pins.LAST_POUR: self.last_pour,
            self.Pins.DATE: self.date,
        }

    @staticmethod
    def pins():
        return list(PlaatoKeg.Pins)

    class Pins(_PinsBase, Enum):
        BEER_NAME = "v64"
        PERCENT_BEER_LEFT = "v48"
        POURING = "v49"
        BEER_LEFT = "v51"
        BEER_LEFT_UNIT = "v74"
        TEMPERATURE = "v56"
        TEMPERATURE_UNIT = "v71"
        MEASURE_UNIT = "v75"
        VOLUME_UNIT = "v82"
        LAST_POUR = "v59"
        DATE = "v67"


class PlaatoAirlock:
    """Class for holding a Plaato Airlock"""

    def __init__(self, attrs):
        self.bmp = attrs.get(self.Pins.BPM, None)
        self.temperature_unit = attrs.get(self.Pins.TEMPERATURE_UNIT, None)
        self.volume_unit = attrs.get(self.Pins.VOLUME_UNIT, None)
        self.bubbles = attrs.get(self.Pins.BUBBLES, None)
        self.batch_volume = attrs.get(self.Pins.BATCH_VOLUME, None)
        self.__sg = attrs.get(self.Pins.SG, None)
        self.__og = attrs.get(self.Pins.OG, None)
        self.__abv = attrs.get(self.Pins.ABV, None)
        self.__co2_volume = attrs.get(self.Pins.CO2_VOLUME, None)
        self.__temperature = attrs.get(self.Pins.TEMPERATURE, None)

    def __repr__(self):
        return (f"{self.__class__.__name__} -> "
                f"BMP: {self.bmp}, "
                f"Temp: {self.temperature}")

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

    def get_attrs(self):
        """Convenience method for Home Assistant"""
        return {
            self.Pins.BPM: self.bmp,
            self.Pins.TEMPERATURE: self.temperature,
            self.Pins.BATCH_VOLUME: self.batch_volume,
            self.Pins.OG: self.og,
            self.Pins.SG: self.sg,
            self.Pins.ABV: self.abv,
            self.Pins.TEMPERATURE_UNIT: self.temperature_unit,
            self.Pins.VOLUME_UNIT: self.volume_unit,
            self.Pins.BUBBLES: self.bubbles,
            self.Pins.CO2_VOLUME: self.co2_volume,
        }

    @staticmethod
    def pins():
        return list(PlaatoAirlock.Pins)

    class Pins(_PinsBase, Enum):
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

    def __init__(self, auth_token="NO_AUTH_TOKEN", url=URL, headers=None):
        if headers is None:
            headers = {}
        self.__headers = headers
        self.__url = url.replace('{auth_token}', auth_token)

    async def get_keg_data(self, session: ClientSession):
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoKeg.pins():
            result[pin] = await self.fetch_data(session, pin)

        return PlaatoKeg(result)

    async def get_airlock_data(self, session: ClientSession):
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoAirlock.pins():
            result[pin] = await self.fetch_data(session, pin)

        return PlaatoAirlock(result)

    async def fetch_data(self, session: ClientSession, pin: _PinsBase):
        """Fetches the data for a specific pin"""
        async with session.get(
                url=f"{self.__url}/{pin.value}",
                headers=self.__headers
        ) as resp:
            result = None
            try:
                data = await resp.json(content_type=None)
                if "error" in data:
                    logging.getLogger(__name__) \
                        .error(f"Pin {pin.name} not found")
                elif len(data) == 1:
                    result = data[0]

            except JSONDecodeError as e:
                logging.getLogger(__name__)\
                    .error(f"Failed to decode json for pin {pin} - {e.msg}")
            return result or None
