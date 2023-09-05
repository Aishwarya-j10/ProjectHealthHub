import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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
            # Retrieve health data attributes from the form
            age = int(request.form.get('age')) or None
            gender = str(request.form.get('gender')) 
            fever = bool(request.form.get('fever'))
            heart_rate = int(request.form.get('heart_rate'))
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
            # Add similar lines for other health data attributes
            # lst = ['age', 'gender', 'fever', 'heart_rate', 'acidity', 'vomiting', 'headache', 'breathlessness', 'cough', 'anxiety'] 
            # Set default values to None for attributes where no value is provided
            # if age is None:
            #     age = None
            # if gender is None:
            #     gender = None
            
            # if acidity is None:
            #     acidity = None
            # if vomiting is None:
            #     vomiting = None
            # if headache is None:
            #     headache = None
            # if breathlessness is None:
            #     breathlessness = None
            # if cough is None:
            #     cough = None
            # if anxiety is None:
            #     anxiety = None
            # Create a new HealthData record in the database
            existing_health_data = HealthData.query.filter_by(user=user).first()
            if existing_health_data : 
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
                    user=user,
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

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the user ID from the session
    return redirect(url_for('home'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
