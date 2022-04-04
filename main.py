from flask import Flask, redirect, render_template, request, url_for
from pymysql import connections
import os
import boto3
from config import *
import json

app = Flask(__name__,template_folder='template')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

client = boto3.client('s3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token
        )

session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token
        )

s3 = session.resource('s3')
my_bucket = s3.Bucket('desmondchongsoonchuen-employee')

output = {}
table = 'employee'
cursor = db_conn.cursor()

userName = 'Admin'
pwd = 'password'
valid1 = ['False']

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('login.html', valid = valid1[0])

@app.route('/profile', methods = ['GET','POST'])
def profile():

    username = request.form['username']
    password = request.form['password']
        
    if username == userName and password == pwd:

        valid1[0] = 'False'
        return redirect(url_for('manage'))
    else:
        valid1[0] = 'True'
        return redirect(url_for('login'))

@app.route('/manage')
def manage():

    SQL = 'select emp_id, emp_name, email from employee'
    cursor.execute(SQL)
    data = cursor.fetchall()
    data = list(map(list,data))
    return render_template('manage.html', myData = data)

@app.route("/addEmp", methods=['GET', 'POST'])
def add():
    return render_template('addData.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():

    emp_id = request.form['emp_id']
    emp_name = request.form['emp_name']
    emp_ic = request.form['emp_ic']
    emp_dob = request.form['emp_dob']
    gender = request.form['gender']
    email = request.form['email']
    benefits = request.form['benefits']
    payroll = request.form['payroll']
    hireddate = request.form['hireddate']
    leavingdate = request.form['leavingdate']
    emp_photo = request.files['emp_photo']

    insert_emp = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


    cursor = db_conn.cursor()


    try:
        cursor.execute(insert_emp, (emp_id, emp_name, email, emp_ic, emp_dob, gender, benefits, payroll, hireddate, leavingdate))
        db_conn.commit()
        fname = emp_photo.filename
        fileFormat = fname.split('.')[1]
        emp_photo_name = str(emp_id) +'.'+fileFormat

        client.upload_fileobj(emp_photo, custombucket, emp_photo_name)


    finally:
        cursor.close()

    print("Employee has been added ")
    return redirect(url_for('manage'))

@app.route('/delete/<int:id>',methods=['POST','GET'])
def deleteData(id):
    data = id

    SQL_Delete = "Delete from employee where emp_id = {ID}".format(ID=data)
    cursor.execute(SQL_Delete)
    db_conn.commit()

    return redirect(url_for('manage'))

@app.route('/delete',methods=['POST','GET'])
def deleteMultiple():
    data = request.form['listID']
    data = json.loads(data)
    for n in data:
        SQL_Delete = "Delete from employee where emp_id = {ID}".format(ID=n)
        cursor.execute(SQL_Delete)
        db_conn.commit()

    return redirect(url_for('manage')) 

@app.route("/fetchdata", methods=['GET','POST'])
def fectdata():

    # s3 = boto3.resource('s3')
    # my_bucket = s3.Bucket(custombucket)
    # s3_file = BytesIO()

    emp_id = request.form.get('empButton')
    cursor1 = db_conn.cursor()
    cursor2 = db_conn.cursor()
    cursor1.execute("SELECT * FROM employee")
    employee = cursor1.fetchall()
    sqls = "SELECT * FROM Attendence where emp_id = {s}".format(s=emp_id)
    cursor2.execute(sqls)
    datedetail= cursor2.fetchall()
    datedetail=list(map(list,datedetail))
    detail =[]
    k = 0
    
    
    print(employee[0][0])
    for x in employee:
        print(x)
        if emp_id == x[0]:
            detail.append(x[0])
            detail.append(x[1])
            detail.append(x[2])
            detail.append(x[3])
            detail.append(x[4])
            detail.append(x[5])
            detail.append(x[6])
            detail.append(x[7])
            detail.append(x[8])
            detail.append(x[9])
            print(detail)
            
            working_directory = r"C:\Users\Desmond\Documents\Taruc\Year 2 Sem 3\Cloud Computing\Assignment\static\image"
            #summaries = your_bucket.objects.all()
            
            for file in my_bucket.objects.all():
                if file.key.startswith(emp_id):
                    local_file_name = os.path.join(working_directory, file.key.split("/")[0])
                    print(f"Downloading {file.key} to {local_file_name}")
                    my_bucket.download_file(file.key,local_file_name)
                    detail.append(file.key)         
                    print(f"Successful Downloading  to {local_file_name}")
                    
           
    print(detail)
    return render_template('account.html', detail=detail,datedetail=datedetail)

@app.route('/editEmp',methods=['POST','GET'])
def editEmp():
    emp_id = request.form['empID2']

    cursor = db_conn.cursor()
    sql = "SELECT * FROM employee where emp_id = {s}".format(s=emp_id)
    cursor.execute(sql)
    empData = cursor.fetchall()

    return render_template("editData.html",data=empData[0])

@app.route("/updateemp", methods=['POST','GET'])
def UpdateEmp():

    emp_id = request.form.get('emp_id_')
    emp_name = request.form.get('emp_name_')
    emp_ic = request.form.get('emp_ic_')
    emp_dob = request.form.get('emp_dob_')
    gender = request.form.get('gender_')
    email = request.form.get('email_')
    benefits = request.form.get('benefits_')
    payroll = request.form.get('payroll_')
    hireddate = request.form.get('hireddate_')
    leavingdate = request.form.get('leavingdate_')


    cursor = db_conn.cursor()
    update_sql = "UPDATE employee SET emp_id = %s, emp_name = %s, email = %s, emp_ic = %s, emp_dob = %s, gender = %s, benefits = %s, payroll = %s, hireddate = %s, leavingdate = %s WHERE emp_id = %s"
    cursor.execute(update_sql,(emp_id,emp_name,email,emp_ic,emp_dob,gender,benefits,payroll, hireddate, leavingdate,emp_id))
    db_conn.commit()

    return redirect(url_for('manage'))

if __name__ == '__main__':
    app.run(debug=True)