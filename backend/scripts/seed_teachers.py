
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Add parent directory to path to find app
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

def seed_teachers():
    print("Seeding teachers...")
    
    # Default password hash for 'teacher123'
    hashed_password = generate_password_hash('teacher123')
    
    created_count = 0
    
    for subject in SUBJECTS:
        # Create 2 teachers per subject
        for i in range(1, 3):
            # Generate unique ID and data
            # Clean subject name for ID (e.g., Physical Education -> PhysicalEducation)
            clean_sub = subject.replace(" ", "")
            teacher_id = f"T_{clean_sub}_{i}"
            name = f"Teacher {subject} {i}"
            email = f"teacher.{clean_sub.lower()}{i}@example.com"
            
            # Check if exists
            if db.teachers.find_one({'teacher_id': teacher_id}):
                print(f"Skipping {teacher_id} (already exists)")
                continue
                
            # 1. Create Teacher Document
            teacher_doc = {
                'teacher_id': teacher_id,
                'name': name,
                'email': email,
                'subject': subject,
                'phone': '123-456-7890',
                'qualification': 'M.Ed / PhD',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            db.teachers.insert_one(teacher_doc)
            
            # 2. Create User Document
            # Check if user email exists
            if db.users.find_one({'email': email}):
                 print(f"Skipping User for {email} (already exists)")
            else:
                user_doc = {
                    'username': teacher_id,
                    'email': email,
                    'password': hashed_password,
                    'role': 'teacher',
                    'full_name': name,
                    'teacher_id': teacher_id,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'is_active': True,
                    'is_approved': True # Auto-approve seeded teachers
                }
                db.users.insert_one(user_doc)
                
            created_count += 1
            print(f"Created {name} ({email})")

    print(f"Successfully created {created_count} new teachers.")

if __name__ == "__main__":
    seed_teachers()
