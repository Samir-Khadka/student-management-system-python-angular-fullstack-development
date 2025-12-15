"""
Course and Grading routes.
Handles course creation, enrollment, and grading.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.utils.decorators import handle_exceptions
from datetime import datetime
from bson.objectid import ObjectId

courses_bp = Blueprint('courses', __name__)

# --- Course Management (Admin) ---

@courses_bp.route('/', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_course():
    """
    Create a new course.
    Admin only.
    """
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403

    data = request.get_json()
    
    required = ['course_id', 'name', 'teacher_id']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check if course exists
    if mongo.db.courses.find_one({'course_id': data['course_id']}):
        return jsonify({'error': 'Course ID already exists'}), 409
        
    # Verify teacher exists
    teacher = mongo.db.teachers.find_one({'teacher_id': data['teacher_id']})
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
        
    course_doc = {
        'course_id': data['course_id'],
        'name': data['name'],
        'teacher_id': data['teacher_id'],
        'teacher_name': teacher['name'],
        'credits': data.get('credits', 50), # Default to 50
        'description': data.get('description', ''),
        'created_at': datetime.utcnow()
    }
    
    mongo.db.courses.insert_one(course_doc)
    
    return jsonify({'message': 'Course created successfully', 'course': {k:v for k,v in course_doc.items() if k != '_id'}}), 201

@courses_bp.route('/<course_id>', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_course(course_id):
    """
    Update course details.
    Admin only.
    """
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403

    data = request.get_json()
    
    # 1. Update basic fields
    update_data = {
        'name': data.get('name'),
        'description': data.get('description'),
        'credits': data.get('credits'),
        'updated_at': datetime.utcnow()
    }
    
    # 2. Update teacher if provided
    if 'teacher_id' in data:
        teacher = mongo.db.teachers.find_one({'teacher_id': data['teacher_id']})
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        update_data['teacher_id'] = data['teacher_id']
        update_data['teacher_name'] = teacher['name']
        
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    result = mongo.db.courses.update_one(
        {'course_id': course_id},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Course not found'}), 404
        
    return jsonify({'message': 'Course updated successfully'}), 200

@courses_bp.route('/public', methods=['GET'])
@handle_exceptions
def get_public_courses():
    """
    Get all courses (Public access for registration).
    """
    courses = list(mongo.db.courses.find({}, {'_id': 0}))
    return jsonify({'courses': courses, 'count': len(courses)}), 200

@courses_bp.route('/', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_all_courses():
    """
    Get all courses.
    Accessible to all roles (Admin for management, Students for browsing).
    """
    query = {}
    from flask_jwt_extended import get_jwt
    
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') == 'teacher':
        # Find the user to get the teacher_id (username)
        from bson.objectid import ObjectId
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        
        if user and user.get('role') == 'teacher':
             # Courses are linked by teacher_id
             # In create_teacher, username = teacher_id.
             query['teacher_id'] = user['username']

    courses = list(mongo.db.courses.find(query, {'_id': 0}))
    return jsonify({'courses': courses, 'count': len(courses)}), 200

# --- Enrollment ---

@courses_bp.route('/enroll', methods=['POST'])
@jwt_required()
@handle_exceptions
def enroll_student():
    """
    Enroll a student in a course.
    - Admin can enroll any student.
    - Student can enroll themselves.
    - Enforces MAX 5 courses limit.
    """
    from flask_jwt_extended import get_jwt
    
    data = request.get_json()
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    # Determine student_id
    target_student_id = None
    
    if role == 'admin':
        target_student_id = data.get('student_id')
        if not target_student_id:
             return jsonify({'error': 'student_id is required for admin'}), 400
    elif role == 'student':
        # For students, we need to find their student_id.
        # It might be in the claims if we put it there, or we look it up.
        # auth_helper.py didn't put student_id in claims, only role.
        # So we must look up the user to get the student_id or rely on the fact 
        # that for students, we usually expect them to have a 'student_id' field in users collection?
        # Actually, let's look at auth.py login response. It returns user.student_id.
        # But here we only have the token.
        
        # We need to fetch the user to get the student_id
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user or 'student_id' not in user:
             return jsonify({'error': 'Student profile not found'}), 404
        target_student_id = user['student_id']
    else:
        return jsonify({'error': 'Unauthorized'}), 403

    if 'course_id' not in data:
        return jsonify({'error': 'course_id is required'}), 400
        
    # Verify exact IDs
    if not mongo.db.students.find_one({'student_id': target_student_id}):
        return jsonify({'error': 'Student not found'}), 404
        
    course = mongo.db.courses.find_one({'course_id': data['course_id']})
    if not course:
        return jsonify({'error': 'Course not found'}), 404
        
    # Check existing enrollment
    existing = mongo.db.enrollments.find_one({
        'student_id': target_student_id,
        'course_id': data['course_id']
    })
    
    if existing:
        return jsonify({'error': 'Student already enrolled in this course'}), 409

    # CHECK LIMIT: MAX 5 COURSES
    current_count = mongo.db.enrollments.count_documents({'student_id': target_student_id})
    if current_count >= 5:
        return jsonify({'error': 'Enrollment limit reached. Maximum 5 courses allowed.'}), 400
        
    enrollment_doc = {
        'student_id': target_student_id,
        'course_id': data['course_id'],
        'course_name': course['name'],
        'teacher_id': course['teacher_id'],
        'marks': None, # Not graded yet
        'enrolled_at': datetime.utcnow()
    }
    
    mongo.db.enrollments.insert_one(enrollment_doc)
    
    return jsonify({'message': 'Enrollment successful'}), 200

# --- Teacher Actions ---

@courses_bp.route('/teacher/<teacher_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_teacher_courses(teacher_id):
    """
    Get courses assigned to a specific teacher.
    """
    courses = list(mongo.db.courses.find({'teacher_id': teacher_id}, {'_id': 0}))
    return jsonify({'courses': courses}), 200

@courses_bp.route('/<course_id>/students', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_course_students(course_id):
    """
    Get all students enrolled in a specific course (with their marks).
    """
    # 1. Get enrollments for this course
    enrollments = list(mongo.db.enrollments.find({'course_id': course_id}, {'_id': 0}))
    
    # 2. Enhance with student names
    result = []
    for enrollment in enrollments:
        student = mongo.db.students.find_one({'student_id': enrollment['student_id']})
        student_name = student['name'] if student else 'Unknown'
        
        result.append({
            'student_id': enrollment['student_id'],
            'student_name': student_name,
            'marks': enrollment.get('marks', None)
        })
        
    return jsonify({'students': result, 'count': len(result)}), 200

@courses_bp.route('/grade', methods=['POST'])
@jwt_required()
@handle_exceptions
def grade_student():
    """
    Assign or update marks for a student in a course.
    Teacher only (in theory, but verified by ID if needed).
    """
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get('role') not in ['teacher', 'admin']:
        return jsonify({'error': 'Unauthorized', 'message': 'Teacher/Admin access required'}), 403

    data = request.get_json()
    
    required = ['course_id', 'student_id', 'marks']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
        
    result = mongo.db.enrollments.update_one(
        {'course_id': data['course_id'], 'student_id': data['student_id']},
        {
            '$set': {
                'marks': int(data['marks']),
                'graded_at': datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Enrollment not found'}), 404
        
    return jsonify({'message': 'Marks updated successfully'}), 200

# --- Student Actions ---

@courses_bp.route('/student/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student_grades(student_id):
    """
    Get all enrolled courses and marks for a student.
    """
@courses_bp.route('/<course_id>', methods=['DELETE'])
@jwt_required()
@handle_exceptions
def delete_course(course_id):
    """
    Delete a course.
    Admin only.
    """
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403
        
    course = mongo.db.courses.find_one({'course_id': course_id})
    if not course:
        return jsonify({'error': 'Course not found'}), 404
        
    mongo.db.courses.delete_one({'course_id': course_id})
    
    # Optional: Delete enrollments for this course?
    mongo.db.enrollments.delete_many({'course_id': course_id})
    
    return jsonify({'message': 'Course deleted successfully'}), 200
