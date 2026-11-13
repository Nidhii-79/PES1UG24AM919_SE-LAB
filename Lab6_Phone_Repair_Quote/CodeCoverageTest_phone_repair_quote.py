"""
Lab 6 - Code (line) coverage tests for phone_repair_quote.py
Name: Nidhi S SRN: PES1UG24AM919
Goal : execute every line of the module at least once.
"""
import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------- starter examples ----------
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


# ---------- repair_quote ----------
def test_unknown_part_raises():
    with pytest.raises(ValueError):
        repair_quote("speaker", "budget", False, False)


def test_unknown_tier_raises():
    with pytest.raises(ValueError):
        repair_quote("screen", "midrange", False, False)


def test_flagship_screen_express():
    # (4000*2) + 600 labour + 500 express
    assert repair_quote("screen", "flagship", False, True) == 9100


def test_battery_under_warranty_free_part():
    # part cost waived, only labour 300
    assert repair_quote("battery", "budget", True, False) == 300


# ---------- repair_days ----------
def test_no_technician_free():
    assert repair_days("battery", True, 0) == 3


def test_screen_out_of_stock():
    assert repair_days("screen", False, 2) == 6


def test_battery_out_of_stock():
    assert repair_days("battery", False, 2) == 3


# ---------- trade_in_value ----------
def test_trade_in_invalid_price():
    with pytest.raises(ValueError):
        trade_in_value(0, 10, False)


def test_trade_in_too_old():
    assert trade_in_value(50000, 49, False) == 0


def test_trade_in_new_phone_cracked():
    # 60% of 50000 = 30000, halved = 15000
    assert trade_in_value(50000, 6, True) == 15000


def test_trade_in_mid_age():
    assert trade_in_value(50000, 18, False) == 20000


def test_trade_in_old_phone():
    assert trade_in_value(50000, 36, False) == 10000
