# Issues found in `billing_system.py`

Severity order: High, then Medium, then Low. Line numbers refer to the ORIGINAL file.
Type: Security / Bug (logic) / Quality / Style.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Hardcoded secrets (Bandit B105/B106) | Security (High) | 13-14 | `WEBHOOK_SECRET` and `CARD_KEY` are written in the source, so anyone with repo access can forge webhooks and decrypt card data. | Read both from environment variables (`os.environ`); random fallback only for the demo. |
| Insecure AES-ECB mode + `pycrypto` import (Bandit B413) | Security (High) | 8, 70-72 | ECB encrypts equal blocks to equal ciphertext (the demo prints `True` for "same ciphertext"), leaks patterns, has no integrity check; card was padded with spaces. | Use AES-GCM from `cryptography` with a fresh random 12-byte nonce per encryption; no manual padding. |
| XXE-vulnerable XML parsing (Bandit B320/B410) | Security (High) | 5, 79 | `lxml.etree.fromstring` on untrusted webhook bytes can allow external entity / entity-expansion attacks. | Parse with `defusedxml.ElementTree.fromstring`. |
| XSS via Mako template (Bandit B702) | Security (High) | 6, 83-84 | Username is injected into HTML unescaped; `<b onmouseover=alert(1)>` runs script in the browser. | Escape every value with `html.escape` and build the string with an f-string; drop Mako. |
| Weak RNG for coupon codes (Bandit B311) | Security (Low) | 61 | `random` is predictable, so coupon codes can be guessed. | Use `secrets.choice`. |
| `assert` used for validation (Bandit B101) | Security (Low) | 83 | Asserts are removed under `python -O`, so the negative-amount check vanishes. | Raise `ValueError` explicitly. |
| Non-constant-time signature compare | Security (Medium) | 77 | `expected == signature` leaks timing information. | Use `hmac.compare_digest`. |
| Coupon over 100% | Bug | 21-22 | `FRIENDS150` gives 150% off, producing a NEGATIVE invoice (-294.41). | Reject coupons outside 0-100%; round to 2 decimals. |
| `return` inside `finally` + dead code (Pylint W0150, W0101) | Bug | 53-57 | `return` in `finally` swallows exceptions; the `print` after it never runs; `days_used` is ignored so a user who used 25 of 30 days gets a FULL refund (999). | Remove try/finally; refund = price x unused days / 30. |
| Retry loop off by one | Bug | 45-50 | `while attempts <= MAX_ATTEMPTS` makes 4 attempts when the max is 3. | Use `<`. |
| Coupon expires a day early | Bug | 28 | `today >= expires` rejects the coupon ON its expiry day, which is the last valid day. | Use `today > expires`. |
| Trial end off by one | Bug | 18 | `> TRIAL_DAYS` says a 14-day trial from 09-01 is NOT over on 09-15. | Use `>= TRIAL_DAYS`. |
| Month rollover crash | Bug | 35 | `replace(month=month+1)` raises `ValueError` in December and on days like 31 Jan. | Compute next month/year and clamp the day with `calendar.monthrange`. |
| Hardcoded 30-day proration | Bug | 42 | February has 28 days, so the upgrade charge is wrong (166.67 vs 178.57); negative days_left not handled. | Use the real days in the period; `max(days_left, 0)`. |
| `today=None` default crashes | Bug | 25-31 | Calling `invoiceAmount(user, code)` with a coupon compares `None` to a date. | Default `today` to `date.today()`. |
| `== None` / `== []` (Flake8 E711, Pylint C0121) | Style | 24, 66 | Comparison to `None` / empty list with `==`. | Use `is None` and `not sub["invoices"]`. |
| Unused / combined imports (Flake8 E401, F401; Pylint W0611) | Style | 1 | `import os, sys` on one line; `sys` unused. | One import per line, remove unused. |
| Lines > 79 chars (Flake8 E501) | Style | many | Long `print` and `subscriptions[...]` lines. | Wrap lines. |
| Missing blank lines (Flake8 E302/E305) | Style | all functions | Only one blank line between functions; code at module end. | Two blank lines; `if __name__ == "__main__":`. |
| camelCase names, no docstrings (Pylint C0103, C0114, C0116) | Quality | all | Functions are camelCase; module and functions have no docstrings; module-level dicts named like variables. | snake_case, docstrings, UPPER_CASE for module-level state. |
| `dict()`, `list()`, `set([...])` (Pylint R1735, R1718) | Quality | 14, 17, 66 | Unneeded constructor calls. | Use `{}`, `[]`, and a set comprehension. |
| Demo runs on import | Quality | 100 | `main()` runs when the file is imported. | `if __name__ == "__main__":` guard. |
