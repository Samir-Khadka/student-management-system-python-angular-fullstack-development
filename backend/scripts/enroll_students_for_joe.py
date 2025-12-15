"""
Enroll students in teacher joe's courses so they can see students in their dashboard.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def enroll_students_in_joe_courses():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    db = client.get_database('student_management')
    
    courses_collection = db.courses
    students_collection = db.students
    enrollments_collection = db.enrollments
    
    # Find joe's courses
    joe_courses = list(courses_collection.find({'teacher_id': 'joe'}))
    
    if len(joe_courses) == 0:
        print("⚠️  Teacher 'joe' has no assigned courses!")
        client.close()
        return
    
    print(f"Teacher 'joe' teaches {len(joe_courses)} course(s):")
    for course in joe_courses:
        print(f"  - {course['course_id']}: {course['name']}")
    
    # Get some students (limit to 10-15 per course)
    all_students = list(students_collection.find({}).limit(30))
    
    if len(all_students) == 0:
        print("\n⚠️  No students found in database!")
        client.close()
        return
    
    print(f"\nFound {len(all_students)} students in database")
    
    # Enroll students in joe's courses
    enrolled_count = 0
    
    for course in joe_courses:
        print(f"\nEnrolling students in {course['course_id']}...")
        
        # Check existing enrollments
        existing_count = enrollments_collection.count_documents({'course_id': course['course_id']})
        print(f"  Current enrollments: {existing_count}")
        
        # Enroll 10-15 students per course
        students_to_enroll = all_students[:15]
        
        for student in students_to_enroll:
            # Check if already enrolled
            existing = enrollments_collection.find_one({
                'student_id': student['student_id'],
                'course_id': course['course_id']
            })
            
            if existing:
                continue
            
            # Check student's total enrollments (max 5)
            student_enrollments = enrollments_collection.count_documents({
                'student_id': student['student_id']
            })
            
            if student_enrollments >= 5:
                continue
            
            # Enroll student
            enrollment_doc = {
                'student_id': student['student_id'],
                'course_id': course['course_id'],
                'course_name': course['name'],
                'teacher_id': 'joe',
                'marks': None,
                'enrolled_at': datetime.utcnow()
            }
            
            enrollments_collection.insert_one(enrollment_doc)
            enrolled_count += 1
        
        # Show final count
        final_count = enrollments_collection.count_documents({'course_id': course['course_id']})
        print(f"  ✅ Total enrollments now: {final_count}")
    
    print(f"\n✅ Enrolled {enrolled_count} new student-course combinations")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY - Teacher Joe's Classes:")
    print(f"{'='*60}")
    for course in joe_courses:
        count = enrollments_collection.count_documents({'course_id': course['course_id']})
        print(f"{course['course_id']} - {course['name']}: {count} students")
    print(f"{'='*60}\n")
    
    client.close()

if __name__ == '__main__':
    enroll_students_in_joe_courses()
