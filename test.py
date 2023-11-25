import unittest
from flask import Flask
from flask_login import LoginManager
from google.cloud import storage  # If needed for your tests
from app import User  # Import any necessary models or classes
import random

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret_key'  # Set a test secret key
        self.app.config['TESTING'] = True

        # Create a test client
        self.test_client = self.app.test_client()

        # Initialize other components as needed (e.g., login manager)
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)

        # Initialize other necessary variables or connections internally
        self.connection = None  # Initialize your database connection here
        self.storage_client = storage.Client()  # Initialize storage client if needed
        self.bucket_name = 'your_test_bucket_name'  # Set test bucket name

    def tearDown(self):
        pass  # Add teardown if needed in the future

    def test_register_and_login(self):
        x = str(random.randint(30, 45))

        # Register a new user
        with self.app.test_request_context():
            response = self.test_client.post('/register', data=dict(
                username='testuser' + x,
                password='testpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Log in with the registered user
            response = self.test_client.post('/login', data=dict(
                username='testuser' + x,
                password='testpassword'
            ), follow_redirects=True)
            self.assertIn(b'Image Gallery', response.data)
            # Note: For current_user, you may need to manage the session manually for testing purposes

if __name__ == '__main__':
    unittest.main()
