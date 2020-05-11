from abc import abstractmethod, ABC
from datetime import datetime
from enum import Enum

from .pins import PinsBase


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
    def get_sensor_name(self, pin: PinsBase) -> str:
        """Convenience method for Home Assistant"""
        pass

    @abstractmethod
    def get_unit_of_measurement(self, pin: PinsBase):
        """Convenience method to get unit of measurement for Home Assistant"""
        pass

    @staticmethod
    @abstractmethod
    def pins() -> list:
        pass
