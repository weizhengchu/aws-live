from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/fetchdata", methods=['POST'])
def fectdata():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM employee")
    employee = cursor.fetchall()
    return render_template('account.html',employee=employee)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)