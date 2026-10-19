# Repository instructions

These instructions apply to the entire repository. This project is a Python
software testing and debugging assignment. Read `README.md` for the requirements
and the relevant program docstrings for expected behavior.

## Code review guidelines

- Prioritize reproducible defects, regressions, missing required tests, and
  inconsistencies between the implementation, tests, and bug report.
- Review the changed code and its callers before reporting a finding. Explain
  the concrete input or state that triggers the issue and the resulting impact.
- Reference the smallest useful file and line range for each finding. Distinguish
  confirmed defects from questions or assumptions about unspecified behavior.
- Use priorities consistently: P0 for an immediate blocker, P1 for a serious
  defect, P2 for an ordinary correctness issue, and P3 for a minor actionable issue.
- Avoid speculative edge cases outside the documented contract and cosmetic
  findings unless they materially affect readability or assignment requirements.
- If there are no actionable findings, say so. State which checks were run and
  any limits on verification; never claim a test or UI run that did not occur.
- A review request alone does not authorize editing code, committing, or pushing.

## Review checklist

- `problem1.py`: at least six meaningful doctests, including fare boundaries,
  rush-hour surcharge, passenger discounts, combined rules, and exceptions.
- `problem2.py` / `test_problem2.py`: check balances, fees, overdraft boundaries,
  status transitions, transaction history, transfers, and frozen accounts.
  Rejected operations should preserve account state.
- `problem3.py` / `test_problem3.py`: check item quantities, membership and coupon
  discounts, taxable versus grocery items, shipping thresholds, totals, and
  order lifecycle restrictions. Assert multiple attributes together.
- `problem4.py` / `test_problem4.py`: check overlap rejection, allowed adjacent
  meetings, sorted bookings, cancellation, capacity, maintenance, free slots,
  and utilization. Keep conflict validation in separate, readable steps, as
  requested by the user.
- `problem5.py`: verify each aggregation, input validation, filtering, and None
  cleaning. Preserve the supplied `test_problem5.py`; add regression tests in
  a separate file rather than weakening existing expectations.
- `bug_report.md`: each defect should include a reproducing test, actual failure
  output, root cause, and a fix matching the current implementation. Distinguish
  terminal evidence from actual VSCode Testing-panel screenshots.
- `.vscode/settings.json`: unittest discovery must include the project tests
  and the doctest bridge in `test_problem1.py`.

## Validation

Run these commands from the repository root using an available Python interpreter:

```sh
python -m unittest discover -v -s . -p "test_problem*.py"
python -m doctest -v problem1.py
```

The project uses the Python standard library. Do not add dependencies merely to
run the tests. A passing suite is evidence, not a substitute for reviewing logic.

## Changes and repository hygiene

- Keep fixes focused on the documented behavior and add useful regression tests
  for defects when changing executable code.
- Preserve unrelated user edits and staged changes. Stage only files relevant
  to the requested work.
- Do not commit caches, credentials, or generated temporary scripts.
- Keep code, report examples, and validation evidence consistent. Do not fabricate
  screenshots or change assertions solely to make a broken implementation pass.
- Commit or push only when requested or already authorized for the current task.
