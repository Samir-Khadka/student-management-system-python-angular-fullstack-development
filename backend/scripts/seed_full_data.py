
import os
import sys
import random
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
client = MongoClient(MONGO_URI)
db = client.get_database()

SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology", 
    "English", "History", "Geography", "Computer Science", 
    "Art", "Music", "Physical Education", "Economics"
]

def seed_data():
    print("Step 1: Ensuring Courses Exist...")
    courses_created = 0
    
    # 1. Create Courses if they don't exist
    # We will try to find a teacher for each subject to assign the course to.
    for subject in SUBJECTS:
        # Check if course exists
        course_id = f"C_{subject.replace(' ', '')}"
        existing_course = db.courses.find_one({'course_id': course_id})
        
        if not existing_course:
            # Find a teacher for this subject
            teacher = db.teachers.find_one({'subject': subject})
            if not teacher:
                print(f"Warning: No teacher found for {subject}, skipping course creation.")
                continue
                
            course_doc = {
                'course_id': course_id,
                'name': subject, # Course name = Subject name
                'teacher_id': teacher['teacher_id'],
                'teacher_name': teacher['name'],
                'credits': 50,
                'description': f"Advanced {subject} course",
                'created_at': datetime.utcnow()
            }
            db.courses.insert_one(course_doc)
            courses_created += 1
            print(f"Created Course: {subject} ({teacher['name']})")
    
    print(f"Courses Created: {courses_created}")

    print("\nStep 2: Enrolling Students & Assigning Grades...")
    students = list(db.students.find({}))
    enrollments_count = 0
    
    for student in students:
        # Check their enrolled_subjects
        subjects = student.get('enrolled_subjects', [])
        
        for subject in subjects:
            course_id = f"C_{subject.replace(' ', '')}"
            course = db.courses.find_one({'course_id': course_id})
            
            if not course:
                continue
                
            # Check/Create Enrollment
            existing_enrollment = db.enrollments.find_one({
                'student_id': student['student_id'],
                'course_id': course_id
            })
            
            if not existing_enrollment:
                # Random Grade 40-95
                rand_marks = random.randint(40, 95)
                
                enrollment_doc = {
                    'student_id': student['student_id'],
                    'course_id': course_id,
                    'course_name': course['name'],
                    'teacher_id': course['teacher_id'],
                    'marks': rand_marks,
                    'enrolled_at': datetime.utcnow(),
                    'graded_at': datetime.utcnow()
                }
                db.enrollments.insert_one(enrollment_doc)
                enrollments_count += 1
    
    print(f"Enrollments Created/Updated: {enrollments_count}")
    print("Data Seeding Complete.")

if __name__ == "__main__":
    seed_data()
