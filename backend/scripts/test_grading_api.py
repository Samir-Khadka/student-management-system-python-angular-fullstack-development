
import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://localhost:5001/api"
TEACHER_EMAIL = "teacher.mathematics1@example.com" # From seeded data
TEACHER_PASSWORD = "teacher123"

def test_grading_flow():
    print("1. Logging in as Teacher...")
    # NOTE: Auth expects 'username', not 'email' based on error.
    # Seeded username pattern: T_Mathematics_1
    login_payload = {
        "username": "T_Mathematics_1", 
        "password": TEACHER_PASSWORD
    }
    
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return
        
        token = res.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
        
        print("\n2. Getting Teacher's Courses...")
        res = requests.get(f"{BASE_URL}/courses", headers=headers)
        if res.status_code != 200:
            print(f"Get Courses failed: {res.text}")
            return
            
        courses = res.json()['courses']
        if not courses:
            print("No courses found for teacher.")
            return
            
        target_course = courses[0] # Pick first course (e.g., Mathematics)
        print(f"Selected Course: {target_course['name']} ({target_course['course_id']})")
        
        print("\n3. Getting Enrolled Students...")
        res = requests.get(f"{BASE_URL}/courses/{target_course['course_id']}/students", headers=headers)
        if res.status_code != 200:
            print(f"Get Students failed: {res.text}")
            return
            
        students = res.json()['students']
        if not students:
            print("No students enrolled in this course.")
            return
            
        target_student = students[0]
        print(f"Selected Student: {target_student['student_name']} ({target_student['student_id']})")
        print(f"Current Marks: {target_student['marks']}")
        
        print("\n4. Updating Grade...")
        new_marks = 88
        grade_payload = {
            "course_id": target_course['course_id'],
            "student_id": target_student['student_id'],
            "marks": new_marks
        }
        
        res = requests.post(f"{BASE_URL}/courses/grade", json=grade_payload, headers=headers)
        print(f"Update Result: {res.status_code} - {res.text}")
        
        if res.status_code != 200:
            print("Update Failed!")
            return
            
        print("\n5. Verifying Update...")
        res = requests.get(f"{BASE_URL}/courses/{target_course['course_id']}/students", headers=headers)
        updated_students = res.json()['students']
        
        # Find our student
        verified_student = next((s for s in updated_students if s['student_id'] == target_student['student_id']), None)
        
        if verified_student and verified_student['marks'] == new_marks:
            print(f"SUCCESS: Grade updated to {verified_student['marks']}!")
        else:
            print(f"FAILURE: Grade is {verified_student['marks'] if verified_student else 'Not Found'}, expected {new_marks}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_grading_flow()
