#!/usr/bin/env python
"""
Large dataset seeding script.
Populates MongoDB with 100 students and appropriate related data.
Run this script: python seed_large_dataset.py
"""
import os
import sys
from datetime import datetime, timedelta
import random
from faker import Faker
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure to use the local environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(__file__))


def hash_password(password):
    """Hash a password using bcrypt (same as auth_helper.py)."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

fake = Faker()

def get_mongo_connection():
    """
    Create MongoDB connection.
    
    Returns:
        MongoDB client and database
    """
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    
    # Extract database name from URI or use default
    if '/' in mongo_uri.split('mongodb://')[-1]:
        db_name = mongo_uri.split('/')[-1].split('?')[0]
    else:
        db_name = 'student_management'
    
    db = client[db_name]
    print(f"Using database: {db_name}")
    return client, db


def clear_collections(db):
    """
    Clear existing collections to avoid duplicates.
    
    Args:
        db: MongoDB database instance
    """
    print("🧹 Clearing existing collections...")
    db.students.delete_many({})
    db.users.delete_many({})
    db.teachers.delete_many({})
    db.courses.delete_many({})
    db.enrollments.delete_many({})
    print("✓ Collections cleared")


def seed_teachers(db):
    """
    Seed teacher records.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        List of created teachers
    """
    print("\n👨‍🏫 Seeding teachers...")
    
    subjects = [
        'Mathematics', 'Physics', 'Chemistry', 'Biology', 
        'Computer Science', 'English Literature', 'History', 
        'Geography', 'Economics', 'Psychology',
        'Physical Education', 'Art', 'Music', 'Spanish', 'French'
    ]
    
    qualifications = [
        'Ph.D. in Education',
        'Master of Science',
        'Master of Arts',
        'Bachelor of Education',
        'Master in Computer Science'
    ]
    
    teachers = []
    teacher_users = []
    now = datetime.utcnow()
    
    for i, subject in enumerate(subjects, start=1):
        teacher_id = f'T{i:03d}'
        name = fake.name()
        email = f'teacher{i}@school.com'
        
        teacher = {
            'teacher_id': teacher_id,
            'name': name,
            'email': email,
            'subject': subject,
            'phone': fake.phone_number()[:15],
            'qualification': random.choice(qualifications),
            'created_at': now - timedelta(days=random.randint(180, 365)),
            'updated_at': now
        }
        
        teachers.append(teacher)
        
        # Create user account for teacher
        user = {
            'username': teacher_id,
            'email': email,
            'password': hash_password('teacher123'),
            'role': 'teacher',
            'full_name': name,
            'teacher_id': teacher_id,
            'created_at': teacher['created_at'],
            'updated_at': now,
            'is_active': True
        }
        
        teacher_users.append(user)
    
    # Insert teachers
    db.teachers.insert_many(teachers)
    print(f"✓ Created {len(teachers)} teachers")
    
    return teachers, teacher_users


def seed_courses(db, teachers):
    """
    Seed course records.
    
    Args:
        db: MongoDB database instance
        teachers: List of teachers
        
    Returns:
        List of created courses
    """
    print("\n📖 Seeding courses...")
    
    course_templates = {
        'Mathematics': ['Algebra I', 'Geometry', 'Calculus'],
        'Physics': ['Mechanics', 'Thermodynamics', 'Electromagnetism'],
        'Chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry'],
        'Biology': ['Cell Biology', 'Genetics', 'Ecology'],
        'Computer Science': ['Programming 101', 'Data Structures', 'Algorithms', 'Web Development'],
        'English Literature': ['British Literature', 'American Literature', 'Poetry'],
        'History': ['World History', 'American History', 'Ancient Civilizations'],
        'Geography': ['Physical Geography', 'Human Geography', 'Cartography'],
        'Economics': ['Microeconomics', 'Macroeconomics', 'International Trade'],
        'Psychology': ['Introduction to Psychology', 'Cognitive Psychology', 'Social Psychology'],
        'Physical Education': ['Sports Training', 'Health & Wellness'],
        'Art': ['Drawing & Painting', 'Sculpture'],
        'Music': ['Music Theory', 'Instrumental Music'],
        'Spanish': ['Spanish I', 'Spanish II'],
        'French': ['French I', 'French II']
    }
    
    courses = []
    now = datetime.utcnow()
    course_counter = 1
    
    for teacher in teachers:
        subject = teacher['subject']
        
        if subject in course_templates:
            course_names = course_templates[subject]
            
            for course_name in course_names:
                course_id = f'C{course_counter:03d}'
                
                course = {
                    'course_id': course_id,
                    'name': f'{subject}: {course_name}',
                    'teacher_id': teacher['teacher_id'],
                    'teacher_name': teacher['name'],
                    'credits': random.choice([50, 75, 100]),
                    'description': f'A comprehensive course in {course_name}',
                    'created_at': now - timedelta(days=random.randint(30, 180))
                }
                
                courses.append(course)
                course_counter += 1
    
    # Insert courses
    db.courses.insert_many(courses)
    print(f"✓ Created {len(courses)} courses")
    
    return courses


def seed_students(db):
    """
    Seed 100 student records with realistic dummy data.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        List of created students
    """
    print("\n📚 Seeding students...")
    
    genders = ['Male', 'Female', 'Other']
    parental_support_levels = ['low', 'medium', 'high']
    
    students = []
    student_users = []
    now = datetime.utcnow()
    
    for i in range(1, 101):  # 100 students
        student_id = f'S{i:03d}'
        
        # Generate realistic data
        age = random.randint(14, 22)
        gender = random.choice(genders)
        study_time = random.randint(0, 40)  # Hours per week
        absences = random.randint(0, 30)
        parental_support = random.choice(parental_support_levels)
        internet_access = random.choice([True, False])
        
        # Generate grade with some correlation to study time and parental support
        base_grade = study_time * 1.5
        if parental_support == 'high':
            base_grade += random.randint(10, 20)
        elif parental_support == 'medium':
            base_grade += random.randint(0, 10)
        
        base_grade -= absences * 0.5
        final_grade = max(0, min(100, int(base_grade + random.randint(-10, 10))))
        
        # Attendance log - simulate daily attendance for last 100 days
        attendance_log = []
        current_date = now - timedelta(days=100)
        for _ in range(100):
            attendance_log.append({
                'date': current_date.isoformat(),
                'present': random.choice([True, False]) if random.random() > 0.1 else True
            })
            current_date += timedelta(days=1)
        
        name = fake.name()
        email = f'student{i}@school.com'
        
        student = {
            'student_id': student_id,
            'name': name,
            'age': age,
            'gender': gender,
            'study_time': study_time,
            'absences': absences,
            'parental_support': parental_support,
            'internet_access': internet_access,
            'final_grade': final_grade,
            'attendance_log': attendance_log,
            'created_at': now - timedelta(days=random.randint(30, 180)),
            'updated_at': now - timedelta(days=random.randint(0, 10))
        }
        
        students.append(student)
        
        # Create user account for student
        user = {
            'username': f'student_{i:03d}',
            'email': email,
            'password': hash_password(f'student{i}123'),
            'role': 'student',
            'full_name': name,
            'student_id': student_id,
            'created_at': student['created_at'],
            'updated_at': now,
            'is_active': True
        }
        
        student_users.append(user)
    
    # Insert students
    db.students.insert_many(students)
    print(f"✓ Created {len(students)} students")
    
    return students, student_users


def seed_enrollments(db, students, courses):
    """
    Seed enrollment records - each student enrolled in 2-5 courses.
    
    Args:
        db: MongoDB database instance
        students: List of students
        courses: List of courses
        
    Returns:
        List of created enrollments
    """
    print("\n📝 Seeding enrollments...")
    
    enrollments = []
    now = datetime.utcnow()
    
    for student in students:
        # Each student gets 2-5 courses
        num_courses = random.randint(2, 5)
        selected_courses = random.sample(courses, num_courses)
        
        for course in selected_courses:
            # Generate marks (None for some, indicating not graded yet)
            marks = None
            if random.random() > 0.3:  # 70% of students have been graded
                marks = random.randint(40, 100)
            
            enrollment = {
                'student_id': student['student_id'],
                'course_id': course['course_id'],
                'course_name': course['name'],
                'teacher_id': course['teacher_id'],
                'marks': marks,
                'enrolled_at': now - timedelta(days=random.randint(30, 90))
            }
            
            if marks is not None:
                enrollment['graded_at'] = now - timedelta(days=random.randint(1, 30))
            
            enrollments.append(enrollment)
    
    # Insert enrollments
    db.enrollments.insert_many(enrollments)
    print(f"✓ Created {len(enrollments)} enrollments")
    
    return enrollments


def seed_admin_user(db):
    """
    Create admin user account.
    
    Args:
        db: MongoDB database instance
    """
    print("\n👤 Creating admin user...")
    
    admin = {
        'username': 'admin',
        'email': 'admin@school.com',
        'password': hash_password('admin123'),
        'role': 'admin',
        'full_name': 'System Administrator',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True
    }
    
    db.users.insert_one(admin)
    print("✓ Admin user created")


def print_summary(db):
    """
    Print summary of seeded data.
    
    Args:
        db: MongoDB database instance
    """
    print("\n" + "="*60)
    print("📊 DATABASE SEEDING SUMMARY")
    print("="*60)
    
    # User summary
    total_users = db.users.count_documents({})
    admin_count = db.users.count_documents({'role': 'admin'})
    teacher_count = db.users.count_documents({'role': 'teacher'})
    student_user_count = db.users.count_documents({'role': 'student'})
    
    print(f"\n👥 Users: {total_users}")
    print(f"   ├─ Admin: {admin_count}")
    print(f"   ├─ Teachers: {teacher_count}")
    print(f"   └─ Student accounts: {student_user_count}")
    
    # Teacher summary
    total_teachers = db.teachers.count_documents({})
    print(f"\n👨‍🏫 Teachers: {total_teachers}")
    
    # Course summary
    total_courses = db.courses.count_documents({})
    print(f"\n📖 Courses: {total_courses}")
    
    # Student summary
    total_students = db.students.count_documents({})
    male_students = db.students.count_documents({'gender': 'Male'})
    female_students = db.students.count_documents({'gender': 'Female'})
    other_students = db.students.count_documents({'gender': 'Other'})
    
    print(f"\n📚 Students: {total_students}")
    print(f"   ├─ Male: {male_students}")
    print(f"   ├─ Female: {female_students}")
    print(f"   └─ Other: {other_students}")
    
    # Enrollment summary
    total_enrollments = db.enrollments.count_documents({})
    graded_enrollments = db.enrollments.count_documents({'marks': {'$ne': None}})
    ungraded_enrollments = total_enrollments - graded_enrollments
    
    print(f"\n📝 Enrollments: {total_enrollments}")
    print(f"   ├─ Graded: {graded_enrollments}")
    print(f"   └─ Pending grading: {ungraded_enrollments}")
    
    # Grade statistics
    pipeline = [
        {'$match': {'marks': {'$ne': None}}},
        {
            '$group': {
                '_id': None,
                'avg_marks': {'$avg': '$marks'},
                'min_marks': {'$min': '$marks'},
                'max_marks': {'$max': '$marks'},
                'pass_count': {
                    '$sum': {'$cond': [{'$gte': ['$marks', 40]}, 1, 0]}
                },
                'fail_count': {
                    '$sum': {'$cond': [{'$lt': ['$marks', 40]}, 1, 0]}
                }
            }
        }
    ]
    
    stats = list(db.enrollments.aggregate(pipeline))
    if stats:
        s = stats[0]
        print(f"\n📈 Grade Statistics (Enrollments):")
        print(f"   ├─ Average: {s['avg_marks']:.2f}")
        print(f"   ├─ Range: {s['min_marks']} - {s['max_marks']}")
        print(f"   ├─ Pass count (marks ≥ 40): {s['pass_count']}")
        print(f"   └─ Fail count (marks < 40): {s['fail_count']}")
    
    print("\n" + "="*60)
    print("✅ Database seeding completed successfully!")
    print("="*60)
    
    print("\n🔐 Sample Login Credentials:")
    print("   Admin:")
    print("      Username: admin")
    print("      Password: admin123")
    print("\n   Teacher:")
    print("      Username: T001")
    print("      Password: teacher123")
    print("\n   Student:")
    print("      Username: student_001")
    print("      Password: student1123")
    print()


def main():
    """Main seeding function."""
    print("🌱 Starting Large Dataset Seeding (100 students)...\n")
    
    try:
        # Get MongoDB connection
        client, db = get_mongo_connection()
        print(f"✓ Connected to MongoDB")
        
        # Clear existing data
        clear_collections(db)
        
        # Seed data in order
        teachers, teacher_users = seed_teachers(db)
        courses = seed_courses(db, teachers)
        students, student_users = seed_students(db)
        enrollments = seed_enrollments(db, students, courses)
        
        # Create all users
        print("\n👥 Creating user accounts...")
        all_users = teacher_users + student_users
        db.users.insert_many(all_users)
        print(f"✓ Created {len(all_users)} user accounts")
        
        # Create admin
        seed_admin_user(db)
        
        # Print summary
        print_summary(db)
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
