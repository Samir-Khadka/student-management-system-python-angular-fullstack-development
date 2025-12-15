# Student Grades Troubleshooting Guide

## Issue
Students not seeing their grades in the "My Grades" section despite data existing in the database.

## What's Been Done

### ✅ Backend
1. **Endpoint exists**: `/api/students/{student_id}/grades` (lines 417-445 in `students.py`)
2. **Data exists**: Verified 100 students with enrollments and grades in database
3. **Code is correct**: Backend properly queries enrollments and returns grades

### ✅ Frontend  
1. **Component exists**: `StudentGradesComponent` at `/dashboard/grades`
2. **Route configured**: Route works at `/dashboard/grades`
 3. **API service method**: `getStudentGrades()` calls correct endpoint
4. **Added logging**: Console logs added to debug the issue

## Next Steps - DEBUGGING

### Step 1: Open Browser Console
1. Login as a student (e.g., `student_001` / `student1123`)
2. Navigate to "My Grades" section
3. Open browser console (F12 → Console tab)

### Step 2: Check Console Logs

You should see:
```
User from auth service: {user object}
Student ID: S001
Fetching grades for student: S001
Grades response: {grades: [...]}
Loaded X grade records
```

### Step 3: Identify the Issue

#### ❌ **If you see: "No user or student_id found!"{**
- Problem: Auth service not returning student_id
- Fix needed: Check localStorage or auth service

#### ❌ **If you see: "Error loading grades" with 404**
- Problem: Backend endpoint not found
- Fix needed: Check backend is running and route is correct

#### ❌ **If you see: "Error loading grades" with 401/403**
- Problem: Authentication/authorization issue
- Fix needed: Check JWT token is valid

#### ✅ **If you see: "Loaded 0 grade records"**
- Problem: Student has no enrollments
- Fix needed: Student needs to enroll in courses

#### ✅ **If you see: "Loaded 3 grade records" (or more)**
- Problem: Data is loading but not displaying
- Fix needed: Check template rendering

## How to Fix Common Issues

### Fix 1: Student ID Not in Auth Response

If `student_id` is null, check the login response in Network tab:
1. Login as student
2. Check Network → login request → Response
3. Should include: `"student_id": "S001"`

If missing, backend login needs to return it (it should already - line 293 in auth.py)

### Fix 2: Navigate to Grades Page

Make sure you're clicking on the correct menu item to navigate to `/dashboard/grades`. The route should be:
- Path: `/dashboard/grades`
- Component: `StudentGradesComponent`

### Fix 3: Check Data in Database

Run this to verify data exists:
```bash
cd backend
python scripts\test_student_grades.py
```

Should show enrollments for student_001.

## Expected Behavior

When working correctly:
1. Student logs in →  `student_id` is in user object
2. Navigate to "My Grades" → Component loads
3. `loadGrades()` called → Fetches from API
4. API returns grades → Displayed in table
5. Each row shows: Course Name, Teacher, Marks, Status

## Sample Data

Student `student_001` (S001) should have 2-5 courses enrolled with marks like:
- Course: "Mathematics: Algebra I" - Teacher: "John Doe" - Marks: 65 - Status: "Passed"
- Course: "Physics: Mechanics" - Teacher: "Jane Smith" - Marks: null - Status: "Pending"

## Files Modified

1. `backend/scripts/seed_large_dataset.py` - Fixed password hashing
2. `backend/scripts/test_student_grades.py` - Test script for verification
3. `frontend/src/app/students/student-grades.component.ts` - Added console logging

## Test Credentials

Try these students:
- **student_001** / student1123
- **student_050** / student50123
- **student_100** / student100123

All should see their individual grades (2-5 courses each).

---

## Quick Diagnosis Commands

### Check if student has enrollments:
```bash
cd backend
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); db = MongoClient(os.getenv('MONGO_URI'))[os.getenv('MONGO_URI').split('/')[-1].split('?')[0]]; print(f'Enrollments for S001: {db.enrollments.count_documents({\"student_id\": \"S001\"})}')"
```

### Check if backend endpoint works:
```bash
# After logging in and getting token, test API directly:
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5001/api/students/S001/grades
```

---

**Next Action**: Open browser console, login as student, go to "My Grades", and share the console output!
