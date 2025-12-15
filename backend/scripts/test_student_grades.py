#!/usr/bin/env python
"""
Test student grades functionality.
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

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
    return client, db

def main():
    client, db = get_mongo_connection()
    
    print("="*60)
    print("TESTING STUDENT GRADES")
    print("="*60)
    
    # Test student_001
    user = db.users.find_one({'username': 'student_001'})
    if not user:
        print("❌ Student user not found!")
        return
    
    print(f"\n📝 Student User:")
    print(f"   Username: {user.get('username')}")
    print(f"   Student ID: {user.get('student_id')}")
    print(f"   Role: {user.get('role')}")
    
    student_id = user.get('student_id')
    
    # Check enrollments
    enrollments = list(db.enrollments.find({'student_id': student_id}))
    print(f"\n📚 Enrollments for {student_id}: {len(enrollments)}")
    
    if len(enrollments) == 0:
        print("   ❌ No enrollments found!")
    else:
        for i, enrollment in enumerate(enrollments, 1):
            course = db.courses.find_one({'course_id': enrollment['course_id']})
            print(f"\n   {i}. {enrollment.get('course_name')}")
            print(f"      Course ID: {enrollment.get('course_id')}")
            print(f"      Teacher: {course.get('teacher_name') if course else 'Unknown'}")
            print(f"      Marks: {enrollment.get('marks')}")
            print(f"      Status: {'Graded' if enrollment.get('marks') is not None else 'Pending'}")
    
    print("\n" + "="*60)
    
    client.close()

if __name__ == '__main__':
    main()
