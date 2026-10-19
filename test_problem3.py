"""Order pricing, multiple attributes and lifecycle tests."""
import copy
import unittest
from problem3 import Order

class TestOrder(unittest.TestCase):
    def setUp(self):
        self.regular_order = Order('ORD100')
        self.silver_order = Order('ORD200', 'silver')
        self.gold_order = Order('ORD300', 'gold')

    def assert_totals(self, order, subtotal, discount, tax, shipping, total, count):
        summary = order.get_summary()
        for field, value in zip(
                ('subtotal', 'discount_amount', 'tax_amount', 'shipping_fee', 'final_total'),
                (subtotal, discount, tax, shipping, total)):
            self.assertAlmostEqual(getattr(order, field), value)
            self.assertAlmostEqual(summary[field], value)
        self.assertEqual(summary['item_count'], count)
        self.assertEqual(summary['status'], order.status)
        self.assertEqual(summary['order_id'], order.order_id)
        self.assertEqual(summary['tier'], order.customer_tier)

    def test_initial_state_and_tiers(self):
        for order in (self.regular_order, self.silver_order, self.gold_order):
            self.assert_totals(order, 0, 0, 0, 0, 0, 0)
            self.assertEqual(order.items, {})
            self.assertIsNone(order.applied_coupon)
            self.assertEqual(order.status, 'PENDING')
        self.assertEqual(Order('mixed', 'GoLd').customer_tier, 'gold')
        with self.assertRaises(ValueError):
            Order('bad', 'platinum')

    def test_add_merge_remove_and_empty(self):
        order = self.regular_order
        order.add_item('Book', 10, 2)
        order.add_item('Book', 10)
        self.assertEqual(order.items['Book']['quantity'], 3)
        self.assert_totals(order, 30, 0, 2.4, 5.99, 38.39, 3)
        order.remove_item('Book', 1)
        self.assert_totals(order, 20, 0, 1.6, 5.99, 27.59, 2)
        order.remove_item('Book', 2)
        self.assert_totals(order, 0, 0, 0, 0, 0, 0)
        order.add_item('Food', 5, category='GROCERY')
        self.assertEqual(order.items['Food']['category'], 'grocery')
        order.remove_item('Food')
        self.assertEqual(order.items, {})

    def test_tier_discounts_and_mixed_tax(self):
        for order, discount, tax, total in (
                (self.regular_order, 0, 4.8, 104.8),
                (self.silver_order, 5, 4.56, 99.56),
                (self.gold_order, 10, 4.32, 94.32)):
            order.add_item('Food', 40, category='grocery')
            order.add_item('Device', 60)
            self.assert_totals(order, 100, discount, tax, 0, total, 2)

    def test_coupons_stack_replace_and_cap(self):
        order = self.gold_order
        order.add_item('Device', 100)
        order.apply_coupon(' save10 ')
        self.assertEqual(order.applied_coupon, 'SAVE10')
        self.assert_totals(order, 100, 19, 6.48, 0, 87.48, 1)
        order.apply_coupon('FLAT15')
        self.assert_totals(order, 100, 25, 6, 0, 81, 1)
        order.remove_item('Device')
        order.add_item('Small', 10)
        self.assert_totals(order, 10, 10, 0, 5.99, 5.99, 1)

    def test_shipping_threshold_uses_discounted_subtotal(self):
        order = self.regular_order
        order.add_item('Food', 50, category='grocery')
        self.assert_totals(order, 50, 0, 0, 0, 50, 1)
        order.apply_coupon('SAVE10')
        self.assert_totals(order, 50, 5, 0, 5.99, 50.99, 1)
        below = Order('below')
        below.add_item('Food', 49.99, category='grocery')
        self.assert_totals(below, 49.99, 0, 0, 5.99, 55.98, 1)

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

    def test_checkout_and_cancel_lifecycle(self):
        with self.assertRaises(ValueError):
            self.regular_order.checkout()
        self.regular_order.add_item('Book', 10)
        self.assertTrue(self.regular_order.checkout())
        self.assertEqual(self.regular_order.status, 'PAID')
        self.assert_totals(self.regular_order, 10, 0, 0.8, 5.99, 16.79, 1)
        self.assertTrue(self.silver_order.cancel())
        self.assertEqual(self.silver_order.status, 'CANCELLED')
        for order in (self.regular_order, self.silver_order):
            before = copy.deepcopy(order.__dict__)
            for operation in (lambda: order.add_item('X', 1),
                              lambda: order.remove_item('Book'),
                              lambda: order.apply_coupon('SAVE10'), order.checkout):
                with self.assertRaises(RuntimeError):
                    operation()
                self.assertEqual(order.__dict__, before)
        with self.assertRaises(RuntimeError):
            self.regular_order.cancel()

if __name__ == '__main__':
    unittest.main()
