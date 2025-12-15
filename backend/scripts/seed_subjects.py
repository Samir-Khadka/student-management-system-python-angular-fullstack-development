
import os
import sys
import random
from pymongo import MongoClient
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

def seed_subjects():
    print("Seeding subjects for students...")
    students = list(db.students.find({}))
    
    updated_count = 0
    for student in students:
        # Choose 5 unique random subjects
        student_subjects = random.sample(SUBJECTS, 5)
        
        db.students.update_one(
            {'_id': student['_id']},
            {'$set': {'enrolled_subjects': student_subjects}}
        )
        updated_count += 1
        print(f"Updated {student.get('name', 'Unknown')} with: {student_subjects}")

    print(f"Successfully updated {updated_count} students.")

if __name__ == "__main__":
    seed_subjects()
