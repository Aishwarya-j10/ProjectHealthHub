import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import pandas as pd
from io import StringIO
# from flask_migrate import Migrate

from sqlalchemy.sql import func
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'not_A_secret'
# migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))

    def __repr__(self):
        return f'<User {self.name}>' 
    
# Add a new table for health data
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('health_data', lazy=True))
    age = db.Column(db.Integer)  
    gender = db.Column(db.String) 
    fever = db.Column(db.Boolean)
    heart_rate = db.Column(db.Integer)
    acidity = db.Column(db.Boolean) 
    vomiting = db.Column(db.Boolean) 
    headache = db.Column(db.Boolean) 
    breathlessness = db.Column(db.Boolean)  
    cough = db.Column(db.Boolean) 
    anxiety = db.Column(db.Boolean) 

    def __repr__(self):
        return f'<HealthData for User {self.user_id}>'

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        session['user_id'] = user.id  
        return render_template('dashboard.html', user = user)
    else:
        flash('Invalid email or password. Please try again.', 'danger')
        return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone_number = request.form.get('phone_number')
        
        new_user = User(name=name, email=email, password=password, phone_number=phone_number)
        
        try:
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered. Please use a different email.', 'danger')
    
    return render_template('register.html') 


@app.route('/dashboard')
def dashboard():
    # Fetch the user's information from the session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return render_template('dashboard.html', user=user)
    
    flash('You need to log in to access the dashboard.', 'danger')
    return redirect(url_for('home'))


@app.route('/add_health_data', methods=['POST'])
def add_health_data():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            print(f'User ID: {user_id}')
            # Retrieve health data attributes from the form
            age = int(request.form.get('age')) if request.form.get('age') else None
            gender = str(request.form.get('gender')) 
            fever = bool(request.form.get('fever'))
            heart_rate = int(request.form.get('heart_rate')) if request.form.get('heart_rate') else None
            # heart_rate = request.form.get('heart_rate') or None
            # if heart_rate_str is None:
            #     heart_rate = None
            # else:
            #     heart_rate = int(heart_rate_str)
            acidity = bool(request.form.get('acidity')) 
            vomiting = bool(request.form.get('vomiting')) 
            headache = bool(request.form.get('headache')) 
            breathlessness = bool(request.form.get('breathlessness')) 
            cough = bool(request.form.get('cough')) 
            anxiety = bool(request.form.get('anxiety')) 

            existing_health_data = HealthData.query.filter_by(user=user).first()
            if existing_health_data : 
                existing_health_data.user = user.id
                existing_health_data.age = age
                existing_health_data.gender = gender
                existing_health_data.fever = fever
                existing_health_data.heart_rate = heart_rate
                existing_health_data.acidity = acidity
                existing_health_data.vomiting = vomiting
                existing_health_data.headache = headache
                existing_health_data.breathlessness = breathlessness
                existing_health_data.cough = cough
                existing_health_data.anxiety = anxiety
                db.session.add(existing_health_data)
                db.session.commit()
            else : 
                new_health_data = HealthData(
                    user=user.id,
                    age = age, 
                    gender = gender, 
                    fever=fever,
                    heart_rate=heart_rate, 
                    acidity = acidity, 
                    vomiting = vomiting, 
                    headache = headache, 
                    breathlessness = breathlessness, 
                    cough = cough, 
                    anxiety = anxiety  
                    # Add similar lines for other health data attributes
                )
                db.session.add(new_health_data)
                db.session.commit()

        flash('Health data submitted successfully.', 'success')
        return redirect(url_for('dashboard', user = user))
    else: 
        flash('You need to log in to submit health data.', 'danger')
        return redirect(url_for('home'))
    
# @app.route('/view_data')
# def view_data():
#     user_id = session.get('user_id')
#     if user_id:
#         user = User.query.get(user_id) 
#         # user = User.query.filter_by(user_id = user_id).first()
#         print(user)
#         if user:
#             # Fetch the user's health data
#             health_data = HealthData.query.filter_by(user_id=user_id).all()
#             print(health_data)
#             return render_template('view_data.html', user=user, health_data=health_data)
    
#     flash('You need to log in to view health data.', 'danger')
#     return redirect(url_for('home'))
@app.route('/view_data', methods=['GET'])
def view_data():
    print("out of if") 
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            try:
                # Fetch the user's health data
                health_data = HealthData.query.filter_by(user_id=user_id).all()
                print("User:", user)
                print("Health Data:", health_data)
                return render_template('view_data.html', user=user, health_data=health_data)
            except Exception as e:
                print("Error fetching health data:", str(e))
                flash('An error occurred while fetching health data.', 'danger')
                return redirect(url_for('home'))

    
    flash('You need to log in to view health data.', 'danger')
    return redirect(url_for('home'))


# import os
# from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
# import pandas as pd


# ... (your existing code)

@app.route('/download_health_data_csv')
def download_health_data_csv():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.filter_by(user_id=user_id).all()
            if health_data:
                # Create a list of dictionaries with the selected columns
                data_list = [
                    {
                        "Age": data.age,
                        "Gender": data.gender,
                        "Fever": data.fever,
                        "Heart Rate": data.heart_rate,
                        "Acidity": data.acidity,
                        "Vomiting": data.vomiting,
                        "Headache": data.headache,
                        "Breathlessness": data.breathlessness,
                        "Cough": data.cough,
                        "Anxiety": data.anxiety,
                    }
                    for data in health_data
                ]

                # Create a Pandas DataFrame from the list of dictionaries
                df = pd.DataFrame(data_list)

                # Create a unique file name
                file_name = f"user_{user.id}_health_data.csv"

                # Save the DataFrame to a CSV file in memory
                csv_data = StringIO()
                df.to_csv(csv_data, index=False)

                # Move the file pointer to the beginning of the file
                csv_data.seek(0)

                # Create a response with the CSV data
                response = Response(
                    csv_data,
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={file_name}"
                    }
                )
                return response

    flash('No health data available for download.', 'danger')
    return redirect(url_for('dashboard'))

# Add a new route to download the entire health_data table
@app.route('/download_entire_health_data_csv')
def download_entire_health_data_csv():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.all()  # Retrieve all health data
            if health_data:
                # Create a list of dictionaries with all columns
                data_list = [
                    {
                        "User ID": data.user_id,
                        "Age": data.age,
                        "Gender": data.gender,
                        "Fever": data.fever,
                        "Heart Rate": data.heart_rate,
                        "Acidity": data.acidity,
                        "Vomiting": data.vomiting,
                        "Headache": data.headache,
                        "Breathlessness": data.breathlessness,
                        "Cough": data.cough,
                        "Anxiety": data.anxiety,
                    }
                    for data in health_data
                ]

                # Create a Pandas DataFrame from the list of dictionaries
                df = pd.DataFrame(data_list)

                # Create a unique file name
                file_name = "entire_health_data.csv"

                # Save the DataFrame to a CSV file in memory
                csv_data = StringIO()
                df.to_csv(csv_data, index=False)

                # Move the file pointer to the beginning of the file
                csv_data.seek(0)

                # Create a response with the CSV data
                response = Response(
                    csv_data,
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={file_name}"
                    }
                )
                return response

    flash('No health data available for download.', 'danger')
    return redirect(url_for('dashboard'))



@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the user ID from the session
    return redirect(url_for('home'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
