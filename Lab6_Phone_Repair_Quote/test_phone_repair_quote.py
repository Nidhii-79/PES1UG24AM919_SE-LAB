import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value

#Example test cases:
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600

def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1

#Write the rest of the test cases so that the code is 90- 100% covered.
