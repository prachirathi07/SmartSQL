import sqlite3
import pandas as pd
import os
from faker import Faker
import random

# Initialize faker for generating realistic student data
fake = Faker()

# Create or connect to the SQLite database
def create_student_database():
    print("Creating enhanced student database...")
    connection = sqlite3.connect("student.db")
    cursor = connection.cursor()
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS STUDENT_GRADES")
    cursor.execute("DROP TABLE IF EXISTS STUDENT")
    cursor.execute("DROP TABLE IF EXISTS COURSE")
    cursor.execute("DROP TABLE IF EXISTS TEACHER")
    
    # Create TEACHER table
    cursor.execute("""
    CREATE TABLE TEACHER (
        TEACHER_ID INTEGER PRIMARY KEY,
        NAME VARCHAR(50),
        DEPARTMENT VARCHAR(25),
        YEARS_EXPERIENCE INTEGER,
        EMAIL VARCHAR(100)
    )
    """)
    
    # Create COURSE table
    cursor.execute("""
    CREATE TABLE COURSE (
        COURSE_ID INTEGER PRIMARY KEY,
        NAME VARCHAR(50),
        DEPARTMENT VARCHAR(25),
        CREDIT_HOURS INTEGER,
        TEACHER_ID INTEGER,
        FOREIGN KEY (TEACHER_ID) REFERENCES TEACHER(TEACHER_ID)
    )
    """)
    
    # Create STUDENT table with more fields
    cursor.execute("""
    CREATE TABLE STUDENT (
        STUDENT_ID INTEGER PRIMARY KEY,
        NAME VARCHAR(50),
        CLASS VARCHAR(25),
        SECTION VARCHAR(25),
        ENROLLMENT_DATE DATE,
        EMAIL VARCHAR(100),
        GRADUATION_YEAR INTEGER
    )
    """)
    
    # Create STUDENT_GRADES table for normalized structure
    cursor.execute("""
    CREATE TABLE STUDENT_GRADES (
        ID INTEGER PRIMARY KEY,
        STUDENT_ID INTEGER,
        COURSE_ID INTEGER,
        SEMESTER VARCHAR(25),
        YEAR INTEGER,
        MARKS FLOAT,
        GRADE CHAR(2),
        FOREIGN KEY (STUDENT_ID) REFERENCES STUDENT(STUDENT_ID),
        FOREIGN KEY (COURSE_ID) REFERENCES COURSE(COURSE_ID)
    )
    """)
    
    # Generate and insert sample data
    # Teachers
    teachers = []
    departments = ["Computer Science", "Mathematics", "Physics", "Engineering", "Biology"]
    for i in range(1, 11):
        teacher = (
            i,
            fake.name(),
            random.choice(departments),
            random.randint(1, 20),
            fake.email()
        )
        teachers.append(teacher)
        cursor.execute("INSERT INTO TEACHER VALUES (?, ?, ?, ?, ?)", teacher)
    
    # Courses
    courses = []
    course_names = [
        "Introduction to Programming", "Data Structures", "Algorithms", 
        "Machine Learning", "Artificial Intelligence", "Database Systems",
        "Computer Networks", "Operating Systems", "Software Engineering",
        "Calculus I", "Linear Algebra", "Statistics", "Physics I",
        "Digital Logic", "Computer Architecture", "Web Development"
    ]
    
    for i in range(1, len(course_names) + 1):
        dept = random.choice(departments)
        course = (
            i,
            course_names[i-1],
            dept,
            random.choice([3, 4, 5]),
            random.choice([t[0] for t in teachers])
        )
        courses.append(course)
        cursor.execute("INSERT INTO COURSE VALUES (?, ?, ?, ?, ?)", course)
    
    # Students
    students = []
    classes = ["AI_ML", "CS", "DSA", "IoT", "Cybersecurity"]
    sections = ["A", "B", "C"]
    years = [2023, 2024, 2025, 2026]
    
    for i in range(1, 101):  # Generate 100 students
        student = (
            i,
            fake.name(),
            random.choice(classes),
            random.choice(sections),
            fake.date_between(start_date="-3y", end_date="today"),
            fake.email(),
            random.choice(years)
        )
        students.append(student)
        cursor.execute("INSERT INTO STUDENT VALUES (?, ?, ?, ?, ?, ?, ?)", student)
    
    # Student Grades
    semesters = ["Fall", "Spring", "Summer"]
    grades_map = {
        range(0, 50): "F",
        range(50, 60): "D",
        range(60, 70): "C",
        range(70, 80): "B",
        range(80, 90): "B+",
        range(90, 101): "A"
    }
    
    grade_id = 1
    for student in students:
        # Each student takes 3-6 random courses
        num_courses = random.randint(3, 6)
        taken_courses = random.sample(courses, num_courses)
        
        for course in taken_courses:
            marks = random.randint(35, 100)
            grade = next(g for r, g in grades_map.items() if marks in r)
            
            grade_entry = (
                grade_id,
                student[0],
                course[0],
                random.choice(semesters),
                random.randint(2022, 2024),
                marks,
                grade
            )
            cursor.execute("INSERT INTO STUDENT_GRADES VALUES (?, ?, ?, ?, ?, ?, ?)", grade_entry)
            grade_id += 1
    
    # Create some views for convenience
    cursor.execute("""
    CREATE VIEW student_performance AS
    SELECT 
        s.STUDENT_ID,
        s.NAME as STUDENT_NAME,
        s.CLASS,
        s.SECTION,
        c.NAME as COURSE_NAME,
        c.DEPARTMENT,
        sg.MARKS,
        sg.GRADE,
        t.NAME as TEACHER_NAME
    FROM STUDENT s
    JOIN STUDENT_GRADES sg ON s.STUDENT_ID = sg.STUDENT_ID
    JOIN COURSE c ON sg.COURSE_ID = c.COURSE_ID
    JOIN TEACHER t ON c.TEACHER_ID = t.TEACHER_ID
    """)
    
    # Commit and create a summary report
    connection.commit()
    
    # Output database summary
    print("\nDatabase created successfully with the following structure:")
    print(f"- {len(teachers)} teachers")
    print(f"- {len(courses)} courses")
    print(f"- {len(students)} students")
    print(f"- {grade_id-1} grade records")
    
    # Show example data
    print("\nSample student performance data:")
    sample_data = cursor.execute("SELECT * FROM student_performance LIMIT 5").fetchall()
    for row in sample_data:
        print(row)
    
    connection.close()
    print("\nDatabase setup completed!")

if __name__ == "__main__":
    create_student_database()