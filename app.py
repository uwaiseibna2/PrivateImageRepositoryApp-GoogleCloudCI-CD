import os
from flask import Flask, render_template, request, redirect, url_for,flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pymysql
from google.cloud import storage
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
from google.cloud import secretmanager
app = Flask(__name__)


def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/group-21-project-2/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_path})
    return response.payload.data.decode("UTF-8")
bucket_name=get_secret('BUCKET_NAME')
app.secret_key=get_secret('APP_SECRET_KEY')
connection = pymysql.connect(
    unix_socket='/cloudsql/group-21-project-2:us-central1:users',
    user=get_secret('DB_USER'),
    password=get_secret('DB_PASSWORD'),
    database=get_secret('DB_NAME'),
    cursorclass=pymysql.cursors.DictCursor
)

login_manager = LoginManager()
login_manager.init_app(app)
def generate_unique_filename(filename):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{current_time}_{filename}"
class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM User WHERE id=%s", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        return User(user_data['id'], user_data['username'], user_data['password'])
    else:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            user_id = user['id']
            login_user(User(user['id'], user['username'], user['password']))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')
#comment
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('This username already exists', 'error')
        else:
            cursor.execute("INSERT INTO User (username, password) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            flash('Account created successfully', 'success')
            cursor.execute("SELECT * FROM User WHERE username=%s", (username,))
            new_user = cursor.fetchone()
            if new_user:
                user_id = new_user['id']
                login_user(User(new_user['id'], new_user['username'], new_user['password']))
                return redirect(url_for('home'))

    return render_template('register.html', register=True)

@app.route('/logout', methods=['POST'] )
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
        # Initialize the Google Cloud Storage client
    storage_client = storage.Client()

    # Get a list of all objects (images) in the GCS bucket
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    # Filter images to display only those associated with the current user
    user_images = []
    for blob in blobs:
        if blob.exists():
            image_metadata = blob.metadata
            associated_user = image_metadata.get('associated_user') if image_metadata else None
        else:
            # Handle the case when the blob doesn't exist
            image_metadata = {'Status': 'Image not found in GCS bucket'}
            associated_user = None 

        if associated_user == current_user.username:
            user_images.append(blob.name)

    return render_template('home.html', image_files=user_images, username=current_user.username)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = generate_unique_filename(secure_filename(file.filename))
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_file(file)
            exif_data = {}
            try:
                with Image.open(file) as img:
                    if hasattr(img, '_getexif'):
                        exif_info = img._getexif()
                        if exif_info is not None:
                            # Specify the EXIF tags you want to extract
                            desired_tags = {
                                'Make': TAGS.get('Make', 'Make'),
                                'Model': TAGS.get('Model', 'Model'),
                                'ISO': TAGS.get('ISOSpeedRatings', 'ISO'),
                                # Add more tags as needed
                            }
                            for tag, value in exif_info.items():
                                tag_name = TAGS.get(tag, tag)
                                if tag_name in desired_tags:
                                    exif_data[desired_tags[tag_name]] = value
            except Exception as e:
                print(f"Error extracting EXIF data: {str(e)}")
            
            metadata = {
                'size': str(blob.size)+" Bytes" ,  # Convert the size to a string
                'directory': bucket_name+"/"+filename,
                'name': filename,
                'associated_user': current_user.username,
                **exif_data
            }

            blob.metadata = metadata

            # Update the object's metadata in the bucket
            blob.patch()

            return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/image/<filename>', methods=['GET', 'POST'])
def image(filename):
    storage_client = storage.Client()
    gcs_url = f'https://storage.googleapis.com/{bucket_name}/{filename}'
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(filename)

    if blob.exists():
        image_metadata = blob.metadata
    else:
        image_metadata = {'Status': 'Image not found in GCS bucket'}

    if request.method == 'POST':
        # Delete image if the delete button is pressed
        if 'delete_image' in request.form:

            blob.delete()  # Delete the image blob
            return redirect(url_for('home'))

    return render_template('image.html', filename=filename, gcs_url=gcs_url, image_metadata=image_metadata)


@app.route('/download/<filename>')
def download(filename):
    # Construct the GCS URL for the file to be downloaded
    gcs_url = f'https://storage.googleapis.com/{bucket_name}/{filename}'

    # Redirect the user to the GCS URL for download
    return redirect(gcs_url)
@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))

# Create a cursor object
cursor = connection.cursor()

# Define the table creation SQL query
create_table_query = '''
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);
'''

# Execute the query to create the table
cursor.execute(create_table_query)

# Commit changes and close the cursor and connection
connection.commit()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
