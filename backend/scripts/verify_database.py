#!/usr/bin/env python
"""
Quick script to verify database counts.
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_mongo_connection():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    
    if '/' in mongo_uri.split('mongodb://')[-1]:
        db_name = mongo_uri.split('/')[-1].split('?')[0]
    else:
        db_name = 'student_management'
    
    db = client[db_name]
    print(f"Connected to database: {db_name}\n")
    return client, db

def main():
    client, db = get_mongo_connection()
    
    print("="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    print(f"\n📊 Collection Counts:")
    print(f"   Students: {db.students.count_documents({})}")
    print(f"   Teachers: {db.teachers.count_documents({})}")
    print(f"   Courses: {db.courses.count_documents({})}")
    print(f"   Enrollments: {db.enrollments.count_documents({})}")
    print(f"   Users: {db.users.count_documents({})}")
    print(f"     ├─ Admin: {db.users.count_documents({'role': 'admin'})}")
    print(f"     ├─ Teachers: {db.users.count_documents({'role': 'teacher'})}")
    print(f"     └─ Students: {db.users.count_documents({'role': 'student'})}")
    
    # Sample data from each collection
    print(f"\n📝 Sample Student:")
    student = db.students.find_one({})
    if student:
        print(f"   ID: {student.get('student_id')}")
        print(f"   Name: {student.get('name')}")
        print(f"   Age: {student.get('age')}")
        print(f"   Final Grade: {student.get('final_grade')}")
    
    print(f"\n📝 Sample Teacher:")
    teacher = db.teachers.find_one({})
    if teacher:
        print(f"   ID: {teacher.get('teacher_id')}")
        print(f"   Name: {teacher.get('name')}")
        print(f"   Subject: {teacher.get('subject')}")
    
    print(f"\n📝 Sample Course:")
    course = db.courses.find_one({})
    if course:
        print(f"   ID: {course.get('course_id')}")
        print(f"   Name: {course.get('name')}")
        print(f"   Teacher: {course.get('teacher_name')}")
        print(f"   Credits: {course.get('credits')}")
    
    print(f"\n📝 Sample Enrollment:")
    enrollment = db.enrollments.find_one({})
    if enrollment:
        print(f"   Student ID: {enrollment.get('student_id')}")
        print(f"   Course: {enrollment.get('course_name')}")
        print(f"   Marks: {enrollment.get('marks')}")
    
    print("\n" + "="*60)
    
    client.close()

if __name__ == '__main__':
    main()
