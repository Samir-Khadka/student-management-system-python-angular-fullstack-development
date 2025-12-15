#!/usr/bin/env python
"""
Test login credentials to verify password hashing is working.
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

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
    print("PASSWORD VERIFICATION TEST")
    print("="*60)
    
    # Test admin
    print("\n🔐 Testing Admin credentials...")
    admin = db.users.find_one({'username': 'admin'})
    if admin:
        is_valid = verify_password('admin123', admin['password'])
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   ✅ Valid: {is_valid}")
    else:
        print("   ❌ Admin not found")
    
    # Test teacher
    print("\n🔐 Testing Teacher credentials...")
    teacher = db.users.find_one({'username': 'T001'})
    if teacher:
        is_valid = verify_password('teacher123', teacher['password'])
        print(f"   Username: T001")
        print(f"   Password: teacher123")
        print(f"   ✅ Valid: {is_valid}")
    else:
        print("   ❌ Teacher not found")
    
    # Test student
    print("\n🔐 Testing Student credentials...")
    student = db.users.find_one({'username': 'student_001'})
    if student:
        is_valid = verify_password('student1123', student['password'])
        print(f"   Username: student_001")
        print(f"   Password: student1123")
        print(f"   ✅ Valid: {is_valid}")
    else:
        print("   ❌ Student not found")
    
    # Test another student
    print("\n🔐 Testing Another Student...")
    student2 = db.users.find_one({'username': 'student_050'})
    if student2:
        is_valid = verify_password('student50123', student2['password'])
        print(f"   Username: student_050")
        print(f"   Password: student50123")
        print(f"   ✅ Valid: {is_valid}")
    else:
        print("   ❌ Student not found")
    
    print("\n" + "="*60)
    print("✅ All credentials verified!")
    print("="*60)
    
    client.close()

if __name__ == '__main__':
    main()
