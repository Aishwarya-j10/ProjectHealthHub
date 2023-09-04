# from flask import Flask, render_template, redirect, request, session, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a strong, secret key
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/admin/Downloads/Documents/FinalProject/site.db'

# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)

# # Create a User model for your database
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)

# @app.route('/')
# def home():
#     return render_template('index1.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # Hash the password before storing it in the database
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#         # Create a new user and add it to the database
#         user = User(username=username, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()

#         flash('Your account has been created! You can now log in.', 'success')
#         return redirect('/login')
#     return render_template('register.html', action='register')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
# #         username = request.form['username']
# #         password = request.form['password']

# #         # Query the database to find the user by username
# #         user = User.query.filter_by(username=username).first()

# #         if user and bcrypt.check_password_hash(user.password, password):
# #             # Set the user in the session
# #             session['user_id'] = user.id
# #             flash('Login successful!', 'success')
# #             return redirect('/dashboard')
# #         else:
# #             flash('Login unsuccessful. Please check your credentials.', 'danger')
# #     return render_template('login.html', action='login')

# # @app.route('/dashboard')
# # def dashboard():
# #     if 'user_id' in session:
# #         user_id = session['user_id']
# #         user = User.query.get(user_id)
# #         return render_template('dashboard.html', user=user)
# #     else:
# #         return redirect('/login')

# # @app.route('/logout')
# # def logout():
# #     session.pop('user_id', None)
# #     return redirect('/')

# # if __name__ == '__main__':
# #     with app.app_context():
# #         db.create_all()
# #     app.run(debug=True)

# from flask import Flask, render_template, redirect, url_for, flash, session, request
# import csv 

# app = Flask(__name__)
# CSV_FILE = 'health_data.csv'

# @app.route('/') 
# def home() : 
#     return render_template('index1.html') 

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         full_name = request.form['name']
#         password = request.form['password']
#         email = request.form['email']
#         return redirect('/login')
#     return render_template('login.html', action='register')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password'] 
#         if username == 'your_username' and password == 'your_password':
#             session['username'] = username  # Store the username in the session
#             return redirect('/dashboard')  # Redirect after successful login
#         else:
#             return render_template('login.html', action='login', error='Invalid credentials')
#     return render_template('login.html', action='login') 

# @app.route('/dashboard')
# def dashboard():
#     # Check if the user is authenticated in the session
#     if 'username' in session:
#         username = session['username']
#         return render_template('dashboard.html', username=username)
#     else:
#         return redirect('/login')  # Redirect to login if not authenticated
    
# @app.route('/dashboard/health', methods=['GET', 'POST'])
# def health_dashboard():
#     if 'username' not in session:
#         return redirect('/login')

#     if request.method == 'POST':
#         username = session['username']
#         date = request.form['date']
#         weight = request.form['weight']
#         # Add more fields as needed

#         # Append the data to the CSV file
#         with open(CSV_FILE, mode='a', newline='') as csv_file:
#             csv_writer = csv.writer(csv_file)
#             csv_writer.writerow([username, date, weight])

#             # Read and display the user's health data from the CSV file
#     username = session['username']
#     health_data = []
#     with open(CSV_FILE, mode='r') as csv_file:
#         csv_reader = csv.reader(csv_file)
#         for row in csv_reader:
#             if row[0] == username:
#                 health_data.append(row)

#     return render_template('health_dashboard.html', health_data=health_data)

# @app.route('/logout')
# def logout():
#     return redirect('/') 

  
# if __name__ == '__main__' : 
#     app.run(debug = True) 

from flask import Flask, render_template, redirect, flash, session, request
import csv 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CSV_FILE = 'health_data.csv'
app.secret_key = 'your_secret_key_here'
# Dummy user data (replace with database)
users = [{'username': 'your_username', 'password_hash': 'your_password'}]

@app.route('/') 
def home() : 
    return render_template('index1.html') 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        # Check if the username is already taken
        if any(user['username'] == username for user in users):
            flash('Username is already taken. Please choose another.', 'error')
        else:
            # Store the registration data (in-memory for this example)
            users.append({'username': username, 'password_hash': password})
            flash('Registration successful. You can now log in.', 'success')
            return redirect('/login')

    return render_template('login.html', action='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = next((user for user in users if user['username'] == username), None)

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html', action='login') 

@app.route('/dashboard')
def dashboard():
    # if 'username' in session:
    #     username = session['username']

    #     # Read and display the user's health data from the CSV file
        health_data = []
        with open(CSV_FILE, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
    #         for row in csv_reader:
    #             if row[0] == username:
    #                 health_data.append(row)

       # return render_template('dashboard.html', username=username, health_data=health_data)

        return render_template('dashboard.html')
    # else:
    #     return redirect('/dashboard')

@app.route('/dashboard/health', methods=['POST'])
def health_dashboard():
    if 'username' in session:
        username = session['username']
        date = request.form['date']
        weight = request.form['weight']
        # Add more fields as needed

        # Append the data to the CSV file
        with open(CSV_FILE, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([username, date, weight])
            
        flash('Health data added successfully!', 'success')
    else:
        flash('You must be logged in to add health data.', 'error')
    
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/') 

if __name__ == '__main__' : 
    app.secret_key = 'your_secret_key'  # Change this to a secret key
    app.run(debug=True)
