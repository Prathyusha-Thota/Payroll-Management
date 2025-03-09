import datetime
import os
import re

import pymysql as pymysql
from flask import Flask, request, session, render_template, redirect


app = Flask(__name__)
app.secret_key = "payroll"

conn = pymysql.connect(host="database-1.cxsoi84264ts.us-east-1.rds.amazonaws.com", user="admin", password="adminroot", db="payroll")
# conn = pymysql.connect(host="localhost", user="root", password="root", db="payroll")
cursor = conn.cursor()

query = {}

import boto3 as boto3
Payroll_Management_System_Access_Key = "AKIAXQIQAGIUTFMOEAHH"
Payroll_Management_System_Secret_Access_Key = ""#add secret key
Payroll_Management_System_bucket = "payroll-s3-bucket"
Payroll_Management_System_Email_Source = 'yourmail@gmail.com'
Payroll_Management_System_s3_client = boto3.client('s3', aws_access_key_id=Payroll_Management_System_Access_Key, aws_secret_access_key=Payroll_Management_System_Secret_Access_Key)
Payroll_Management_System_ses_client = boto3.client('ses', aws_access_key_id=Payroll_Management_System_Access_Key, aws_secret_access_key=Payroll_Management_System_Secret_Access_Key, region_name='us-east-1')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PAYROLL_PATH = APP_ROOT + "/static/employee"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username=='admin' and password=='admin':
        session["role"] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/supervisor_login")
def supervisor_login():
    return render_template("supervisor_login.html")


@app.route("/supervisor_login_action",methods=['post'])
def supervisor_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from supervisors where email='"+str(email)+"' and password='"+str(password)+"'")
    if count > 0:
        cursor.execute("select * from supervisors where email='" + str(email) + "' and password='" + str(password) + "'")
        supervisor = cursor.fetchone()
        supervisor_name = supervisor[1]
        emails = Payroll_Management_System_ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        if email in emails['Identities']:
            email_msg = 'Hello ' + supervisor_name +' '+ 'You Have Successfully Logged into Payroll Management System Website'
            Payroll_Management_System_ses_client.send_email(Source=Payroll_Management_System_Email_Source,
                                                             Destination={'ToAddresses': [email]},
                                                             Message={
                                                                 'Subject': {'Data': email_msg, 'Charset': 'utf-8'},
                                                                 'Body': {'Html': {'Data': email_msg,
                                                                                   'Charset': 'utf-8'}}})
        else:
            return render_template("message.html", message="Verify your email by the link that has sent to registered your email.")
        session["supervisor_id"] = supervisor[0]
        session['role'] = 'supervisor'
        return redirect("/supervisor_home")
    else:
        return render_template("message.html", message="Invalid login details")


@app.route("/supervisor_home")
def supervisor_home():
    return render_template("supervisor_home.html")



@app.route("/employee_login")
def employee_login():
    return render_template("employee_login.html")


@app.route("/employee_login_action", methods=['post'])
def employee_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from employee where email='"+str(email)+"' and password='"+str(password)+"'")
    if count > 0:
        cursor.execute("select * from employee where email='"+str(email)+"' and password='"+str(password)+"'")
        employee = cursor.fetchone()
        employee_name = employee[1]
        email = employee[2]
        emails = Payroll_Management_System_ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        if email in emails['Identities']:
            email_msg = 'Hello ' + employee_name +' '+ 'You Have Successfully Logged into Payroll Management System Website'
            Payroll_Management_System_ses_client.send_email(Source=Payroll_Management_System_Email_Source,
                                                            Destination={'ToAddresses': [email]},
                                                            Message={
                                                                'Subject': {'Data': email_msg, 'Charset': 'utf-8'},
                                                                'Body': {'Html': {'Data': email_msg,
                                                                                  'Charset': 'utf-8'}}})
        else:
            return render_template("message.html",
                                   message="Verify your email by the link that has sent to registered your email.")
        session["employee_id"] = employee[0]
        session['role'] = 'employee'
        return redirect("/employee_home")
    else:
        return render_template("message.html", message="invalid login details")




@app.route("/employee_home")
def employee_home():
    return render_template("employee_home.html")        



@app.route("/departments")
def departments():
    message = request.args.get("message")
    if message == None:
        message =""
    cursor.execute("select * from departments")
    departments = cursor.fetchall()
    return render_template("departments.html", departments=departments,message=message)


@app.route("/departments_action", methods=['post'])
def departments_action():
    department_name = request.form.get("department_name")
    count = cursor.execute("select * from departments where department_name='"+str(department_name)+"'")
    if count == 0:
        cursor.execute("insert into departments (department_name)values('"+str(department_name)+"')")
        conn.commit()
        return redirect("departments?message=Departments added successfully")
    else:
        return redirect("departments?message=Departments already exits")






@app.route("/supervisor")
def supervisor():
    message = request.args.get("message")
    cursor.execute("select * from departments")
    departments = cursor.fetchall()
    cursor.execute("select * from departments")
    departments2 = cursor.fetchall()
    department_id = request.args.get("department_id")
    if department_id == None:
        department_id = ""
    if department_id == "":
        cursor.execute("select * from supervisors")
        supervisors = cursor.fetchall()
    else:
        cursor.execute("select * from supervisors where department_id='"+str(department_id)+"'")
        supervisors = cursor.fetchall()
    return render_template("supervisor.html", departments=departments,departments2=departments2, supervisors=supervisors, department_id=department_id, message=message, get_departments_by_department_id=get_departments_by_department_id, str=str)

@app.route("/add_supervisor_action",methods=['post'])
def add_supervisor_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    experience = request.form.get("experience")
    department_id = request.form.get("department_id")
    count = cursor.execute("select * from supervisors where email='"+str(email)+"' or phone='"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into supervisors(name,email,phone,password,experience,department_id)values('"+str(name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(experience)+"','"+str(department_id)+"')")
        conn.commit()
        Payroll_Management_System_ses_client.verify_email_address(
            EmailAddress=email
        )
        return redirect("supervisor?message=supervisor added successfully")
    else:
        return redirect("supervisor?message=supervisor already exits")


def get_departments_by_department_id(department_id):
    cursor.execute("select * from departments where department_id='"+str(department_id)+"'")
    department = cursor.fetchone()
    return department






@app.route("/employee")
def employee():
    keyword = request.args.get("keyword")
    sql = ""
    if keyword == None:
        keyword = ""
    if session["role"] == "admin":
        if keyword == "":
            sql = "select * from employee"
        else:
            sql = "select * from employee where (name like '%"+str(keyword)+"%' or phone like '%"+str(keyword)+"%')"
    elif session["role"] == "supervisor":
        supervisor_id = session["supervisor_id"]
        if keyword == "":
            sql = "select * from employee where supervisor_id='"+str(supervisor_id)+"'"
        else:
            sql = "select * from employee where supervisor_id='" + str(supervisor_id) + "' and (name like '%"+str(keyword)+"%' or phone like '%"+str(keyword)+"%')"
    cursor.execute(sql)
    employees = cursor.fetchall()
    return render_template("employee.html", employees=employees, keyword=keyword, get_contract_by_employee_id=get_contract_by_employee_id, get_supervisor_by_supervisor_id=get_supervisor_by_supervisor_id)



@app.route("/employee_action",methods=['post'])
def employee_action():
    ssn = request.form.get("ssn")
    name = request.form.get("name")
    email = request.form.get("email")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    password = request.form.get("password")
    role = request.form.get("role")
    wage_type = request.form.get("wage_type")
    joining_date = request.form.get("joining_date")
    picture = request.files.get("picture")
    path = PAYROLL_PATH + "/" + picture.filename
    picture.save(path)
    Payroll_Management_System_s3_client.upload_file(path, Payroll_Management_System_bucket, picture.filename)
    joining_date = datetime.datetime.strptime(joining_date, "%Y-%m-%d")
    supervisor_id = session["supervisor_id"]
    count = cursor.execute("select * from employee where email='"+str(email)+"'")
    if count > 0:
        return redirect("employee?message=email already exits")
    count2 = cursor.execute("select * from employee where ssn='" + str(ssn) + "'")
    if count2 > 0:
        return redirect("employee?message=employee_id already assigned")
    cursor.execute("insert into employee(supervisor_id,name,email,phone,password,gender,role,wage_type,joining_date,ssn,picture) values('"+str(supervisor_id)+"','"+str(name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(gender)+"','"+str(role)+"','"+str(wage_type)+"','"+str(joining_date)+"','"+str(ssn)+"','"+str(picture.filename)+"')")
    conn.commit()
    Payroll_Management_System_ses_client.verify_email_address(
        EmailAddress=email
    )
    return redirect("employee?message=employee added successfully")


def get_contract_by_employee_id(employee_id):
    cursor.execute("select * from contract where employee_id='"+str(employee_id)+"'")
    contract = cursor.fetchone()
    return contract

def get_supervisor_by_supervisor_id(supervisor_id):
    cursor.execute("select * from supervisors where supervisor_id='"+str(supervisor_id)+"' ")
    supervisor = cursor.fetchone()
    return supervisor




@app.route("/add_contract")
def add_contract():
    employee_id = request.args.get("employee_id")
    cursor.execute("select * from employee where employee_id='"+str(employee_id)+"'")
    employee = cursor.fetchone()
    return render_template("add_contract.html", employee_id=employee_id, employee=employee)

@app.route("/add_contract_action",methods=['post'])
def add_contract_action():
    employee_id = request.form.get("employee_id")
    pay_per_hour = request.form.get("pay_per_hour")
    over_time_pay_per_hour = request.form.get("over_time_pay_per_hour")
    food_allows = request.form.get("food_allows")
    travelling_allows = request.form.get("travelling_allows")
    house_rent_allows = request.form.get("house_rent_allows")
    health_insurance = request.form.get("health_insurance")
    state_tax = request.form.get("state_tax")
    monthly_salary = request.form.get("monthly_salary")
    income_tax = request.form.get("income_tax")
    cursor.execute("insert into contract(employee_id,pay_per_hour,over_time_pay_per_hour,food_allows,travelling_allows,house_rent_allows,health_insurance,state_tax,monthly_salary,income_tax) "
                   "values('"+str(employee_id)+"','"+str(pay_per_hour)+"','"+str(over_time_pay_per_hour)+"','"+str(food_allows)+"','"+str(travelling_allows)+"','"+str(house_rent_allows)+"','"+str(health_insurance)+"','"+str(state_tax)+"','"+str(monthly_salary)+"','"+str(income_tax)+"')")
    conn.commit()
    return redirect("/employee")

@app.route("/transactions")
def transactions():
    employee_id = request.args.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
    cursor.execute("select * from transactions where employee_id='"+str(employee_id)+"' ")
    transactions = cursor.fetchall()
    transactions = list(transactions)
    transactions.reverse()
    return render_template("transactions.html",employee_id=employee_id, transactions=transactions)


@app.route("/transactions_action", methods=['post'])
def transactions_action():
    clock_in_date_time = request.form.get("clock_in_date_time") 
    clock_in_date_time = datetime.datetime.strptime(clock_in_date_time, "%Y-%m-%dT%H:%M")
    clock_out_date_time = request.form.get("clock_out_date_time")
    clock_out_date_time = datetime.datetime.strptime(clock_out_date_time, "%Y-%m-%dT%H:%M")
    diff = clock_out_date_time - clock_in_date_time
    seconds = diff.seconds
    total_hours = seconds/3600
    total_hours =int(total_hours)
    month = clock_in_date_time.strftime("%h")
    year = clock_in_date_time.strftime("%Y")
    month_year = str(month)+"-"+str(year)
    over_time = request.form.get("over_time")
    date = clock_in_date_time.strftime("%Y-%m-%d")
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    employee_id = request.form.get("employee_id")
    if session['role'] == 'employee':
        employee_id = session['employee_id']
    count = cursor.execute("select * from transactions where employee_id='"+str(employee_id)+"' and ((clock_in_date_time >= '"+str(clock_in_date_time)+"' and clock_in_date_time<= '"+str(clock_out_date_time)+"' and clock_out_date_time >='"+str(clock_in_date_time)+"' and clock_out_date_time >= '"+str(clock_out_date_time)+"') or (clock_in_date_time <= '"+str(clock_in_date_time)+"' and clock_in_date_time <= '"+str(clock_out_date_time)+"' and clock_out_date_time >= '"+str(clock_in_date_time)+"' and clock_out_date_time <= '"+str(clock_out_date_time)+"') or (clock_in_date_time <= '"+str(clock_in_date_time)+"' and clock_in_date_time <= '"+str(clock_out_date_time)+"' and clock_out_date_time >= '"+str(clock_in_date_time)+"' and clock_out_date_time >= '"+str(clock_out_date_time)+"') or (clock_in_date_time <= '"+str(clock_out_date_time)+"' and clock_in_date_time <= '"+str(clock_out_date_time)+"' and clock_out_date_time <= '"+str(clock_in_date_time)+"' and clock_out_date_time >= '"+str(clock_out_date_time)+"'))")

    if count==0:
        attendance_date = clock_in_date_time.strftime("%d-%m-%Y")
        clock_in_date_time2 = datetime.datetime.strptime(str(clock_in_date_time),"%Y-%m-%d %H:%M:%S")
        clock_out_date_time2= datetime.datetime.strptime(str(clock_out_date_time), "%Y-%m-%d %H:%M:%S")
        clock_in_date_time2 = clock_in_date_time2.date()
        clock_out_date_time2 = clock_out_date_time2.date()
        count2 = cursor.execute("select * from leaves where employee_id='" + str(
            employee_id) + "' and status='Approved' and ((start_date >= '" + str(
            clock_in_date_time2) + "' and start_date<= '" + str(
            clock_out_date_time2) + "' and end_date >='" + str(
            clock_in_date_time2) + "' and end_date >= '" + str(
            clock_out_date_time2) + "') or (start_date <= '" + str(
            clock_in_date_time2) + "' and start_date <= '" + str(
            clock_out_date_time2) + "' and end_date >= '" + str(
            clock_in_date_time2) + "' and end_date <= '" + str(
            clock_out_date_time2) + "') or (start_date <= '" + str(
            clock_in_date_time2) + "' and start_date <= '" + str(
            clock_out_date_time2) + "' and end_date >= '" + str(
            clock_in_date_time2) + "' and end_date >= '" + str(
            clock_out_date_time2) + "') or (start_date <= '" + str(
            clock_out_date_time2) + "' and start_date <= '" + str(
            clock_out_date_time2) + "' and end_date <= '" + str(
            clock_in_date_time2) + "' and end_date >= '" + str(clock_out_date_time2) + "'))")
        if count2>0:
            return render_template("smessage.html", message="Employee On Leave, You can not add Working Hour")
        else:
            cursor.execute("insert into transactions (employee_id,clock_in_date_time,clock_out_date_time,attendance_date,total_hours,over_time,date,number_of_days,month_year) "
                           "values('"+str(employee_id)+"','"+str(clock_in_date_time)+"','"+str(clock_out_date_time)+"','"+str(attendance_date)+"','"+str(total_hours)+"','"+str(over_time)+"','"+str(date)+"','1','"+str(month_year)+"')")
            conn.commit()
            return redirect("/transactions?employee_id="+str(employee_id))
    else:
        return render_template("smessage.html",message="Working Hour Already Added On This Dates")



@app.route("/leaves")
def leaves():
    sql = ""
    if session['role'] == 'employee':
        employee_id = session['employee_id']
        sql = "select * from leaves where employee_id='"+str(employee_id)+"'"
    elif session['role'] =='admin':
        employee_id = request.args.get("employee_id")
        if employee_id == None:
            sql = "select * from leaves"
        else:
            sql = "select * from leaves where employee_id='"+str(employee_id)+"'"
    elif session['role'] == 'supervisor':
        employee_id = request.args.get("employee_id")
        supervisor_id = session['supervisor_id']
        if employee_id == None:
            sql = "select * from leaves  where employee_id in(select employee_id from employee where supervisor_id='" + str(supervisor_id) + "') "
        else:
            sql = "select * from leaves where employee_id='"+str(employee_id)+"'"
    cursor.execute(sql)
    leaves = cursor.fetchall()
    leaves = list(leaves)
    leaves.reverse()
    return render_template("leaves.html", get_leave_date_format=get_leave_date_format,leaves=leaves, get_employee_by_employee_id=get_employee_by_employee_id)


def get_employee_by_employee_id(employee_id):
    cursor.execute("select * from employee where employee_id='"+str(employee_id)+"'")
    employee = cursor.fetchone()
    return employee



@app.route("/leaves_action", methods=['post'])
def leaves_action():
    start_date = request.form.get("start_date")
    start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date = request.form.get("end_date")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    diff = end_date - start_date
    days = diff.days
    days = days + 1
    hours = days * 8
    reason = request.form.get("reason")
    status = 'applied'
    date = datetime.datetime.now()
    employee_id = session["employee_id"]
    dates = []
    start_date2 = start_date
    while start_date2 <= end_date:
        dates.append(start_date2.strftime("%d-%m-%Y"))
        start_date2 = start_date2 + datetime.timedelta(days=1)
    cursor.execute("insert into leaves (start_date,end_date,reason,status,date,employee_id,days,hours) values ('"+str(start_date)+"','"+str(end_date)+"','"+str(reason)+"','"+str(status)+"','"+str(date)+"','"+str(employee_id)+"','"+str(days)+"','"+str(hours)+"')")
    conn.commit()
    leave_id = cursor.lastrowid
    for my_date in dates:
        cursor.execute("insert into leave_days (leave_id,date) values('"+str(leave_id)+"','"+str(my_date)+"')")
        conn.commit()
    return redirect("leaves?message=applied for leave")


@app.route("/set_status")
def set_status():
    leave_id = request.args.get("leave_id")
    status = request.args.get("status")
    cursor.execute("update leaves set status='"+str(status)+"' where leave_id='"+str(leave_id)+"'")
    conn.commit()
    if session['role'] == 'supervisor':
        return render_template("smessage.html", message=status)
    else:
        return render_template("emessage.html", message=status)


@app.route("/reject_leave")
def reject_leave():
    leave_id = request.args.get("leave_id")
    status = request.args.get("status")
    return render_template("reject_leave.html",leave_id=leave_id, status=status)


@app.route("/reject_leave_action", methods=['post'])
def reject_leave_action():
    leave_id = request.form.get("leave_id")
    status = request.form.get("status")
    reason = request.form.get("reason")
    cursor.execute("update leaves set status='"+str(status)+"',reason='"+str(reason)+"' where leave_id='"+str(leave_id)+"'")
    conn.commit()
    if session['role'] == 'supervisor':
        return render_template("smessage.html", message=status)
    else:
        return render_template("emessage.html", message=status)




@app.route("/paychecks")
def paychecks():
    employee_id = request.args.get("employee_id")
    cursor.execute("select * from paycheck where employee_id='"+str(employee_id)+"'")
    paychecks = cursor.fetchall()
    paychecks = list(paychecks)
    paychecks.reverse()
    return render_template("paychecks.html", paychecks=paychecks, employee_id=employee_id, round=round,get_leave_date_format=get_leave_date_format)



@app.route("/generate_pay_check")
def generate_pay_check():
    employee_id = request.args.get("employee_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    if from_date == None:
        from_date = datetime.datetime.now()
        to_date = from_date + datetime.timedelta(days=30)
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")
    from_date2 = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date2 = datetime.datetime.strptime(to_date, "%Y-%m-%d")
    dates = []
    while from_date2 <= to_date2:
        dates.append(from_date2.strftime("%d-%m-%Y"))
        from_date2 = from_date2 + datetime.timedelta(days=1)
    cursor.execute("select * from employee where employee_id='"+str(employee_id)+"'")
    employee = cursor.fetchone()
    cursor.execute("select * from contract where employee_id='"+str(employee_id)+"'")
    contract = cursor.fetchone()


    total_working_hours = 0
    total_overtime_hours = 0
    total_days = 0
    total_working_days = 0
    total_leave_days = 0
    for date in dates:
        transaction = get_transaction_by_date_and_employee_id(date, employee_id)
        if transaction != None:
            total_working_hours = total_working_hours + int(transaction[4])
            total_overtime_hours = total_overtime_hours + int(transaction[5])
            total_days = total_days + 1
            total_working_days = total_working_days + 1
        else:
            leave = get_leave_by_date_and_employee_id(date, employee_id)
            if leave != None:
                total_days = total_days + 1
                total_leave_days = total_leave_days + 1
    total_leave_hours = total_leave_days * 8
    if employee[7]=='monthly':
       basic_salary = float(total_working_hours) * float(contract[9]) + float(total_overtime_hours) * float(contract[2])
    else:
        basic_salary = float(total_working_hours) * float(contract[1]) + float(total_overtime_hours) * float(contract[2])
    state_tax = basic_salary * float(contract[8])/100
    income_tax = basic_salary * float(contract[10]) / 100
    payable_amount = float(basic_salary) - float(state_tax) - float(income_tax) - float(contract[6]) + float(contract[3]) + float(contract[4])+ float(contract[5])
    return render_template("generate_pay_check.html",employee=employee,contract=contract, dates=dates, employee_id=employee_id,from_date=from_date,to_date=to_date, get_transaction_by_date_and_employee_id=get_transaction_by_date_and_employee_id, get_leave_by_date_and_employee_id=get_leave_by_date_and_employee_id, int=int, round=round,
                           total_working_days=total_working_days,total_leave_days=total_leave_days,total_days=total_days,total_working_hours=total_working_hours, total_leave_hours=total_leave_hours, total_overtime_hours=total_overtime_hours,
                           basic_salary=basic_salary,state_tax=state_tax, income_tax=income_tax,
                           payable_amount=payable_amount,get_leave_date_format=get_leave_date_format,get_transaction_format=get_transaction_format)


def get_leave_date_format(leave_date):
    date = datetime.datetime.strptime(leave_date,"%Y-%m-%d %H:%M:%S")
    leave_date = date.date()
    return leave_date

def get_transaction_format(date):
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
    time = str(date.strftime("%I")) + ":" + str(date.strftime("%M")) + " " + str(date.strftime("%p"))
    return time


def get_transaction_by_date_and_employee_id(date,employee_id):
    cursor.execute("select * from transactions where attendance_date='"+str(date)+"' and employee_id='"+str(employee_id)+"'")
    transaction = cursor.fetchone()
    return transaction

def get_leave_by_date_and_employee_id(date,employee_id):
    cursor.execute("SELECT * FROM leave_days WHERE date = '"+str(date)+"' and leave_id in (select leave_id from leaves where status='Approved' and employee_id = '"+str(employee_id)+"')")
    conn.commit()
    leave = cursor.fetchone()
    if leave!=None:
        cursor.execute("select * from leaves where leave_id='"+str(leave[2])+"'")
        leave = cursor.fetchone()
    return leave


@app.route("/generate_pay_check_action", methods=['post'])
def generate_pay_check_action():
    employee_id = request.form.get("employee_id")
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    from_date =datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date =datetime.datetime.strptime(to_date, "%Y-%m-%d")
    total_working_days = request.form.get("total_working_days")
    total_leave_days = request.form.get("total_leave_days")
    total_days = request.form.get("total_days")
    total_working_hours = request.form.get("total_working_hours")
    total_leave_hours = request.form.get("total_leave_hours")
    total_overtime_hours = request.form.get("total_overtime_hours")
    basic_salary = request.form.get("basic_salary")
    state_tax = request.form.get("state_tax")
    income_tax = request.form.get("income_tax")
    health_insurance = request.form.get("health_insurance")
    food_allows = request.form.get("food_allows")
    travelling_allows = request.form.get("travelling_allows")
    house_rent_allows = request.form.get("house_rent_allows")
    payable_amount = request.form.get("payable_amount")
    bonus = request.form.get("bonus")
    payable_amount = float(payable_amount) + int(bonus)
    cursor.execute("insert into paycheck(employee_id,from_date,to_date,total_working_days,total_leave_days,total_days,total_working_hours,total_leave_hours,total_overtime_hours,basic_salary,state_tax,income_tax,health_insurance,food_allows,travelling_allows,house_rent_allows,payable_amount,bonus)"
                   ""
                   " values('"+str(employee_id)+"','"+str(from_date)+"','"+str(to_date)+"','"+str(total_working_days)+"','"+str(total_leave_days)+"','"+str(total_days)+"','"+str(total_working_hours)+"','"+str(total_leave_hours)+"','"+str(total_overtime_hours)+"','"+str(basic_salary)+"','"+str(state_tax)+"','"+str(income_tax)+"','"+str(health_insurance)+"','"+str(food_allows)+"','"+str(travelling_allows)+"','"+str(house_rent_allows)+"','"+str(payable_amount)+"','"+str(bonus)+"')")
    conn.commit()
    return redirect("paychecks?message=paychecks generated successfully&employee_id="+str(employee_id))



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



app.run(debug=True,host="0.0.0.0",port=80)