# Reflection

(Answers written against the four standard questions; if your handout words them differently, keep my answers but re-title them to match.)

**1. Which issues were easiest and hardest to fix?**
Easiest: the style findings (Flake8 E401/E501/E711, unused import) and the `random` to `secrets` swap, which were one-line changes. Hardest: the AES-ECB fix, because it was not a patch but a design change (a different library, a random nonce per message, and a key that has to be stored outside the code), and the XSS fix, because the correct answer was to stop building HTML from raw strings.

**2. Did the tools report false positives, and what did they miss?**
Mostly their findings were real, but severity is a judgement: Bandit flagged `assert` and `random` as issues, which is low risk in a throwaway script but real in billing code. More importantly, the tools missed the logic bugs entirely. Only running the program showed a negative invoice for the 150% coupon, a full refund after 25 of 30 days used, four "max 3" payment attempts, and a 14-day trial not ending on day 14. Pylint only hinted at the refund bug (return in `finally`, unused `days_used`).

**3. How would you integrate static analysis into a real workflow?**
Run Flake8, Pylint and Bandit as a pre-commit hook and again in CI on every pull request, failing the build on Bandit high/medium findings and on a Pylint score below an agreed threshold. Keep a small, reviewed list of suppressions (with a comment explaining each) rather than ignoring whole checks. Static analysis complements, not replaces, unit tests and code review.

**4. What improvements in quality, security and readability did you see?**
Security: no secrets in source, authenticated encryption, safe XML parsing, escaped HTML, constant-time signature check, and unpredictable coupon codes. Quality: the money and date logic now matches what the demo labels claim, and invalid input is rejected instead of producing silent wrong results. Readability: PEP 8 formatting, snake_case names, docstrings, and no code running on import make the file easier to read, test and reuse.
