import unittest
from src.utils import add, multiply, format_response

class TestUtils(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-2, 3), -6)

    def test_format_response(self):
        data = {"message": "test"}
        result = format_response(data)
        self.assertIn("status", result)
        self.assertIn("data", result)
        self.assertIn("timestamp", result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], data)

if __name__ == '__main__':
    unittest.main()
