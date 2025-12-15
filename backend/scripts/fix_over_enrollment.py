"""
Script to fix over-enrollment issue - ensure all students have max 5 course enrollments.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def fix_enrollments():
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
    client = MongoClient(mongo_uri)
    db = client.get_database('student_management')
    
    enrollments_collection = db.enrollments
    
    # Get all unique student IDs
    student_ids = enrollments_collection.distinct('student_id')
    
    print(f"Found {len(student_ids)} students with enrollments")
    
    fixed_count = 0
    
    for student_id in student_ids:
        # Count enrollments for this student
        enrollments = list(enrollments_collection.find({'student_id': student_id}))
        enrollment_count = len(enrollments)
        
        if enrollment_count > 5:
            print(f"\nStudent {student_id} has {enrollment_count} enrollments (over limit!)")
            
            # Keep only the first 5, delete the rest
            enrollments_to_keep = enrollments[:5]
            enrollments_to_delete = enrollments[5:]
            
            keep_ids = [e['_id'] for e in enrollments_to_keep]
            delete_ids = [e['_id'] for e in enrollments_to_delete]
            
            # Delete excess enrollments
            result = enrollments_collection.delete_many({'_id': {'$in': delete_ids}})
            
            print(f"  Kept {len(keep_ids)} enrollments")
            print(f"  Deleted {result.deleted_count} excess enrollments")
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} students with over-enrollment")
    print("\nVerifying all students now have ≤5 enrollments...")
    
    # Verify
    for student_id in student_ids:
        count = enrollments_collection.count_documents({'student_id': student_id})
        if count > 5:
            print(f"  ❌ ERROR: {student_id} still has {count} enrollments!")
        elif count > 0:
            print(f"  ✅ {student_id}: {count} enrollments")
    
    client.close()
    print("\n✅ Enrollment cleanup complete!")

if __name__ == '__main__':
    fix_enrollments()
