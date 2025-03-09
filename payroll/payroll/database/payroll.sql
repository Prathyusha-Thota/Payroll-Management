drop database payroll;
create database payroll;
use payroll;


create table departments(
department_id int auto_increment primary key,
department_name varchar(255) not null
);


create table supervisors(
supervisor_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null,
phone varchar(255) not null,
password varchar(255) not null,
experience varchar(255) not null,
department_id int,
foreign key(department_id) references departments(department_id)
);


create table employee(
employee_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null,
phone varchar(255) not null,
password varchar(255) not null,
gender varchar(255) not null,
role varchar(255) not null,
wage_type varchar(255) not null,
joining_date varchar(255) not null,
ssn varchar(255),
supervisor_id int,
picture varchar(255) not null,
foreign key(supervisor_id) references supervisors(supervisor_id)
);



create table contract(
contract_id int auto_increment primary key,
pay_per_hour varchar(255),
over_time_pay_per_hour varchar(255) ,
food_allows varchar(255),
travelling_allows varchar(255) ,
house_rent_allows varchar(255) ,
health_insurance varchar(255),
bonus varchar(255),
state_tax varchar(255),
monthly_salary varchar(255) ,
income_tax varchar(255),
employee_id int,
foreign key(employee_id) references employee(employee_id)
);



create table transactions(
transaction_id int auto_increment primary key,
clock_in_date_time varchar(255),
clock_out_date_time varchar(255),
attendance_date varchar(255),
total_hours varchar(255),
over_time varchar(255),
date varchar(255),
number_of_days varchar(255),
month_year varchar(255),
employee_id int,
foreign key(employee_id) references employee(employee_id)
);


create table leaves(
leave_id int auto_increment primary key,
start_date varchar(255),
end_date varchar(255),
reason varchar(255),
status varchar(255),
days varchar(255),
hours varchar(255),
employee_id int,
date varchar(255),
foreign key(employee_id) references employee(employee_id)

);

create table leave_days(
leave_day_id int auto_increment primary key,
date varchar(255) not null,
leave_id int,
foreign key(leave_id) references leaves(leave_id)

);



create table paycheck(
paycheck_id int auto_increment primary key,
from_date varchar(255),
to_date varchar(255),
total_working_days varchar(255),
total_leave_days varchar(255),
total_days varchar(255),
total_working_hours varchar(255),
total_leave_hours varchar(255),
total_overtime_hours varchar(255),
basic_salary varchar(255),
state_tax varchar(255),
income_tax varchar(255),
health_insurance varchar(255),
food_allows varchar(255),
travelling_allows varchar(255),
house_rent_allows varchar(255),
payable_amount varchar(255),
bonus varchar(255),
employee_id int,
foreign key(employee_id) references employee(employee_id)
);

