import unittest
from fastapi.testclient import TestClient
from main import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app.app)
    

    # Unittesting Backend
    def test_products_endpoint(self):
        response = self.client.get("http://127.0.0.1/api/products")
        self.assertEqual(response.status_code, 200)
    
    def test_stock_endpoint(self):
        response = self.client.get("http://127.0.0.1/api/stock")
        self.assertEqual(response.status_code, 200)
    
    def test_checkout_endpoint(self):
        cart_items = [{"name": "Franziskaner", "price": 10.0, "quantity": 2}]
        response = self.client.post("http://127.0.0.1/api/checkout", json={"cartItems": cart_items})
        self.assertEqual(response.status_code, 200)


    # Unittesting Frontend
    def test_index_page(self):
        response = self.client.get("http://127.0.0.1/")
        self.assertEqual(response.status_code, 200)
    
    def test_index_page(self):
        response = self.client.get("http://127.0.0.1/checkout")
        self.assertEqual(response.status_code, 200)

    def test_index_page(self):
        response = self.client.get("http://127.0.0.1/overview")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
