
import os
import sys
from pymongo import MongoClient
from datetime import datetime
import random

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import get_config

def seed_courses():
    # Setup connection
    config = get_config('development')
    client = MongoClient(config.MONGO_URI)
    db = client.get_database()
    
    print(f"Connected to database: {db.name}")
    
    # 1. Get existing teachers
    teachers = list(db.teachers.find({}))
    if not teachers:
        print("No teachers found! Please create teachers first.")
        return
        
    print(f"Found {len(teachers)} teachers.")
    
    # 2. Define courses to create
    courses_data = [
        {"id": "MATH101", "name": "Calculus I", "subject": "Mathematics"},
        {"id": "PHY101", "name": "Physics I", "subject": "Physics"},
        {"id": "ENG101", "name": "English Literature", "subject": "English"},
        {"id": "CS101", "name": "Intro to Programming", "subject": "Computer Science"},
        {"id": "BIO101", "name": "Biology I", "subject": "Biology"},
        {"id": "CHEM101", "name": "Chemistry I", "subject": "Chemistry"},
        {"id": "HIST101", "name": "World History", "subject": "History"},
        {"id": "ART101", "name": "Art Appreciation", "subject": "Art"}
    ]
    
    created_count = 0
    
    for course_def in courses_data:
        # Check if course exists
        if db.courses.find_one({'course_id': course_def['id']}):
            print(f"Course {course_def['id']} already exists. Skipping.")
            continue
            
        # Find a matching teacher (by subject) or random
        matching_teachers = [t for t in teachers if course_def['subject'] in t.get('subject', '')]
        teacher = matching_teachers[0] if matching_teachers else random.choice(teachers)
        
        course_doc = {
            'course_id': course_def['id'],
            'name': course_def['name'],
            'teacher_id': teacher['teacher_id'],
            'teacher_name': teacher['name'],
            'description': f"Introductory course for {course_def['subject']}.",
            'created_at': datetime.utcnow()
        }
        
        db.courses.insert_one(course_doc)
        print(f"Created course: {course_def['name']} (Teacher: {teacher['name']})")
        created_count += 1
        
    print(f"Seeding completed. Created {created_count} new courses.")

if __name__ == '__main__':
    seed_courses()
