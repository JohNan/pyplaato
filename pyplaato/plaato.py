"""Fetch data from Plaato Airlock and Keg"""
from json import JSONDecodeError
from typing import Optional

from aiohttp import ClientSession

import logging

from .models.airlock import PlaatoAirlock
from .models.device import PlaatoDevice, PlaatoDeviceType
from .models.keg import PlaatoKeg
from .models.pins import PinsBase
from .const import *


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
                .warning(f"Failed to get value for {errors}")

        return PlaatoKeg(result)

    async def get_airlock_data(self, session: ClientSession) -> PlaatoAirlock:
        """Fetch values for each pin"""
        result = {}
        for pin in PlaatoAirlock.pins():
            result[pin] = await self.fetch_data(session, pin)

        errors = Plaato._get_errors_as_string(result)
        if errors:
            logging.getLogger(__name__) \
                .warning(f"Failed to get value for {errors}")

        return PlaatoAirlock(result)

    async def fetch_data(self, session: ClientSession, pin: PinsBase):
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
                    .warning(f"Failed to decode json for pin {pin} - {e.msg}")
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
