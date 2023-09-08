import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import pandas as pd
from datetime import datetime 
from io import StringIO 
import matplotlib.pyplot as plt 
import seaborn as sns 
import pytz  
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

from sqlalchemy.sql import func
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'not_A_secret'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))

    def __repr__(self):
        return f'<User {self.name}>' 
    

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)  
    datetime = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata'))) 
    gender = db.Column(db.String)
    heart_rate = db.Column(db.Integer)
    anxiety = db.Column(db.Integer) 

    def __repr__(self):
        return f'<HealthData for User {self.id}>'

@app.route('/')
def home():
    return render_template('start.html')

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form.get('password')
    
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id   
            return redirect(url_for('dashboard')) 
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('home')) 
    return render_template('login.html')

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
    
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return render_template('dashboard.html', user=user)
         
        
    
    flash('You need to log in to access the dashboard.', 'danger')
    return redirect(url_for('home'))



@app.route('/add_health_data', methods=['GET', 'POST'])
def add_health_data():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        if user:
            if request.method == 'GET':
               
                return render_template('enter_data.html')  

            elif request.method == 'POST':
                datetime_str = request.form.get('datetime') 
                if datetime_str is not None and datetime_str != '':  
                    health_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M') 
                else : 
                    health_datetime = None  
                    # health_datetime = datetime.strptime(health_datetime, '%Y-%m-%dT%H:%M')  
                   
                # health_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
                age = request.form.get('age')
                gender = request.form.get('gender')
                heart_rate = request.form.get('heart_rate')
                anxiety = request.form.get('anxiety')

                health_data = HealthData(
                    user_id=user.id,
                    datetime=health_datetime,
                    age=age,
                    gender=gender,
                    heart_rate=heart_rate,
                    anxiety=anxiety,
                )
                db.session.add(health_data)
                db.session.commit()
                flash('Health data submitted successfully.', 'success')
                return redirect(url_for('dashboard', user=user))

    flash('You need to log in to submit health data.', 'danger')
    return redirect(url_for('home'))
 
@app.route('/view_data', methods=['GET'])
def view_data():
    print("out of if") 
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            try:
                
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

@app.route('/visualization', methods=['GET'])
def visualizing():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            # try:
                
                health_data = HealthData.query.filter_by(user_id=user_id).all()
                print("User:", user)
                print("Health Data:", health_data)
                image_path = [] 
                image_path = visualizations()
                return render_template('visualizations.html', user=user, health_data=health_data, image_path = image_path)
   
    flash('You need to log in to view health data.', 'danger')
    return redirect(url_for('home'))  

@app.route('/download_health_data_csv')
def download_health_data_csv():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.filter_by(user_id=user_id).all()
            if health_data:
                
                data_list = [
                    {
                        "Date/Time": data.datetime.strftime('%Y-%m-%d %H:%M'), 
                        "Age": data.age,
                        "Gender": data.gender,
                        "Heart Rate": data.heart_rate,
                        "Anxiety Level": data.anxiety,  
                    }
                    for data in health_data
                ]

              
                df = pd.DataFrame(data_list)
                file_name = f"user_{user.id}_health_data.csv"
                csv_data = StringIO()
                df.to_csv(csv_data, index=False)
                csv_data.seek(0)
                response = Response(
                    csv_data,
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={file_name}"
                    }
                )
                return response

    return redirect(url_for('login'))

# Addding a new route to download the entire health_data table
@app.route('/download_entire_health_data_csv')
def download_entire_health_data_csv():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.all()  
            if health_data:
               
                data_list = [
                    {
                        "Date/Time": data.datetime.strftime('%Y-%m-%d %H:%M'), 
                        "Age": data.age,
                        "Gender": data.gender,
                        "Heart Rate": data.heart_rate,
                        "Anxiety Level": data.anxiety, 
                    }
                    for data in health_data
                ]
             
                df = pd.DataFrame(data_list)
            
                
                file_name = "entire_health_data.csv"

                
                csv_data = StringIO()
                df.to_csv(csv_data, index=False)

                
                csv_data.seek(0)

                
                response = Response(
                    csv_data,
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={file_name}"
                    }
                )
                return response

def visualizations():
   
    # df = pd.read_csv("user_1.csv") 
    user_id = session.get('user_id') 
    print("useridaish", user_id) 
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.filter_by(user_id=user_id).all()  
            if health_data:
               
                data_list = [
                    {
                        "Date/Time": data.datetime.strftime('%Y-%m-%d %H:%M'), 
                        "Age": data.age,
                        "Gender": data.gender,
                        "Heart Rate": data.heart_rate,
                        "Anxiety Level": data.anxiety, 
                    }
                    for data in health_data
                ]
             
                df = pd.DataFrame(data_list) 
                df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    
                # Filtering data for a specific month (September 2023)
                start_date = '2023-09-01'
                end_date = '2023-10-01'
                df1 = df[(df['Date/Time'] >= start_date) & (df['Date/Time'] < end_date)] 
    
                # SORTING THE VALUES IN THE DATAFRAME AND RESETTING THE INDEX:
                df1 = df1.sort_values(by='Date/Time').reset_index(drop=True)
                df1.tail()
                selected_columns = ['Heart Rate', 'Anxiety Level'] 
                subset_data = df1[selected_columns] 
                correlation_matrix = subset_data.corr()  
                # CREATING A TIME SERIES PLOT FOR "Heart Rate"
                plt.figure(figsize=(6, 3))
                plt.plot(df1['Date/Time'], df1['Heart Rate'], marker='o', linestyle='-', color='b')
                plt.title('Heart Rate Over Time')
                plt.xlabel('Date')
                plt.ylabel('Heart Rate')
                plt.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()   
                image_path = "static/plot.png"
                plt.savefig(image_path)
    
                # Creating a histogram of anxiety levels for the month: 
                plt.figure(figsize=(6, 3))
                plt.hist(df1['Anxiety Level'], bins=10, edgecolor='y')
                plt.title('Anxiety Level Distribution (September 2023)')
                plt.xlabel('Anxiety Level')
                plt.ylabel('Frequency')
                plt.tight_layout()   
                image_path1 = "static/plot1.png"
                plt.savefig(image_path1) 
                # Create a pie chart
                category_counts = df1['Heart Rate'].value_counts()
                plt.figure(figsize=(5, 5))
                plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140)
                plt.title('Heart Rate Categories')
                plt.axis('equal')  
                image_path2 = "static/plot2.png"
                plt.savefig(image_path2) 
                selected_columns = ['Heart Rate', 'Anxiety Level'] 
                subset_data = df1[selected_columns] 
                correlation_matrix = subset_data.corr()

                # CREATING A HEATMAP TO CHECK HOW ARE ANXIETY AND HEART RATE RELATED: 
                plt.figure(figsize=(4, 3))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=.5)
                plt.title('Correlation Heatmap')
     
                plt.tight_layout() 
                # plt.show()  
                image_path3 = "static/plot3.png"
                plt.savefig(image_path3)
                return (image_path, image_path1, image_path2, image_path3)  

def dframe() : 
    # df = pd.read_csv("user_1.csv") 
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            health_data = HealthData.query.all()  
            if health_data:
               
                data_list = [
                    {
                        "Date/Time": data.datetime.strftime('%Y-%m-%d %H:%M'), 
                        "Age": data.age,
                        "Gender": data.gender,
                        "Heart Rate": data.heart_rate,
                        "Anxiety Level": data.anxiety, 
                    }
                    for data in health_data
                ]
             
                df = pd.DataFrame(data_list) 
                df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    
                # Filtering data for a specific month (September 2023)
                start_date = '2023-09-01'
                end_date = '2023-10-01'
                df1 = df[(df['Date/Time'] >= start_date) & (df['Date/Time'] < end_date)] 
    
                # SORTING THE VALUES IN THE DATAFRAME AND RESETTING THE INDEX:
                df1 = df1.sort_values(by='Date/Time').reset_index(drop=True) 
                return df1 

def model1() : 
    data = pd.read_csv("updated_data1.csv")


    # Selecting features and target variable
    X = data[['Age', 'Heart Rate']].values
    y = (data['Anxiety Level'] == 'High Anxiety').astype(int)  # Binary classification

    # Splitting the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize features
    scaler1 = StandardScaler()
    X_train = scaler1.fit_transform(X_train)
    X_test = scaler1.transform(X_test)

    # Creating a simple neural network model
    model11 = keras.Sequential([
        keras.layers.Input(shape=(X_train.shape[1],)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')  
        ])

    # Compiling the model
    model11.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Training the model
    model11.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1) 

    # Evaluating the model on the test data
    # _, accuracy = model11.evaluate(X_test, y_test)
    # print(f"Test Accuracy: {accuracy}")
    # scaler = StandardScaler() 
    # Making predictions
    # y_pred = model11.predict(X_test)
    # y_pred_binary = (y_pred > 0.5).astype(int)

    # Generate a classification report
    # report = classification_report(y_test, y_pred_binary)
    # print(report) 
    return model11, scaler1 

def prediction() : 
    from sklearn.preprocessing import StandardScaler 
    # df1 = dframe() 
    model2, scaler1 = model1() 
    # Creating a DataFrame to hold the new data: 
    new_age = 21 
    new_heart_rate = 90 
    
    new_data = pd.DataFrame({'Age': [new_age], 'Heart Rate': [new_heart_rate]})
    # scaler = StandardScaler()
    # Scaling the new data using the same scaler as used for training data
    X_new = scaler1.transform(new_data)

    # Making predictions
    predictions = model2.predict(X_new)

    # Converting the predictions to binary (0 or 1) based on a threshold (e.g., 0.5)
    predictions_binary = (predictions > 0.5).astype(int) 
    return predictions_binary 

@app.route('/predicttion', methods=['GET']) 
def pr() : 
    # a = prediction() 
    # df1 = dframe() 
    model2, scaler1 = model1() 
    # Creating a DataFrame to hold the new data: 
    new_age = 21 
    # new_heart_rate = app.heart_rate 
    
    new_data = pd.DataFrame({'Age': [new_age], 'Heart Rate': [app.heart_rate]})
    # scaler = StandardScaler()
    # Scaling the new data using the same scaler as used for training data
    X_new = scaler1.transform(new_data)

    # Making predictions
    predictions = model2.predict(X_new)

    # Converting the predictions to binary (0 or 1) based on a threshold (e.g., 0.5)
    a = (predictions > 0.5).astype(int) 
    
    return render_template('prediction.html', a = a)

@app.route('/store_heart_rate', methods=['POST'])
def store_heart_rate():
    heart_rate = float(request.form.get('heart_rate'))
    
    # Store the heart rate in a variable (you can save it to a database here)
    # For demonstration purposes, we'll store it in a global variable.
    app.heart_rate = heart_rate
    
    return redirect('/prediction')

@app.route('/form', methods=['GET'])
def show_form():
    return render_template('prediction.html', a=None)
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect(url_for('home'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
