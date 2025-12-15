"""
Assign some courses to teacher 'joe' so they can see their courses.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def assign_courses_to_joe():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    db = client.get_database('student_management')
    
    users_collection = db.users
    teachers_collection = db.teachers
    courses_collection = db.courses
    
    # Check joe's teacher record
    teacher = teachers_collection.find_one({'teacher_id': 'joe'})
    if teacher:
        print(f"Teacher 'joe' found:")
        print(f"  Name: {teacher.get('name')}")
        print(f"  Subject: {teacher.get('subject')}")
    else:
        print("Teacher 'joe' not found in teachers collection!")
        return
    
    # Find courses related to Mathematics (joe's subject)
    print(f"\nLooking for {teacher.get('subject')} courses...")
    math_courses = list(courses_collection.find({
        '$or': [
            {'name': {'$regex': 'Math', '$options': 'i'}},
            {'name': {'$regex': 'Calculus', '$options': 'i'}},
            {'name': {'$regex': 'Algebra', '$options': 'i'}},
            {'name': {'$regex': 'Geometry', '$options': 'i'}}
        ]
    }))
    
    print(f"Found {len(math_courses)} mathematics courses:")
    for course in math_courses:
        print(f"  - {course.get('course_id')}: {course.get('name')}")
    
    if len(math_courses) == 0:
        print("\n⚠️  No mathematics courses found. Creating one...")
        new_course = {
            'course_id': 'MATH101',
            'name': 'Mathematics I',
            'description': 'Introductory course for Mathematics.',
            'teacher_id': 'joe',
            'teacher_name': 'Joe Teacher',
            'credit_hours': 50,
            'max_students': 40
        }
        courses_collection.insert_one(new_course)
        print(f"✅ Created course: MATH101 - Mathematics I")
        math_courses = [new_course]
    
    # Assign these courses to joe
    print(f"\nAssigning courses to teacher 'joe'...")
    for course in math_courses:
        result = courses_collection.update_one(
            {'course_id': course['course_id']},
            {'$set': {
                'teacher_id': 'joe',
                'teacher_name': 'Joe Teacher'
            }}
        )
        if result.modified_count > 0:
            print(f"  ✅ Assigned {course['course_id']} to joe")
        else:
            print(f"  ℹ️  {course['course_id']} already assigned to joe")
    
    # Verify
    print(f"\nVerifying joe's courses...")
    joe_courses = list(courses_collection.find({'teacher_id': 'joe'}))
    print(f"Joe teaches {len(joe_courses)} course(s):")
    for course in joe_courses:
        print(f"  - {course.get('course_id')}: {course.get('name')}")
    
    client.close()
    print(f"\n✅ Done! Teacher 'joe' can now see their courses in the dashboard.")

if __name__ == '__main__':
    assign_courses_to_joe()
