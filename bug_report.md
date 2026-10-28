# 缺陷报告

# 测试验证记录
- [修复前：32 项测试，3 项失败、1 项错误](assets/test_before.txt)
- [修复后历史记录：35 项测试全部通过](assets/test_after.txt)
- [车费 doctest 历史记录：12 个示例全部通过](assets/doctest_results.txt)



## 缺陷报告 1：订单接受小数数量

### 1. 被测程序

- 文件： `problem3.py`
- 类／函数： `Order.add_item() / remove_item()`

### 2. 失败测试用例

测试用例来自 `test_problem3.py`:

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

修复前实际输出（完整错误堆栈见 `assets/test_before.txt`）：

```text
AssertionError: ValueError not raised
```

### 3. 根本原因分析

- 预期行为：商品数量必须为正整数；操作被拒绝后，订单的所有属性应保持不变。
- 实际行为： 新增商品时传入数量 0.5，会创建数量为 0 的商品；增加已有商品数量或移除 0.5 件商品时，会产生小数数量。
- 根本原因： 原代码只检查 quantity <= 0，没有验证整数类型；int(quantity) 会截断新增商品数量的小数部分。

### 4. 代码修复与差异

```diff
-        if quantity <= 0:
+        if isinstance(quantity, bool):
+            raise ValueError("Quantity must be a positive integer")
+        if not isinstance(quantity, int):
+            raise ValueError("Quantity must be a positive integer")
+        if quantity <= 0:
             raise ValueError("Quantity must be a positive integer")
+
+        # 在 remove_item 中，先验证数量，再删除商品或减少数量。
+        if quantity is not None:
+            if isinstance(quantity, bool):
+                raise ValueError("Quantity to remove must be a positive integer")
+            if not isinstance(quantity, int):
+                raise ValueError("Quantity to remove must be a positive integer")
+            if quantity <= 0:
+                raise ValueError("Quantity to remove must be a positive integer")
```

## 缺陷报告 2：相邻会议被误判为冲突

### 1. 被测程序

- 文件： `problem4.py`
- 类／函数： `MeetingRoom.book()`

### 2. 失败测试用例

测试用例来自 `test_problem4.py`:

```python
    def test_back_to_back_meetings_allowed(self):
        self.room.book('B01', 'First', 9, 10, 10)
        self.assertTrue(self.room.book('B02', 'Next', 10, 12, 5))
        self.assertTrue(self.room.book('B00', 'Earlier', 8, 9, 1))
        self.assert_schedule(['B00', 'B01', 'B02'], 4, [(12, 18)])
```

修复前实际输出（完整错误堆栈见 `assets/test_before.txt`）：

```text
ValueError: Time slot [10, 12] conflicts with booking 'B01' [9, 10]
```

### 3. 根本原因分析

- 预期行为： 应允许 9—10 点与 10—12 点，以及 8—9 点与 9—10 点这样的相邻会议；预约应保持排序，并正确更新累计时长和空闲时段。
- 实际行为： 第二场会议恰好在第一场会议结束时开始，仍然抛出 ValueError。
- 根本原因：严格的小于和大于比较，将共享时间端点的相邻会议误判为重叠。

### 4. 代码修复与差异

```diff
-            if not (end_time < b["start_time"] or start_time > b["end_time"]):
+            if end_time <= b["start_time"]:
+                continue
+            if start_time >= b["end_time"]:
+                continue
+            # 两种不重叠情况均不成立，因此拒绝该预约。
+            raise ValueError(...)
```

## 缺陷报告 3：最小值与最大值操作颠倒

### 1. 被测程序

- 文件： `problem5.py`
- 类／函数： `clean_and_aggregate()`

### 2. 失败测试用例

测试用例来自 `test_problem5.py`:

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

修复前实际输出（完整错误堆栈见 `assets/test_before.txt`）：

```text
AssertionError: 200.0 != 100.0 within 7 places (100.0 difference)
```

### 3. 根本原因分析

预期行为North 分组的数值为 [100, 200]，最小值应为 100，最大值应为 200。
实际行为： min 返回 200，max 返回 100。
根本原因： min 分支错误地调用了 max(values)，max 分支错误地调用了 min(values)。

### 4. 代码修复与差异

```diff
         elif agg_op == "min":
-            val = max(values)
+            val = min(values)
         elif agg_op == "max":
-            val = min(values)
+            val = max(values)
```

## 缺陷报告 4：缺少空输入和容器类型验证

### 1. 被测程序

- 文件： `problem5.py`
- 类／函数： `clean_and_aggregate()`

### 2. 失败测试用例

测试用例来自 `test_problem5.py`:

```python
    def test_empty_dataset_raises_value_error(self):
        """Test that passing an empty list raises ValueError."""
        with self.assertRaises(ValueError):
            clean_and_aggregate([], group_by="region", metric="sales")
```

修复前实际输出（完整错误堆栈见 `assets/test_before.txt`）：

```text
AssertionError: ValueError not raised
```

### 3. 根本原因分析

预期行为：按照文档约定，空列表应抛出 ValueError，非列表输入应抛出 TypeError。
实际行为： 空列表返回 {}；包含有效记录的元组被接受；None 输入只会在遍历时意外报错。
根本原因： 分组处理前缺少输入验证。原有字符串测试只是因为字符串中的字符不是字典而碰巧通过，并未真正验证输入容器必须为列表。

### 4. 代码修复与差异

```diff
+    if not isinstance(records, list):
+        raise TypeError("records must be a list")
+    if not records:
+        raise ValueError("records cannot be empty")
```
## 其他程序

原有完整测试套件未发现 `problem1.py` 或 `problem2.py` 业务逻辑中的缺陷。
历史车费测试覆盖起步价边界、超出里程、高峰时段、折扣、规则组合和两种文档约定的异常。
银行账户测试检查余额、状态、交易记录、摘要、手续费、透支边界与恢复、转账、冻结限制，
以及操作被拒绝后状态是否保持不变。
