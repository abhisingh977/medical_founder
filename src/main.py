from flask import Flask, url_for, render_template, request, redirect, make_response, session
from google.cloud import firestore
from uuid import uuid1
# db = firestore.Client(project="healthstaffconnect")
app = Flask("healthstaffconnect")

session_uuid = str(uuid1())

# doctor_collection = db.collection("doctors")



@app.route("/")
def home():
   return render_template("home.html")

@app.route("/")
def contact():
   return render_template("home.html")


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        # doctors.append(new_doctor)
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=False, port=8080)