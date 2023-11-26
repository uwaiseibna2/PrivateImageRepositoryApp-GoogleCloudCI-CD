import unittest
from flask import Flask
from app import app, User  # Import the Flask app and User model from app.py
import random

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()  # Use the app from app.py
        app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_register_and_login(self):
        x = str(random.randint(30, 45))

        # Register a new user
        response = self.app.post('/register', data=dict(
            username='testuser' + x,
            password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Log in with the registered user
        response = self.app.post('/login', data=dict(
            username='testuser' + x,
            password='testpassword'
        ), follow_redirects=True)
        self.assertIn(b'Image Gallery', response.data)
        # Ensure that the login redirects to a page containing 'Image Gallery'

if __name__ == '__main__':
    unittest.main()
