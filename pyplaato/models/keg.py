from datetime import datetime
from enum import Enum

import dateutil.parser

from .device import PlaatoDevice, PlaatoDeviceType
from .pins import PinsBase
from ..const import UNIT_TEMP_CELSIUS, UNIT_TEMP_FAHRENHEIT, UNIT_PERCENTAGE, \
    METRIC, UNIT_OZ, UNIT_ML


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
        self.__unit_type = attrs.get(self.Pins.UNIT_TYPE, None)
        self.__last_pour = attrs.get(self.Pins.LAST_POUR, None)
        self.__date = attrs.get(self.Pins.DATE, None)

    def __repr__(self):
        return f"{self.__class__.__name__} -> " \
               f"Beer Left: {self.beer_left}, " \
               f"Temp: {self.temperature}, " \
               f"Pouring: {self.pouring}"

    @property
    def date(self) -> float:
        if self.__date is not None and self.__date and not self.__date.isspace():
            date = dateutil.parser.parse(self.__date)
            return date.timestamp()
        return super().date

    @property
    def temperature(self):
        if self.__temperature is not None:
            return round(float(self.__temperature), 1)

    @property
    def temperature_unit(self):
        if self.__unit_type == METRIC:
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
        if self.__unit_type == METRIC:
            return UNIT_ML
        return UNIT_OZ

    @property
    def abv(self):
        if self.__abv is not None and not self.__abv:
            return round(float(self.__abv), 2)

    @property
    def pouring(self):
        """
        0 = Not Pouring
        255 = Pouring
        :return: True if 255 = Pouring else False
        """
        return self.__pouring == "255"

    @property
    def leak_detection(self):
        """
        1 = Leaking
        0 = Not Leaking
        :return: True if 1 = Leaking else False
        """
        return self.__leak_detection == "1"

    @property
    def mode(self):
        """
        1 = Beer
        2 = Co2
        """
        return "Beer" if self.__mode == "1" else "Co2"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def firmware_version(self) -> str:
        return self.__firmware_version

    def get_sensor_name(self, pin: PinsBase) -> str:
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

    def get_unit_of_measurement(self, pin: PinsBase):
        if pin == self.Pins.BEER_LEFT:
            return self.beer_left_unit
        if pin == self.Pins.TEMPERATURE:
            return self.temperature_unit
        if pin == self.Pins.LAST_POUR:
            return self.last_pour_unit
        if pin == self.Pins.ABV or pin == self.Pins.PERCENT_BEER_LEFT:
            return UNIT_PERCENTAGE

        return ""

    # noinspection PyTypeChecker
    @staticmethod
    def pins():
        return list(PlaatoKeg.Pins)

    class Pins(PinsBase, Enum):
        BEER_NAME = "v64"
        PERCENT_BEER_LEFT = "v48"
        POURING = "v49"
        BEER_LEFT = "v51"
        BEER_LEFT_UNIT = "v74"
        TEMPERATURE = "v56"
        UNIT_TYPE = "v71"
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
