
import os
import sys
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
client = MongoClient(MONGO_URI)
db = client.get_database()

def hash_password(password):
    """Hash a password using bcrypt (matching auth_helper.py)."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def fix_passwords():
    print("Fixing teacher passwords...")
    
    # Target all users with role 'teacher'
    teachers = list(db.users.find({'role': 'teacher'}))
    print(f"Found {len(teachers)} teacher accounts.")
    
    hashed_password = hash_password('teacher123')
    
    updated_count = 0
    for teacher in teachers:
        db.users.update_one(
            {'_id': teacher['_id']},
            {'$set': {'password': hashed_password}}
        )
        updated_count += 1
        
    print(f"Updated passwords for {updated_count} teachers to 'teacher123' (bcrypt).")

if __name__ == "__main__":
    fix_passwords()
