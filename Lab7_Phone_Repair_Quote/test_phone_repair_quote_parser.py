"""
Lab 7 - Hypothesis fuzz tests for phone_repair_quote_parser.py
Name: Nidhi | SRN: PES1UG24AM919
Each test feeds arbitrary text (or None) to one function and fails if it crashes.
"""
from hypothesis import given, strategies as st
from phone_repair_quote_parser import mask_imei, parse_parts_order, parse_model


@given(st.text() | st.none())
def test_mask_imei_no_crash(s):
    try:
        result = mask_imei(s)
    except Exception as e:
        assert False, f"mask_imei crashed on {s!r}: {type(e).__name__}: {e}"
    # must return text and never reveal more than the last four characters
    assert isinstance(result, str)
    assert len(result.replace('*', '')) <= 4


@given(st.text() | st.none())
def test_parse_parts_order_no_crash(s):
    try:
        result = parse_parts_order(s)
    except Exception as e:
        assert False, f"parse_parts_order crashed on {s!r}: {type(e).__name__}: {e}"
    assert isinstance(result, dict)


@given(st.text() | st.none())
def test_parse_model_no_crash(s):
    try:
        result = parse_model(s)
    except Exception as e:
        assert False, f"parse_model crashed on {s!r}: {type(e).__name__}: {e}"
    assert isinstance(result, tuple) and len(result) == 2
