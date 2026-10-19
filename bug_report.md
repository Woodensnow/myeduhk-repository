# Bug Report

## Validation evidence

Tests were executed locally using Python unittest and doctest. The unmodified reference
suite `test_problem5.py` is preserved. The original fare doctests were preserved and extended.

- [Before fixes: 32 tests, 3 failures and 1 error](assets/test_before.txt)
- [After fixes: 35 tests, all pass](assets/test_after.txt)
- [Fare doctests: 12 examples, all pass](assets/doctest_results.txt)

The 35 discovered tests include one doctest suite containing all 12 fare examples.
Additional aggregator regression tests cover non-list containers, invalid records,
missing keys, boolean metrics, filtering, None cleaning and case normalization.

### VSCode evidence limitation

`.vscode/settings.json` now enables unittest discovery from the project root with
`test_problem*.py`, including fare doctests through `test_problem1.py`. The same
discovery was verified from the terminal. No VSCode Testing-panel run or screenshot
was captured in this environment. `assets/example_test_runs.png` is the supplied
example, not evidence of this work. To complete that submission item, select a working
Python interpreter in VSCode, open Testing, run all tests and capture the actual panel.


## Bug Report 1: Order accepts fractional quantities

### 1. Program under test

- File: `problem3.py`
- Class / function: `Order.add_item() / remove_item()`

### 2. Failing test case

From `test_problem3.py`:

```python
    def test_invalid_changes_preserve_state(self):
        order = self.regular_order
        order.add_item('Book', 10, 2)
        before = copy.deepcopy(order.__dict__)
        for operation in (lambda: order.add_item('bad', 0),
                          lambda: order.add_item('bad', -1),
                          lambda: order.add_item('bad', 1, 0),
                          lambda: order.add_item('bad', 1, -1),
                          lambda: order.add_item('bad', 1, 0.5),
                          lambda: order.add_item('Book', 10, 1.5),
                          lambda: order.remove_item('Book', 0),
                          lambda: order.remove_item('Book', -1),
                          lambda: order.remove_item('Book', 0.5),
                          lambda: order.apply_coupon('INVALID')):
            with self.assertRaises(ValueError):
                operation()
            self.assertEqual(order.__dict__, before)
        with self.assertRaises(KeyError):
            order.remove_item('missing')
        self.assertEqual(order.__dict__, before)
```

Actual pre-fix output (full traceback in `assets/test_before.txt`):

```text
AssertionError: ValueError not raised
```

### 3. Root cause analysis

- **Expected behavior:** Quantities must be positive integers; rejected operations must preserve all order attributes.
- **Actual behavior:** Adding quantity 0.5 creates an item with quantity 0; adding to an existing item or removing 0.5 permits fractional quantities.
- **Root cause:** The code only checked quantity <= 0, and int(quantity) silently truncated new quantities.

### 4. Code fix & diff

```diff
-        if quantity <= 0:
+        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
             raise ValueError("Quantity must be a positive integer")
+
+        # In remove_item, validate before deleting or decreasing quantity.
+        if quantity is not None and (
+            isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0
+        ):
+            raise ValueError("Quantity to remove must be a positive integer")
```

### 5. Regression result

The failing test now passes in `assets/test_after.txt`.


## Bug Report 2: Adjacent meetings incorrectly conflict

### 1. Program under test

- File: `problem4.py`
- Class / function: `MeetingRoom.book()`

### 2. Failing test case

From `test_problem4.py`:

```python
    def test_back_to_back_meetings_allowed(self):
        self.room.book('B01', 'First', 9, 10, 10)
        self.assertTrue(self.room.book('B02', 'Next', 10, 12, 5))
        self.assertTrue(self.room.book('B00', 'Earlier', 8, 9, 1))
        self.assert_schedule(['B00', 'B01', 'B02'], 4, [(12, 18)])
```

Actual pre-fix output (full traceback in `assets/test_before.txt`):

```text
ValueError: Time slot [10, 12] conflicts with booking 'B01' [9, 10]
```

### 3. Root cause analysis

- **Expected behavior:** 9-10 and 10-12, as well as 8-9 and 9-10, must be permitted; bookings stay sorted and hours/free slots update.
- **Actual behavior:** The second meeting raises ValueError even though it starts exactly when the first ends.
- **Root cause:** Strict separation comparisons treated shared endpoints as overlap.

### 4. Code fix & diff

```diff
-            if not (end_time < b["start_time"] or start_time > b["end_time"]):
+            if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
```

### 5. Regression result

The failing test now passes in `assets/test_after.txt`.


## Bug Report 3: Minimum and maximum operations are reversed

### 1. Program under test

- File: `problem5.py`
- Class / function: `clean_and_aggregate()`

### 2. Failing test case

From `test_problem5.py`:

```python
    def test_aggregate_min_and_max(self):
        """Test min and max aggregation operations."""
        min_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="min")
        max_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="max")

        self.assertAlmostEqual(min_result["North"], 100.0)
        self.assertAlmostEqual(max_result["North"], 200.0)
        self.assertAlmostEqual(min_result["South"], 150.0)
        self.assertAlmostEqual(max_result["South"], 350.0)
```

Actual pre-fix output (full traceback in `assets/test_before.txt`):

```text
AssertionError: 200.0 != 100.0 within 7 places (100.0 difference)
```

### 3. Root cause analysis

- **Expected behavior:** For North values [100, 200], min must be 100 and max must be 200.
- **Actual behavior:** min returns 200 and max returns 100.
- **Root cause:** The min branch called max(values), and the max branch called min(values).

### 4. Code fix & diff

```diff
         elif agg_op == "min":
-            val = max(values)
+            val = min(values)
         elif agg_op == "max":
-            val = min(values)
+            val = max(values)
```

### 5. Regression result

The failing test now passes in `assets/test_after.txt`.


## Bug Report 4: Empty input and container type validation missing

### 1. Program under test

- File: `problem5.py`
- Class / function: `clean_and_aggregate()`

### 2. Failing test case

From `test_problem5.py`:

```python
    def test_empty_dataset_raises_value_error(self):
        """Test that passing an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            clean_and_aggregate([], group_by="region", metric="sales")
```

Actual pre-fix output (full traceback in `assets/test_before.txt`):

```text
AssertionError: ValueError not raised
```

### 3. Root cause analysis

- **Expected behavior:** Empty lists raise ValueError; non-list input raises TypeError, as documented.
- **Actual behavior:** An empty list returns {}; a tuple of valid records is accepted; None fails incidentally during iteration.
- **Root cause:** There was no input validation before grouping records. The provided string test passed incidentally because string characters are not dictionaries.

### 4. Code fix & diff

```diff
+    if not isinstance(records, list):
+        raise TypeError("records must be a list")
+    if not records:
+        raise ValueError("records cannot be empty")
```

### 5. Regression result

The failing test now passes in `assets/test_after.txt`.


## Other programs

No defects were exposed in `problem1.py` or `problem2.py` by the completed suites.
Fare tests cover base-fare boundaries, additional distance, rush hour, discounts,
combined rules and both documented exceptions. Bank tests check balance, status,
history, summary, fee handling, overdraft boundary/recovery, transfers, frozen
accounts and state preservation after rejected operations.
