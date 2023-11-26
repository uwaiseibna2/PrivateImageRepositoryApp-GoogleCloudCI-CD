import unittest
from flask import Flask
from flask_login import LoginManager
import pymysql
import random

class TestFlaskApp(unittest.TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.secret_key = 'test_secret_key'
        app.config['TESTING'] = True
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
        return app

    def test_register_and_login(self):
        app = self.create_app()
        test_client = app.test_client()

        # Set up a test database connection using the same configuration as in app.py
        DB_SOCKET = '/cloudsql/group-21-project-2:us-central1:users'
        DB_USER = 'root'
        DB_PASSWORD = 'secretpass'
        DB_NAME = 'users-db'

        connection = pymysql.connect(
            unix_socket=DB_SOCKET,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )

        x = str(random.randint(30, 45))

        # Register a new user
        with app.test_request_context():
            response = test_client.post('/register', data=dict(
                username='testuser' + x,
                password='testpassword'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # Log in with the registered user
            response = test_client.post('/login', data=dict(
                username='testuser' + x,
                password='testpassword'
            ), follow_redirects=True)
            self.assertIn(b'Image Gallery', response.data)
            # Note: For current_user, you may need to manage the session manually for testing purposes

        # Close the test database connection after the test
        connection.close()

if __name__ == '__main__':
    unittest.main()
