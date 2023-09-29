import os
import boto3
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import json
import time
import pymysql


app = Flask(__name__)

app.secret_key = os.urandom(24)

# create a new s3 client 
s3 = boto3.client('s3', 
                  aws_access_key_id="AKIATTVW5OAFBREHIW64",
                  aws_secret_access_key="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",
                  region_name="us-east-1")


# connect to AWS RDS
db_connection = pymysql.connect(
    host="database-1.c80smuniyazj.us-east-2.rds.amazonaws.com",
    user = "admin",
    password = "Bhanu1745",
    database = "info"
)

db_cursor = db_connection.cursor()

# Helper function to create the uploaded files table in the database
def create_table():
    db_cursor.execute('CREATE TABLE IF NOT EXISTS uploaded_files (id INTEGER AUTO_INCREMENT PRIMARY KEY, username TEXT, file_name TEXT, file_url TEXT, email TEXT)')
    db_connection.commit()

# Create the uploaded files table
create_table()

# Helper function to create connection to database
def connect_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)')
    conn.commit()
    conn.close()

# Helper function to insert data into database
def insert_db(username, password, email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
    conn.commit()
    conn.close()


# Helper function to retrieve data from database
def retrieve_db(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Helper function to check if the username exists in the database

def check_username(username, password):
    user = retrieve_db(username)
    if user:
        if user[2] == password:
            return True
        else:
            return False
    else:
        return False
    
# Helper function to insert data into the uploaded files table
def insert_uploaded_files(username, file_name, file_url, email_list):
    for email in email_list:
        db_cursor.execute('INSERT INTO uploaded_files (username, file_name, file_url, email) VALUES (%s, %s, %s, %s)', (username, file_name, file_url, email))
    db_connection.commit()

@app.route('/', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_username(username, password):
            session['username'] = username
            return redirect('/upload')
        else:
            error_msg = 'Invalid username or password'
            return render_template('login.html', error_msg=error_msg)
    
    return render_template('login.html')
    
@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username and password and email:
            connect_db()
            if not retrieve_db(username):
                insert_db(username, password, email)
                return redirect('/dashboard')
            else:
                error_msg = 'Username already exists'
                return render_template('signup.html', error_msg=error_msg)
        else:
            error_msg = 'Please fill in all the fields'
            return render_template('signup.html', error_msg=error_msg)
        
    return render_template('signup.html')

@app.route('/upload', methods=['GET', 'POST'])

def upload():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['file']
            emails = request.form['email']

            if not file or not emails:
                flash ('Please select a file and enter an email address')
                return redirect(url_for('upload'))
            
            filename = secure_filename(file.filename)
            s3.upload_fileobj(file, 'finalcloudproject', filename)

            # AWS lambda function to send email
            client = boto3.client('lambda',
                  aws_access_key_id="AKIATTVW5OAFBREHIW64",
                  aws_secret_access_key="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",
                  region_name="us-east-2")
            email_list = emails.split(',')

            email_list = [email.strip() for email in email_list if email.strip()]

            if not email_list:
                flash ('Please enter a valid email address')
                return redirect(url_for('upload'))
            
            insert_uploaded_files(session['username'], filename, f'https://finalcloudproject.s3.amazonaws.com/{filename}', email_list)

            for email in email_list:
                email = email.strip()
                if email:
                    lambda_payload = {
                        'file_url': f'https://finalcloudproject.s3.amazonaws.com/{filename}',
                        'email': email
                    }

                    response = client.invoke(
                        FunctionName='finallambda',
                        InvocationType='Event',
                        Payload=json.dumps(lambda_payload)
                    )

            return json.dumps({'status': 'File uploaded successfully'}) 
        

            
        
        username = session['username']        
        return render_template('upload.html', username=username)
    else:
        return redirect('/')
    
if __name__ == '__main__':
    app.run(debug=True)