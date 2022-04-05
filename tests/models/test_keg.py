from datetime import datetime
from unittest import mock

from pyplaato.models.keg import PlaatoKeg


def test_date_prop_with_value_returns_its_timestamp():
    pins = PlaatoKeg.Pins
    keg = PlaatoKeg({pins.DATE: "1/1/2022"})
    assert 1641024000.0 == keg.date


@mock.patch("pyplaato.models.device.datetime")
def test_date_prop_with_no_value_returns_current_timestamp(m_datetime):
    now = datetime(2022, 10, 1)
    m_datetime.now.return_value = now
    keg = PlaatoKeg({})
    assert now.timestamp() == keg.date

