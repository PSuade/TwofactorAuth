from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
from twilio.rest import Client
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Dictionary to store user details
users = {}

# Function to generate a random 6-digit code
def generate_code():
    return ''.join(random.choices(string.digits, k=6))

# Twilio API credentials
account_sid = 'AC2beeb234402297a5643d3a7cde24d49d'
auth_token = 'cbea3b94c019d28731f07905364a88cf'
twilio_phone_number = '+16789935357'
service_id = 'VAb535eaa00633e4f7d9a8ec2717fbcd6f'

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Function to send SMS using Twilio Verify Service
def send_sms(recipient):
    verification = client.verify.services(service_id).verifications.create(to=recipient, channel='sms')
    print(f'SMS verification sent to {recipient}: {verification.sid}')

def fetch_code_from_twilio(phone_number):
    verification = client.verify.services(service_id).verifications.fetch(to=phone_number)
    return verification.code if verification else None





# Function to validate username and password
def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return True
    return False

# Function to verify code
def verify_code(code):
    current_time = datetime.now()
    for user in users.values():
        if 'code' in user and user['code'] == code and user['expire_time'] > current_time:
            return True
    return False

# Function to register a new user
def register_user(full_name, major, username, password, phone_number):
    users[username] = {
        'full_name': full_name,
        'major': major,
        'password': password,
        'username': username,
        'phone': phone_number
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        major = request.form['major']
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone']
        register_user(full_name, major, username, password, phone_number)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            if authenticate(username, password):
                session['username'] = username  # Store username in session
                send_sms(users[username]['phone'])
                users[username]['expire_time'] = datetime.now() + timedelta(minutes=10)
                return redirect(url_for('verify_code'))
            else:
                return render_template('login.html', error=True)
        else:
            return render_template('login.html', error=True)
    return render_template('login.html', error=False)

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    print("Request method:", request.method)  # Print the request method
    if request.method == 'POST':
        code = request.form['code']
        if code:
            return render_template('success.html')
        return render_template('verify_code.html', error=True)
    return render_template('verify_code.html', error=False)



if __name__ == '__main__':
    app.run(debug=True)

