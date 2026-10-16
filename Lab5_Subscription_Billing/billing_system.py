"""Subscription billing: trials, coupons, proration, refunds and webhooks."""
import calendar
import hashlib
import hmac
import html
import os
import secrets
from datetime import date

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml import ElementTree

PLANS = {"basic": 199, "pro": 499, "team": 999}
GST = 0.18
TRIAL_DAYS = 14
MAX_ATTEMPTS = 3
BILLING_PERIOD_DAYS = 30
# Secrets come from the environment, never from source code. The random
# fallbacks only keep the demo runnable; set the variables in real use.
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET") or secrets.token_hex(32)


def _load_card_key():
    """Return the 256-bit card key from CARD_KEY (hex) or a random one."""
    key_hex = os.environ.get("CARD_KEY")
    if key_hex:
        return bytes.fromhex(key_hex)
    return AESGCM.generate_key(bit_length=256)


CARD_KEY = _load_card_key()
SUBSCRIPTIONS = {}
COUPONS = {
    "WELCOME10": {"percent": 10, "expires": date(2026, 12, 31)},
    "FRIENDS150": {"percent": 150, "expires": date(2027, 1, 31)},
}


def subscribe(user, plan, start):
    """Create a trial subscription for a user."""
    SUBSCRIPTIONS[user] = {
        "plan": plan, "start": start, "status": "trial", "invoices": [],
    }
    return SUBSCRIPTIONS[user]


def is_trial_over(user, today):
    """Return True once the TRIAL_DAYS-day trial has fully elapsed."""
    return (today - SUBSCRIPTIONS[user]["start"]).days >= TRIAL_DAYS


def apply_coupon(amount, code, today=None):
    """Apply a valid, unexpired coupon; invalid coupons change nothing."""
    today = today or date.today()
    coupon = COUPONS.get(code)
    if coupon is None or today > coupon["expires"]:
        return amount
    if not 0 <= coupon["percent"] <= 100:
        return amount
    return round(amount - amount * coupon["percent"] / 100, 2)


def invoice_amount(user, code=None, today=None):
    """Return the plan price plus GST, minus any coupon, in rupees."""
    plan_price = PLANS[SUBSCRIPTIONS[user]["plan"]]
    with_tax = round(plan_price * (1 + GST), 2)
    return apply_coupon(with_tax, code, today)


def next_billing_date(current):
    """Return the same day next month, clamped to the month's last day."""
    year = current.year + current.month // 12
    month = current.month % 12 + 1
    day = min(current.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def prorate_upgrade(user, new_plan, today, period_end):
    """Switch plans and return the prorated extra charge."""
    old = PLANS[SUBSCRIPTIONS[user]["plan"]]
    new = PLANS[new_plan]
    days_left = max((period_end - today).days, 0)
    period_days = calendar.monthrange(period_end.year, period_end.month)[1]
    SUBSCRIPTIONS[user]["plan"] = new_plan
    return round((new - old) * days_left / period_days, 2)


def retry_payment(charge):
    """Call charge() up to MAX_ATTEMPTS times; return attempts used."""
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        if charge():
            return attempts
    return attempts


def cancel_refund(user, days_used):
    """Refund the unused part of the billing period."""
    price = PLANS[SUBSCRIPTIONS[user]["plan"]]
    unused = max(BILLING_PERIOD_DAYS - days_used, 0)
    return round(price * unused / BILLING_PERIOD_DAYS, 2)


def coupon_code():
    """Generate a random coupon code using a cryptographic RNG."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "SAVE-" + "".join(secrets.choice(alphabet) for _ in range(6))


def active_users():
    """Return users that have not been invoiced yet."""
    return {u for u, sub in SUBSCRIPTIONS.items() if not sub["invoices"]}


def encrypt_card(card_number):
    """Encrypt a card number with AES-GCM and a fresh random nonce."""
    nonce = secrets.token_bytes(12)
    sealed = AESGCM(CARD_KEY).encrypt(nonce, card_number.encode(), None)
    return (nonce + sealed).hex()


def verify_webhook(body, signature):
    """Check the HMAC signature in constant time."""
    expected = hmac.new(WEBHOOK_SECRET.encode(), body,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook(xml_bytes):
    """Parse a webhook body with a parser that blocks XXE attacks."""
    root = ElementTree.fromstring(xml_bytes)
    return {"event": root.findtext("event"), "user": root.findtext("user")}


def render_invoice(user, amount):
    """Render invoice HTML with all user data escaped."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    return (f"<h1>Invoice for {html.escape(user)}</h1>"
            f"<p>Total: Rs.{html.escape(str(amount))}</p>")


def always_failing_charge():
    """Simulate a payment that is always declined."""
    return False


def main():
    """Run a short demo of the billing functions."""
    subscribe("asha", "pro", date(2026, 9, 1))
    subscribe("<b onmouseover=alert(1)>ravi</b>", "basic", date(2026, 9, 20))
    print("Trial (14 days from 09-01) over on 09-15?",
          is_trial_over("asha", date(2026, 9, 15)))
    print("Pro invoice with WELCOME10:",
          invoice_amount("asha", "WELCOME10", date(2026, 10, 1)))
    print("Pro invoice with FRIENDS150:",
          invoice_amount("asha", "FRIENDS150", date(2026, 10, 1)))
    print("Coupon on its expiry day:",
          invoice_amount("asha", "WELCOME10", date(2026, 12, 31)))
    print("Next billing after 2026-10-15:",
          next_billing_date(date(2026, 10, 15)))
    print("Next billing after 2026-12-31:",
          next_billing_date(date(2026, 12, 31)))
    print("Refund after using 25 of 30 days:", cancel_refund("asha", 25))
    print("Upgrade pro->team with 10 days left in Feb:",
          prorate_upgrade("asha", "team", date(2027, 2, 18),
                          date(2027, 2, 28)))
    print("Payment attempts (max 3, always failing):",
          retry_payment(always_failing_charge))
    print("Same card, same ciphertext?",
          encrypt_card("4111111111111111") == encrypt_card("4111111111111111"))
    sig = hmac.new(WEBHOOK_SECRET.encode(), b"<x/>",
                   hashlib.sha256).hexdigest()
    print("Webhook verified:", verify_webhook(b"<x/>", sig))
    print("Webhook:", parse_webhook(
        b"<hook><event>paid</event><user>asha</user></hook>"))
    print("Invoice HTML:",
          render_invoice("<b onmouseover=alert(1)>ravi</b>", 199))
    print("Coupon:", coupon_code())


if __name__ == "__main__":
    main()
