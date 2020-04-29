"""Fetch data from Plaato Airlock and Keg"""
from datetime import datetime
from json import JSONDecodeError
from abc import ABC, abstractmethod
from typing import Optional

from aiohttp import ClientSession
from enum import Enum

import logging
import dateutil.parser

URL = "http://plaato.blynk.cc/{auth_token}/get"

# Temperature units
UNIT_TEMP_CELSIUS = "°C"
UNIT_TEMP_FAHRENHEIT = "°F"
UNIT_PERCENTAGE = "%"


class _PinsBase(str, Enum):
    """Base class"""


class PlaatoDeviceType(str, Enum):
    Airlock = "Airlock"
    Keg = "Keg"


class PlaatoDevice(ABC):
    @property
    @abstractmethod
    def device_type(self) -> PlaatoDeviceType:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def date(self) -> float:
        return datetime.now().timestamp()

    @property
    def firmware_version(self) -> str:
        return ""

    @property
    @abstractmethod
    def sensors(self) -> dict:
        """Convenience method for Home Assistant"""
        pass

    @property
    def binary_sensors(self) -> dict:
        """Convenience method for Home Assistant"""
        return {}

    @property
    def attributes(self) -> dict:
        """Convenience method for Home Assistant"""
        return {}

    @abstractmethod
    def get_sensor_name(self, pin: _PinsBase) -> str:
        """Convenience method for Home Assistant"""
        pass

    @abstractmethod
    def get_unit_of_measurement(self, pin: _PinsBase):
        """Convenience method to get unit of measurement for Home Assistant"""
        pass

    @staticmethod
    @abstractmethod
    def pins() -> list:
        pass


class PlaatoKeg(PlaatoDevice):
    """Class for holding a Plaato Keg"""

    device_type = PlaatoDeviceType.Keg

    def __init__(self, attrs):
        self.beer_left_unit = attrs.get(self.Pins.BEER_LEFT_UNIT, None)
        self.volume_unit = attrs.get(self.Pins.VOLUME_UNIT, None)
        self.mass_unit = attrs.get(self.Pins.MASS_UNIT, None)
        self.measure_unit = attrs.get(self.Pins.MEASURE_UNIT, None)
        self.og = attrs.get(self.Pins.OG, None)
        self.fg = attrs.get(self.Pins.FG, None)
        self.__mode = attrs.get(self.Pins.MODE, None)
        self.__firmware_version = attrs.get(self.Pins.FIRMWARE_VERSION, None)
        self.__leak_detection = attrs.get(self.Pins.LEAK_DETECTION, None)
        self.__abv = attrs.get(self.Pins.ABV, None)
        self.__name = attrs.get(self.Pins.BEER_NAME, "Beer")
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
    def date(self) -> float:
        if self.__date is not None:
            date = dateutil.parser.parse(self.__date)
            return datetime.timestamp(date)
        return super().date

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(float(self.__temperature), 1)

    @property
    def temperature_unit(self):
        if self.__temperature_unit is "1":
            return UNIT_TEMP_CELSIUS
        return UNIT_TEMP_FAHRENHEIT

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
    def last_pour_unit(self):
        if self.measure_unit is "1":
            return self.mass_unit
        return self.volume_unit

    @property
    def abv(self):
        if self.__abv is not None:
            return round(float(self.__abv), 2)

    @property
    def pouring(self):
        """
        0 = Not Pouring
        255 = Pouring
        :return: True if 255 = Pouring else False
        """
        return self.__pouring is "255"

    @property
    def leak_detection(self):
        """
        1 = Leaking
        0 = Not Leaking
        :return: True if 1 = Leaking else False
        """
        return self.__leak_detection is "1"

    @property
    def mode(self):
        """
        1 = Beer
        2 = Co2
        """
        return "Beer" if self.__mode is "1" else "Co2"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def firmware_version(self) -> str:
        return self.__firmware_version

    def get_sensor_name(self, pin: _PinsBase) -> str:
        names = {
            self.Pins.PERCENT_BEER_LEFT: "Percent Beer Left",
            self.Pins.POURING: "Pouring",
            self.Pins.BEER_LEFT: "Beer Left",
            self.Pins.TEMPERATURE: "Temperature",
            self.Pins.LAST_POUR: "Last Pour Amount",
            self.Pins.OG: "Original Gravity",
            self.Pins.FG: "Final Gravity",
            self.Pins.ABV: "Alcohol by Volume",
            self.Pins.LEAK_DETECTION: "Leaking",
            self.Pins.MODE: "Mode",
            self.Pins.DATE: "Keg Date",
            self.Pins.BEER_NAME: "Beer Name"
        }
        return names.get(pin, pin.name)

    @property
    def sensors(self) -> dict:
        return {
            self.Pins.PERCENT_BEER_LEFT: self.percent_beer_left,
            self.Pins.BEER_LEFT: self.beer_left,
            self.Pins.TEMPERATURE: self.temperature,
            self.Pins.LAST_POUR: self.last_pour
        }

    @property
    def binary_sensors(self) -> dict:
        return {
            self.Pins.LEAK_DETECTION: self.leak_detection,
            self.Pins.POURING: self.pouring,
        }

    @property
    def attributes(self) -> dict:
        return {
            self.get_sensor_name(self.Pins.BEER_NAME): self.name,
            self.get_sensor_name(self.Pins.DATE): datetime.fromtimestamp(self.date).strftime('%x'),
            self.get_sensor_name(self.Pins.MODE): self.mode,
            self.get_sensor_name(self.Pins.OG): self.og,
            self.get_sensor_name(self.Pins.FG): self.fg,
            self.get_sensor_name(self.Pins.ABV): self.abv
        }

    def get_unit_of_measurement(self, pin: _PinsBase):
        if pin == self.Pins.BEER_LEFT:
            return self.beer_left_unit
        if pin == self.Pins.TEMPERATURE:
            return self.temperature_unit
        if pin == self.Pins.LAST_POUR:
            return self.last_pour_unit
        if pin == self.Pins.ABV or pin == self.Pins.PERCENT_BEER_LEFT:
            return UNIT_PERCENTAGE

        return ""

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
        MASS_UNIT = "v73"
        VOLUME_UNIT = "v82"
        LAST_POUR = "v59"
        DATE = "v67"
        OG = "v65"
        FG = "v66"
        ABV = "v68"
        FIRMWARE_VERSION = "v93"
        LEAK_DETECTION = "v83"
        MODE = "v88"


class PlaatoAirlock(PlaatoDevice):
    """Class for holding a Plaato Airlock"""

    device_type = PlaatoDeviceType.Airlock

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

    @property
    def name(self) -> str:
        return "Airlock"

    def get_sensor_name(self, pin: _PinsBase) -> str:
        names = {
            self.Pins.BPM: "Bubbles per Minute",
            self.Pins.TEMPERATURE: "Temperature",
            self.Pins.BATCH_VOLUME: "Batch Volume",
            self.Pins.OG: "Original Gravity",
            self.Pins.SG: "Specific Gravity",
            self.Pins.ABV: "Alcohol by Volume",
            self.Pins.BUBBLES: "Bubbles",
            self.Pins.CO2_VOLUME: "CO2 Volume",
        }
        return names.get(pin, pin.name)

    @property
    def sensors(self) -> dict:
        return {
            self.Pins.BPM: self.bmp,
            self.Pins.TEMPERATURE: self.temperature,
            self.Pins.BATCH_VOLUME: self.batch_volume,
            self.Pins.OG: self.og,
            self.Pins.SG: self.sg,
            self.Pins.ABV: self.abv,
            self.Pins.BUBBLES: self.bubbles,
            self.Pins.CO2_VOLUME: self.co2_volume,
        }

    def get_unit_of_measurement(self, pin: _PinsBase):
        if pin == self.Pins.TEMPERATURE:
            return self.temperature_unit
        if pin == self.Pins.BATCH_VOLUME or self.Pins.CO2_VOLUME:
            return self.volume_unit
        if pin == self.Pins.BPM:
            return "bpm"
        if pin == self.Pins.ABV:
            return UNIT_PERCENTAGE

        return ""

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
        if not url:
            url = URL
        self.__url = url.replace('{auth_token}', auth_token)

    async def get_data(
            self, session: ClientSession,
            device_type: PlaatoDeviceType
    ) -> PlaatoDevice:
        if device_type == PlaatoDeviceType.Keg:
            return await self.get_keg_data(session)
        if device_type == PlaatoDeviceType.Airlock:
            return await self.get_airlock_data(session)

        pass

    async def get_keg_data(self, session: ClientSession) -> PlaatoKeg:
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoKeg.pins():
            result[pin] = await self.fetch_data(session, pin)

        errors = Plaato._get_errors_as_string(result)
        if errors:
            logging.getLogger(__name__) \
                .error(f"Failed to get values for {errors}")

        return PlaatoKeg(result)

    async def get_airlock_data(self, session: ClientSession) -> PlaatoAirlock:
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoAirlock.pins():
            result[pin] = await self.fetch_data(session, pin)

        errors = Plaato._get_errors_as_string(result)
        if errors:
            logging.getLogger(__name__) \
                .error(f"Failed to get values for {errors}")

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
                if Plaato._iterable(data):
                    if "error" in data:
                        logging.getLogger(__name__) \
                            .debug(f"Pin {pin.name} not found")
                    elif len(data) == 1:
                        result = data[0]
                else:
                    result = data

            except JSONDecodeError as e:
                logging.getLogger(__name__)\
                    .error(f"Failed to decode json for pin {pin} - {e.msg}")
            return result

    @staticmethod
    def _get_errors_as_string(result: dict) -> Optional[str]:
        errors = dict(filter(lambda elem: elem[1] is None, result.items()))
        if errors:
            return ', '.join(map(lambda elem: elem.name, errors.keys()))
        return None

    @staticmethod
    def _iterable(obj):
        try:
            iter(obj)
        except TypeError:
            return False
        else:
            return True
