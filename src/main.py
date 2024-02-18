from flask import Flask, url_for, render_template, request, redirect, make_response, session
# from google.cloud import firestore
from uuid import uuid1
# db = firestore.Client(project="healthstaffconnect")
app = Flask("healthstaffconnect")

session_uuid = str(uuid1())

# doctor_collection = db.collection("doctors")

@app.route("/")
def index():
   return render_template("home.html")

@app.route("/contact")
def contact():
   return render_template("home.html")


@app.route('/add_docter')
def add_docter():
    return render_template('add_doc.html')

@app.route('/process_profile', methods=['POST'])
def process_profile():
    return render_template('add_doc.html')



if __name__ == '__main__':
    app.run(debug=True, port=8080)