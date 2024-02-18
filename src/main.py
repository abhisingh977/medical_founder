from flask import Flask, url_for, render_template, request, redirect, make_response, session, jsonify
from google.cloud import firestore
from uuid import uuid1
from PIL import Image
from io import BytesIO

# from dotenv import load_dotenv
import logging
import os
from google.cloud import storage
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)
# load_dotenv(".env")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/healthstaffconnect-e913cb44aef7.json" #os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
db = firestore.Client(project="healthstaffconnect")
app = Flask("healthstaffconnect")
bucket_name = "doctor_pic"

session_uuid = str(uuid1())

storage_client = storage.Client()
# Specify the allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Set the path where uploaded files will be saved

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

doctor_collection = db.collection("doctors")

@app.route("/")
def index():
   return render_template("home.html")


@app.route("/contact")
def contact():
   return render_template("home.html")

@app.route("/get_doctors")
def get_doctors():
    doctors = []
    docs = db.collection('doctors').stream()

    for doc in docs:
        doctor_data = doc.to_dict()
        doctors.append(doctor_data)
    return jsonify(doctors)


@app.route('/add_docter')
def add_docter():
    return render_template('add_doc.html')


@app.route('/process_profile', methods=['POST'])
def process_profile():
    name = request.form.get('name')
    location = request.form.get('location')
    specialty = request.form.get('specialty')
    experience = request.form.get('experience')
    number = request.form.get('number')
    countryCode = request.form.get('countryCode')

    if 'profile_pic' not in request.files:
        return "No file selected"

    file = request.files['profile_pic']

    if file.filename == '':
        return "No file selected"

    # Resize and compress the image
    max_size_kb = 100
    image = Image.open(file)
    output = BytesIO()

    # Resize while maintaining the aspect ratio
    base_width = 300  # Adjust this value as needed
    w_percent = base_width / float(image.width)
    h_size = int(float(image.height) * float(w_percent))
    image = image.resize((base_width, h_size))

    # Compress and save the image to BytesIO buffer
    image.save(output, format='JPEG', quality=85)  # Adjust quality as needed
    formatted_number = number.replace(" ", "")
    # Upload the compressed image to Google Cloud Storage
    uuid_blob_name = None
    if file:
        blob_name = secure_filename(file.filename)
        uuid_blob_name = f"{session_uuid}_{blob_name}"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(uuid_blob_name)
        blob.upload_from_string(output.getvalue(), content_type='image/jpeg')

    # Save data to Firestore with the GCS file path
    doc_ref = db.collection('doctors').add({
        'name': str(name),
        'location': str(location),
        'specialty': str(specialty),
        'experience': f"{experience} years",
        'profile_pic': f"gs://{bucket_name}/{uuid_blob_name}",
        'whatsapp_number': str(countryCode+formatted_number)
    })


    return f"Profile added"


if __name__ == '__main__':
    app.run(debug=False, port=8080)