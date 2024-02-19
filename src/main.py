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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "healthstaffconnect-e913cb44aef7.json" #os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
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


@app.route("/")
def index():
   return render_template("home.html")

@app.route("/get_doctors")
def get_doctors():
    doctors = []
    docs = db.collection('doctors').stream()

    for doc in docs:
        doctor_data = doc.to_dict()
        doctors.append(doctor_data)
    return jsonify(doctors)

@app.route("/get_nurses")
def get_nurses():
    nurse = []
    docs = db.collection('nurse').stream()
    for doc in docs:
        nurse_data = doc.to_dict()
        nurse.append(nurse_data)

    return jsonify(nurse)

@app.route("/get_technicians")
def get_technicians():
    technicians = []
    docs = db.collection('technicians').stream()

    for doc in docs:
        technicians_data = doc.to_dict()
        technicians.append(technicians_data)

    return jsonify(technicians)


@app.route('/add_profile')
def add_docter():
    return render_template('add_profile.html')

@app.route('/previous_page')
def previous_page():
    return render_template('add_profile.html')

@app.route('/doctors_profiles')
def doctors_profiles():
    title = 'Doctors'
    header = 'Doctors'
    add_url = '/add_profile'
    data_url = '/get_doctors'

    return render_template('profile.html', title=title, header=header, add_url=add_url, data_url=data_url)

@app.route('/nurse_profiles')
def nurse_profiles():
    title = 'Nurse Profiles'
    header = 'Nurse Profiles'
    add_url = '/add_profile'
    data_url = '/get_nurses'

    return render_template('profile.html', title=title, header=header, add_url=add_url, data_url=data_url)

@app.route('/technicians_profiles')
def technicians_profiles():
    title = 'Technicians Profiles'
    header = 'Technicians Profiles'
    add_url = '/add_profile'
    data_url = '/get_technicians'

    return render_template('profile.html', title=title, header=header, add_url=add_url, data_url=data_url)


@app.route('/process_profile', methods=['POST'])
def process_profile():
    name = request.form.get('name')
    location = request.form.get('location')
    occupation = request.form.get('occupation')
    specialty = request.form.get('specialty')
    experience = request.form.get('experience')
    number = request.form.get('number')
    countryCode = request.form.get('countryCode')

    if 'profile_pic' not in request.files or request.files['profile_pic'].filename == '':
        # If no profile pic is added, use default image
        default_image_path = os.path.join(app.root_path, 'static', 'images', 'blank-profile.png')
        image = Image.open(default_image_path)
        output = BytesIO()

        # Set a fixed size for the output image
        output_size = (300, 300)  # Adjust this value as needed

        # Resize the default image to the fixed size
        image = image.resize(output_size)

        # Save the default image to BytesIO buffer
        image.save(output, format='PNG')

        # Upload the default image to Google Cloud Storage
        uuid_blob_name = f"{session_uuid}_default_profile.png"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(uuid_blob_name)
        blob.upload_from_string(output.getvalue(), content_type='image/png')
    else:
        file = request.files['profile_pic']
        max_size_kb = 100
        image = Image.open(file)
        output = BytesIO()

        # Set a fixed size for the output image
        output_size = (300, 300)  # Adjust this value as needed

        # Resize the image to the fixed size
        image = image.resize(output_size)

        # Compress and save the image to BytesIO buffer
        image.save(output, format='JPEG', quality=85)
        
        # Upload the compressed image to Google Cloud Storage
        uuid_blob_name = None
        if file:
            blob_name = secure_filename(file.filename)
            uuid_blob_name = f"{session_uuid}_{blob_name}"
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(uuid_blob_name)
            blob.upload_from_string(output.getvalue(), content_type='image/jpeg')

    formatted_number = number.replace(" ", "")
    if occupation=="Doctor":
    # Save data to Firestore with the GCS file path
        profile_ref = db.collection('doctors').add({
            'name': str(name),
            'location': str(location),
            'occupation': str(occupation),
            'specialty': str(specialty),
            'experience': f"{experience} years",
            'profile_pic': f"gs://{bucket_name}/{uuid_blob_name}",
            'whatsapp_number': str(countryCode+formatted_number)
        })
    elif occupation=="Nurse":
        profile_ref = db.collection('nurse').add({
            'name': str(name),
            'location': str(location),
            'occupation': str(occupation),
            'specialty': str(specialty),
            'experience': f"{experience} years",
            'profile_pic': f"gs://{bucket_name}/{uuid_blob_name}",
            'whatsapp_number': str(countryCode+formatted_number)
        })
    elif occupation=="Technicians":
        profile_ref = db.collection('technicians').add({
            'name': str(name),
            'location': str(location),
            'occupation': str(occupation),
            'specialty': str(specialty),
            'experience': f"{experience} years",
            'profile_pic': f"gs://{bucket_name}/{uuid_blob_name}",
            'whatsapp_number': str(countryCode+formatted_number)
        })

    return redirect(url_for('previous_page'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)