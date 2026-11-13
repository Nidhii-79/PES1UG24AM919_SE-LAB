"""
Lab 6 - Branch coverage tests for phone_repair_quote.py
Name : Nidhi S | SRN: PES1UG24AM919
Goal : make every decision (if / elif / else) evaluate to BOTH True and False,
       including boundary values and each side of compound conditions.
"""
import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------- starter examples ----------
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


# ================= repair_quote =================
# validation branches
def test_unknown_part_raises():
    with pytest.raises(ValueError, match="unknown part"):
        repair_quote("speaker", "budget", False, False)


def test_unknown_tier_raises():
    with pytest.raises(ValueError, match="unknown brand tier"):
        repair_quote("screen", "midrange", False, False)


# brand tier: flagship (True) vs budget (False)
def test_flagship_screen_no_express():
    assert repair_quote("screen", "flagship", False, False) == 8600


def test_budget_battery_no_warranty():
    # 1500 + 300 labour
    assert repair_quote("battery", "budget", False, False) == 1800


def test_flagship_camera_no_warranty():
    # 2500*2 + 300 labour
    assert repair_quote("camera", "flagship", False, False) == 5300


# part == "screen" (True) vs else (False) -> labour 600 vs 300
def test_charging_port_labour_300():
    assert repair_quote("charging_port", "budget", False, False) == 1100


# warranty branches: (warranty & non-screen) True; warranty & screen False; no warranty False
def test_warranty_non_screen_part_free():
    assert repair_quote("battery", "budget", True, False) == 300


def test_warranty_flagship_camera_part_free():
    assert repair_quote("camera", "flagship", True, False) == 300


def test_warranty_does_not_cover_screen():
    # screen is excluded from warranty: 4000 + 600
    assert repair_quote("screen", "budget", True, False) == 4600


# express branches: True vs False
def test_express_surcharge_applied():
    assert repair_quote("screen", "flagship", False, True) == 9100


def test_express_with_warranty_battery():
    assert repair_quote("battery", "budget", True, True) == 800


def test_no_express_no_surcharge():
    assert repair_quote("charging_port", "flagship", False, False) == 1900


# ================= repair_days =================
# technicians_free == 0 (True) vs != 0 (False)
def test_no_technician_in_stock():
    assert repair_days("battery", True, 0) == 3


def test_technician_available_in_stock():
    assert repair_days("screen", True, 1) == 1


# parts_in_stock False; part is screen / camera / other
def test_screen_out_of_stock_tech_free():
    assert repair_days("screen", False, 2) == 6


def test_camera_out_of_stock_tech_free():
    # first operand of 'or' is False, second True
    assert repair_days("camera", False, 2) == 6


def test_battery_out_of_stock_tech_free():
    assert repair_days("battery", False, 2) == 3


def test_charging_port_out_of_stock_no_tech():
    assert repair_days("charging_port", False, 0) == 5


def test_screen_out_of_stock_no_tech():
    assert repair_days("screen", False, 0) == 8


# ================= trade_in_value =================
# invalid input: each side of the 'or'
def test_trade_in_zero_price():
    with pytest.raises(ValueError, match="invalid input"):
        trade_in_value(0, 10, False)


def test_trade_in_negative_price():
    with pytest.raises(ValueError):
        trade_in_value(-100, 10, False)


def test_trade_in_negative_age():
    with pytest.raises(ValueError):
        trade_in_value(50000, -1, False)


# age > 48 boundary
def test_trade_in_age_49_is_worthless():
    assert trade_in_value(50000, 49, False) == 0


def test_trade_in_age_48_still_valued():
    assert trade_in_value(50000, 48, False) == 10000


# age <= 12 boundaries
def test_trade_in_age_0():
    assert trade_in_value(50000, 0, False) == 30000


def test_trade_in_age_12_boundary():
    assert trade_in_value(50000, 12, False) == 30000


# 12 < age <= 24 boundaries
def test_trade_in_age_13():
    assert trade_in_value(50000, 13, False) == 20000


def test_trade_in_age_24_boundary():
    assert trade_in_value(50000, 24, False) == 20000


# age > 24
def test_trade_in_age_25():
    assert trade_in_value(50000, 25, False) == 10000


# screen_cracked True vs False
def test_trade_in_cracked_screen_halves_value():
    assert trade_in_value(50000, 6, True) == 15000


def test_trade_in_cracked_older_phone():
    assert trade_in_value(50000, 30, True) == 5000


def test_trade_in_integer_division():
    # 999*60//100 = 599, cracked -> 299
    assert trade_in_value(999, 0, False) == 599
    assert trade_in_value(999, 0, True) == 299
