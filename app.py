from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3 as sql
from functools import wraps
import pandas as pd
import sys

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'
app.secret_key = "my precious"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in first.")
            return redirect(url_for('login'))
    return wrap


@app.route('/admin/dashboard', methods=['POST', 'GET'])
@login_required
def admin_dashboard():
    connection = sql.connect('database.db')
    course_list = Administration("course_list")

    error = None

    if request.method == 'POST':

        if "AddCourse" in request.form:  # if user clicks on button with name="AddCourse"
            course_list = CreatingCourses(request.form['CourseID'], request.form['CourseName'],
                                          request.form['CourseDescription'])
            return render_template('dashboard-admin.html', url=host, error=error, course_list=course_list)
        elif "DeleteCourse" in request.form:  # if user clicks on button with name="DeleteCourse"
            course_list = DeletingCourses(request.form['DeleteCourseID'])
            return render_template('dashboard-admin.html', url=host, error=error, course_list=course_list)
        else:
            error = 'Invalid input name'

    return render_template('dashboard-admin.html', url=host, error=error, course_list=course_list)


@app.route('/professor/dashboard', methods=['POST', 'GET'])
@login_required
def professor_dashboard():
    connection = sql.connect('database.db')

    name = getName("for_faculty_mem")[0][0]
    course_teaching = ProfessorTeaching()
    print(course_teaching, file=sys.stderr)
    hw_assignments = GenerateCourseAssignments(course_teaching[0][0])
    print(hw_assignments, file=sys.stderr)
    course_exams = GenerateCourseExams(course_teaching[0][0])
    print(course_exams, file=sys.stderr)

    error = None
    if request.method == 'POST':
        result = CreatingAssignments(request.form['FirstName'], request.form['LastName'])
        if result:
            return render_template('dashboard-professor.html', error=error, url=host, result=result, name=name,
                                   hw_assignments=hw_assignments, course_exams=course_exams)
        else:
            error = 'Invalid input name'

    return render_template('dashboard-professor.html', url=host, error=error, name=name, course_teaching=course_teaching,
                           hw_assignments=hw_assignments, course_exams=course_exams)


@app.route('/student/dashboard')
@login_required
def student_dashboard():
    connection = sql.connect('database.db')

    test = connection.execute('SELECT * FROM Test')
    print(test.fetchall(), file=sys.stderr)

    name = getName("for_students")[0][0]
    courses = CheckingInfo("courses") #courses = [('aly8942@lionstate.edu', 'EE320', 1, 'EE212', 1, 'CMPEN454', 2)]
    capstone_courses = CheckingInfo("capstone")[0] #capstone_courses = ("CMPEN454", "CMPSC497", "EE340", "IST558", "STAT414")
    courses1 = []
    for i in range(1, len(courses[0])):
        courses1.append(courses[0][i]) #courses1 = ['EE320', 1, 'EE212', 1, 'CMPEN454', 2]

    course_information = []
    professor_information = []
    for course_id in range(0, len(courses1), 2):
        course_info = connection.execute('SELECT Course_name FROM Courses WHERE Course_id= ?', [courses1[course_id]])

        professor_info = connection.execute('SELECT Name, Email, Office FROM Professors_teaches WHERE Teaching = ?',
                                            [courses1[course_id]])
        course_information.append(course_info.fetchall())
        professor_information.append(professor_info.fetchall())

    personal_info = CheckingInfo("personal_information")
    grades = CheckingInfo("grades")
    all_grades = CheckingInfo("all_grades")

    return render_template('dashboard-student.html', url=host, name=name, courses1=courses1,
                           course_information=course_information, professor_information=professor_information,
                           personal_info=personal_info, grades=grades, all_grades=all_grades,
                           capstone_courses=capstone_courses)


@app.route('/') #home page
def home():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST']) #login page
def login():
    error = None

    student_login_info = student_login()
    professor_login_info = professor_login()

    if request.method == 'POST':

        if request.form['username'] == 'admin@lionstate.edu' and request.form['password'] == 'admin':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        elif (request.form['username'], request.form['password']) in student_login_info:
            session['logged_in'] = True
            session['email'] = request.form['username']
            return redirect(url_for('student_dashboard'))

        elif (request.form['username'], request.form['password']) in professor_login_info:
            session['logged_in'] = True
            session['email'] = request.form['username']
            return redirect(url_for('professor_dashboard'))

        else:
            error = "Invalid username or password. Please try again."
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))


# <-------------------------------------All THE DATABASE QUERIES USED --------------------------------------------->

def student_login():
    connection = sql.connect('database.db')
    student_login_info = connection.execute('SELECT Email, Password FROM Students')
    return student_login_info.fetchall()


def professor_login():
    connection = sql.connect('database.db')
    professor_login_info = connection.execute('SELECT Email, Password FROM Professors')
    return professor_login_info.fetchall()


def getName(users):
    connection = sql.connect('database.db')
    if users == "for_students":
        name = connection.execute('SELECT Name FROM Students WHERE Email = ?', [session['email']])
    elif users == "for_faculty_mem":
        name = connection.execute('SELECT Name FROM Professors WHERE Email = ?', [session['email']])

    return name.fetchall()


def CheckingInfo(item):
    connection = sql.connect('database.db')

    if item == "courses":
        info = connection.execute('SELECT * FROM Enrolls WHERE Email = ?', [session['email']])

    elif item == "capstone":
        info = connection.execute('SELECT COURSES FROM Capstone_courses')

    elif item == "personal_information":
        info = connection.execute('SELECT Name, Age, Gender, Major, Street, ZipCode FROM Students WHERE Email = ?',
                                  [session['email']])

    elif item == "grades":
        info = connection.execute('SELECT * FROM Exam_grades WHERE Email= ?', [session['email']])

    elif item == "all_grades":
        info = connection.execute('SELECT * FROM Students_grades WHERE Email= ?', [session['email']])

    return info.fetchall()


def ProfessorTeaching():
    connection = sql.connect('database.db')
    course_teaching = connection.execute('SELECT Teaching FROM Professors_teaches WHERE Email= ?', [session['email']])
    return course_teaching.fetchall()


def CreatingAssignments(first_name, last_name):
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS users(firstname TEXT, lastname TEXT);')
    connection.execute('INSERT INTO users (firstname, lastname) VALUES (?,?);', (first_name, last_name))
    connection.commit()
    cursor = connection.execute('SELECT * FROM users;')

    return cursor.fetchall()


def CreatingCourses(course_id, course_name, course_description):
    connection = sql.connect('database.db')
    connection.execute('INSERT INTO Courses (Course_id, Course_name, Course_description) VALUES (?,?,?)',
                       (course_id, course_name, course_description))
    connection.commit()
    cursor = connection.execute('SELECT * FROM Courses')

    return cursor.fetchall()


def DeletingCourses(course_id):
    connection = sql.connect('database.db')
    connection.execute('DELETE FROM Courses WHERE Course_id = ?', [course_id])
    connection.commit()
    cursor = connection.execute('SELECT * FROM Courses')

    return cursor.fetchall()


def GenerateCourseAssignments(course_teaching):
    connection = sql.connect('database.db')
    list_of_assignments = connection.execute('SELECT hw_no FROM Homework WHERE course_id=?', [course_teaching])
    return list_of_assignments.fetchall()


def GenerateCourseExams(course_teaching):
    connection = sql.connect('database.db')
    list_of_exams = connection.execute('SELECT exam_no FROM Exams WHERE course_id= ?', [course_teaching])
    return list_of_exams.fetchall()


def Administration(item):
    connection = sql.connect('database.db')

    if item == "course_list":
        info = connection.execute('SELECT * FROM Courses')

    return info.fetchall()


if __name__ == '__main__':
    app.run(debug=True)