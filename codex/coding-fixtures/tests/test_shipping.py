import unittest
from src.shipping import shipping_price

class ShippingTest(unittest.TestCase):
    def test_prices_and_boundary(self):
        self.assertEqual(shipping_price(0), 8)
        self.assertEqual(shipping_price(5), 8)
        self.assertEqual(shipping_price(5.01), 12)
        self.assertEqual(shipping_price(10), 20)
        self.assertEqual(shipping_price(10.01), 20)
    def test_negative(self):
        with self.assertRaises(ValueError):
            shipping_price(-1)
