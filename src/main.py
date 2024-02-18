from flask import Flask, url_for, render_template, request, redirect, make_response, session, jsonify
from google.cloud import firestore
from uuid import uuid1
from dotenv import load_dotenv
import logging
import os
from google.cloud import storage
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
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
        print(doctor_data)
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

    if 'profile_pic' not in request.files:
        return "No file selected"

    file = request.files['profile_pic']

    if file.filename == '':
        return "No file selected"

    uuid_blob_name = None
    if file:
        # Upload the image to Google Cloud Storage
        blob_name = secure_filename(file.filename)
        uuid_blob_name = f"{session_uuid}_{blob_name}"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(uuid_blob_name)
        blob.upload_from_string(file.read(), content_type=file.content_type)

    # Save data to Firestore with the GCS file path
    doc_ref = db.collection('doctors').add({
        'name': str(name),
        'location': str(location),
        'specialty': str(specialty),
        'experience': f"{experience} years",
        'profile_pic': f"gs://{bucket_name}/{uuid_blob_name}",
        'whatsapp_number': str(number)
    })


    return f"Profile added"


if __name__ == '__main__':
    app.run(debug=False, port=8080)