from enum import Enum

from ..const import *
from .device import PlaatoDevice, PlaatoDeviceType
from .pins import PinsBase


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
        self.og = attrs.get(self.Pins.OG, None)
        self.__abv = attrs.get(self.Pins.ABV, None)
        self.__co2_volume = attrs.get(self.Pins.CO2_VOLUME, None)
        self.__temperature = attrs.get(self.Pins.TEMPERATURE, None)

    def __repr__(self):
        return (f"{self.__class__.__name__} -> "
                f"BMP: {self.bmp}, "
                f"Temp: {self.temperature}")

    @classmethod
    def from_web_hook(cls, data):
        attrs = {
            PlaatoAirlock.Pins.BPM: data.get(ATTR_BPM, None),
            PlaatoAirlock.Pins.TEMPERATURE_UNIT: data.get(ATTR_TEMP_UNIT,None),
            PlaatoAirlock.Pins.VOLUME_UNIT: data.get(ATTR_VOLUME_UNIT,None),
            PlaatoAirlock.Pins.BUBBLES: data.get(ATTR_BUBBLES, None),
            PlaatoAirlock.Pins.BATCH_VOLUME: data.get(ATTR_BATCH_VOLUME,None),
            PlaatoAirlock.Pins.SG: data.get(ATTR_SG, None),
            PlaatoAirlock.Pins.OG: data.get(ATTR_OG, None),
            PlaatoAirlock.Pins.ABV: data.get(ATTR_ABV, None),
            PlaatoAirlock.Pins.CO2_VOLUME: data.get(ATTR_CO2_VOLUME,None),
            PlaatoAirlock.Pins.TEMPERATURE: data.get(ATTR_TEMP, None)
        }
        return PlaatoAirlock(attrs)

    @property
    def temperature(self):
        if self.__temperature is not None:
            try:
                return round(float(self.__temperature), 1)
            except ValueError:
                return self.__temperature

    @property
    def abv(self):
        if self.__abv is not None:
            return round(float(self.__abv), 2)

    @property
    def sg(self):
        if self.__sg is not None:
            return round(float(self.__sg), 3)

    @property
    def co2_volume(self):
        if self.__co2_volume is not None:
            return round(float(self.__co2_volume), 2)

    @property
    def name(self) -> str:
        return "Airlock"

    def get_sensor_name(self, pin: PinsBase) -> str:
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

    def get_unit_of_measurement(self, pin: PinsBase):
        if pin == self.Pins.TEMPERATURE:
            return self.temperature_unit
        if pin == self.Pins.BATCH_VOLUME or pin == self.Pins.CO2_VOLUME:
            return self.volume_unit
        if pin == self.Pins.BPM:
            return UNIT_BUBBLES_PER_MINUTE
        if pin == self.Pins.ABV:
            return UNIT_PERCENTAGE

        return ""

    # noinspection PyTypeChecker
    @staticmethod
    def pins():
        return list(PlaatoAirlock.Pins)

    class Pins(PinsBase, Enum):
        BPM = "v102"
        TEMPERATURE = "v103"
        BATCH_VOLUME = "v104"
        OG = "v105"
        SG = "v106"
        ABV = "v107"
        TEMPERATURE_UNIT = "v108"
        VOLUME_UNIT = "v109"
        BUBBLES = "v110"
        CO2_VOLUME = "v119"
