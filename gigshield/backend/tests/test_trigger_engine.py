"""
Trigger Engine Tests — verifies MSC signal counting and event logic.
"""

import pytest
from backend.services.trigger_engine import count_confirmed_signals, determine_msc_status


def test_msc_standard_2_signals():
    """Rain + AQI both above threshold → MSC standard confirmed"""
    signals = {
        "rainfall_mm_hr": 14.2,
        "aqi_value": 218,
        "order_drop_pct": 0.20,
    }
    count = count_confirmed_signals(signals)
    assert count == 2
    assert determine_msc_status(count) == "standard"


def test_msc_high_3_signals():
    """Rain + AQI + Order Drop all above threshold → MSC high confirmed"""
    signals = {
        "rainfall_mm_hr": 18.5,
        "aqi_value": 240,
        "order_drop_pct": 0.52,
    }
    count = count_confirmed_signals(signals)
    assert count == 3
    assert determine_msc_status(count) == "high"


def test_msc_not_met_1_signal():
    """Only rain above threshold → MSC not met"""
    signals = {
        "rainfall_mm_hr": 12.0,
        "aqi_value": 100,
        "order_drop_pct": 0.10,
    }
    count = count_confirmed_signals(signals)
    assert count == 1
    assert determine_msc_status(count) == "not_met"


def test_msc_not_met_zero():
    """No signals above threshold → MSC not met"""
    signals = {
        "rainfall_mm_hr": 3.0,
        "aqi_value": 80,
        "order_drop_pct": 0.05,
    }
    count = count_confirmed_signals(signals)
    assert count == 0
    assert determine_msc_status(count) == "not_met"


def test_msc_order_drop_counts():
    """Order drop + AQI → 2 signals (MSC standard)"""
    signals = {
        "rainfall_mm_hr": 2.0,
        "aqi_value": 220,
        "order_drop_pct": 0.45,
    }
    count = count_confirmed_signals(signals)
    assert count == 2
    assert determine_msc_status(count) == "standard"
