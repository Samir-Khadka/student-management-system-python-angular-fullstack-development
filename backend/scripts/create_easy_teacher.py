"""
Create a simple teacher login: joe / password123
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

def create_easy_teacher_login():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    db = client.get_database('student_management')
    
    users_collection = db.users
    teachers_collection = db.teachers
    
    username = 'joe'
    password = 'password123'
    
    # Hash password using bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # Check if user already exists
    existing_user = users_collection.find_one({'username': username})
    
    if existing_user:
        print(f"User '{username}' already exists. Updating password and ensuring approved...")
        # Update password and ensure approved
        users_collection.update_one(
            {'username': username},
            {'$set': {
                'password': hashed,
                'is_approved': True,
                'role': 'teacher'
            }}
        )
        print(f"✅ Updated user '{username}' with new password and approved status")
    else:
        print(f"Creating new teacher user '{username}'...")
        # Create user
        user_doc = {
            'username': username,
            'password': hashed,
            'email': 'joe@teacher.com',
            'role': 'teacher',
            'full_name': 'Joe Teacher',
            'is_approved': True,
            'is_active': True
        }
        users_collection.insert_one(user_doc)
        
        # Create teacher profile
        teacher_doc = {
            'teacher_id': username,
            'name': 'Joe Teacher',
            'email': 'joe@teacher.com',
            'subject': 'Mathematics',
            'phone': '',
            'qualification': 'MSc Mathematics'
        }
        teachers_collection.insert_one(teacher_doc)
        
        print(f"✅ Created teacher user '{username}'")
    
    print(f"\n{'='*50}")
    print(f"✅ TEACHER LOGIN READY!")
    print(f"{'='*50}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Role: Teacher")
    print(f"Status: Approved")
    print(f"{'='*50}\n")
    
    client.close()

if __name__ == '__main__':
    create_easy_teacher_login()
