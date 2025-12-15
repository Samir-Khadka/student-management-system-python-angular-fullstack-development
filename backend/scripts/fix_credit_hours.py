"""
Script to set credit hours to 50 for all courses/subjects.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def fix_credit_hours():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    db = client.get_database('student_management')
    
    courses_collection = db.courses
    
    # Get all courses
    all_courses = list(courses_collection.find({}))
    print(f"Found {len(all_courses)} courses")
    
    # Check current credit hours
    print("\nCurrent credit hours:")
    for course in all_courses[:10]:  # Show first 10
        credit_hrs = course.get('credit_hours', 'NOT SET')
        print(f"  {course.get('name', 'Unknown')}: {credit_hrs}")
    
    if len(all_courses) > 10:
        print(f"  ... and {len(all_courses) - 10} more courses")
    
    # Update all courses to have credit_hours = 50
    print("\nUpdating all courses to credit_hours = 50...")
    result = courses_collection.update_many(
        {},  # All courses
        {'$set': {'credit_hours': 50}}
    )
    
    print(f"✅ Updated {result.modified_count} courses")
    
    # Verify
    print("\nVerifying credit hours after update:")
    all_courses_after = list(courses_collection.find({}))
    for course in all_courses_after[:10]:
        credit_hrs = course.get('credit_hours', 'NOT SET')
        print(f"  {course.get('name', 'Unknown')}: {credit_hrs}")
    
    if len(all_courses_after) > 10:
        print(f"  ... and {len(all_courses_after) - 10} more courses")
    
    # Check if any course doesn't have 50 credit hours
    non_fifty = courses_collection.count_documents({'credit_hours': {'$ne': 50}})
    if non_fifty > 0:
        print(f"\n⚠️  WARNING: {non_fifty} courses still don't have 50 credit hours")
    else:
        print(f"\n✅ All {len(all_courses_after)} courses now have 50 credit hours!")
    
    client.close()

if __name__ == '__main__':
    fix_credit_hours()
