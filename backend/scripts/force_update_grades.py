
import os
import sys
import random
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/student_management')
client = MongoClient(MONGO_URI)
db = client.get_database()

def force_update_grades():
    print("Starting Force Grade Update...")
    
    # 1. Get all enrollments
    enrollments = list(db.enrollments.find({}))
    print(f"Found {len(enrollments)} total enrollments.")
    
    updated_count = 0
    
    for enr in enrollments:
        # Check if marks are missing or we just want to re-verify updates
        # User said "no students marks should be empty"
        
        current_marks = enr.get('marks')
        
        # If marks are missing OR we want to verify the update mechanism works by refreshing them
        # Let's fill missing ones, and for testing, maybe update a few others?
        # User said "for now upload marks to all student"
        
        if current_marks is None or current_marks == "":
            new_marks = random.randint(50, 95)
            
            result = db.enrollments.update_one(
                {'_id': enr['_id']},
                {'$set': {
                    'marks': new_marks,
                    'graded_at': datetime.utcnow()
                }}
            )
            if result.modified_count > 0:
                updated_count += 1
                print(f"Updated Student {enr['student_id']} in {enr['course_id']} -> {new_marks}")
        else:
            # Should we update existing? User said "updating section ... is not updating"
            # Maybe they tried to change a mark and it failed.
            # Let's leave existing ones unless explicitly empty, to preserve data.
            # BUT, let's print one to show it exists.
            pass

    print(f"Filled grades for {updated_count} students who had empty marks.")
    
    # Verify Sync with Students Collection?
    # NOTE: The system seems to store grades in 'enrollments', but 'students' collection has 'final_grade'.
    # The 'final_grade' in students collection seems to be an aggregate or a single illustrative grade.
    # If the dashboard reads from 'students.final_grade' but we are updating 'enrollments', that's a mismatch!
    
    # Let's check if there is a sync issue.
    # The 'Student' model has 'final_grade'.
    # The 'Enrollment' has 'marks'.
    
    # If the teacher dashboard shows "My Students" list, where does it get the grade from?
    # It calls `get_course_students` in `courses.py`, which reads from ENROLLMENTS.
    # So that path is correct for the Course Gradebook.
    
    print("Grade population complete.")

if __name__ == "__main__":
    force_update_grades()
