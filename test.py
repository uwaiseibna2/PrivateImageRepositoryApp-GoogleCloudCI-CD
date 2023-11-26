import unittest
from unittest.mock import patch
from flask import Flask

# Create a dummy Flask app for testing purposes
app = Flask(__name__)

@app.route('/')
def home():
    return 'Home Route'

@app.route('/login')
def login():
    return 'Login Route'

@app.route('/logout')
def logout():
    return 'Logout Route'

@app.route('/register')
def register():
    return 'Register Route'

@app.route('/upload')
def upload():
    return 'Upload Route'

@app.route('/image/<filename>')
def image(filename):
    return f'Image Route: {filename}'

@app.route('/download/<filename>')
def download(filename):
    return f'Download Route: {filename}'

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Home Route')

    def test_login_route(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Login Route')

    def test_logout_route(self):
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Logout Route')

    def test_register_route(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Register Route')

    def test_upload_route(self):
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Upload Route')

    def test_image_route(self):
        response = self.app.get('/image/test_image')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Image Route: test_image')

    def test_download_route(self):
        response = self.app.get('/download/test_image')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Download Route: test_image')

if __name__ == '__main__':
    unittest.main()
