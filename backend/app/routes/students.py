"""
Student CRUD routes.
Handles all student-related operations.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import mongo
from app.models.student_model import (
    validate_student_data,
    serialize_student,
    predict_student_performance
)
from app.utils.decorators import handle_exceptions
from marshmallow import ValidationError
from bson.objectid import ObjectId
from datetime import datetime

students_bp = Blueprint('students', __name__)


@students_bp.route('/', methods=['POST'])
@jwt_required()
@handle_exceptions
def create_student():
    """
    Create a new student.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - student_id
            - name
            - age
            - gender
            - study_time
            - absences
            - parental_support
            - internet_access
            - final_grade
          properties:
            student_id:
              type: string
              example: "S001"
            name:
              type: string
              example: "John Doe"
            age:
              type: integer
              example: 16
            gender:
              type: string
              enum: [Male, Female, Other]
            study_time:
              type: integer
              example: 10
            absences:
              type: integer
              example: 3
            parental_support:
              type: string
              enum: [low, medium, high]
            internet_access:
              type: boolean
            final_grade:
              type: integer
              minimum: 0
              maximum: 100
    responses:
      201:
        description: Student created successfully
      400:
        description: Validation error
      409:
        description: Student ID already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        validated_data = validate_student_data(data)
        
        existing = mongo.db.students.find_one({'student_id': validated_data['student_id']})
        if existing:
            return jsonify({
                'error': 'Conflict',
                'message': f"Student with ID {validated_data['student_id']} already exists"
            }), 409
        
        validated_data['created_at'] = datetime.utcnow()
        validated_data['updated_at'] = datetime.utcnow()
        
        result = mongo.db.students.insert_one(validated_data)
        
        student = mongo.db.students.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Student created successfully',
            'student': serialize_student(student)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': str(e.messages)
        }), 400


@students_bp.route('/', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_all_students():
    """
    Retrieve all students with optional filtering.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: query
        name: gender
        type: string
        description: Filter by gender
      - in: query
        name: min_grade
        type: integer
        description: Minimum final grade
      - in: query
        name: max_grade
        type: integer
        description: Maximum final grade
      - in: query
        name: limit
        type: integer
        description: Number of results to return
        default: 100
      - in: query
        name: skip
        type: integer
        description: Number of results to skip
        default: 0
    responses:
      200:
        description: List of students
    """
    query = {}
    
    if request.args.get('gender'):
        query['gender'] = request.args.get('gender')
    
    if request.args.get('min_grade'):
        query['final_grade'] = {'$gte': int(request.args.get('min_grade'))}
    
    if request.args.get('max_grade'):
        if 'final_grade' in query:
            query['final_grade']['$lte'] = int(request.args.get('max_grade'))
        else:
            query['final_grade'] = {'$lte': int(request.args.get('max_grade'))}
    
    limit = int(request.args.get('limit', 100))
    skip = int(request.args.get('skip', 0))

    # TEACHER FILTER LOGIC
    current_user_id = get_jwt_identity()
    # Check if user is a teacher (we need to look up their role, or trust the frontend/token claim)
    # Better to look up the user or trust claims if added. Let's look up to be safe or use role if in token.
    claims = get_jwt()
    if claims.get('role') == 'teacher':
        # Find teacher profile
        # Teacher ID is usually the username/identity in this system based on auth.py lines
        teacher = mongo.db.teachers.find_one({'teacher_id': claims.get('sub')}) # sub is usually identity (username)
        # However, identity might be ObjectId depending on how login is implemented. 
        # Checking auth.py: identity=str(user['_id']) in login.
        # But Teacher creation uses teacher_id as username.
        # Let's find the user first to get their username/teacher_id string if needed, or query teachers by user_id linkage if it exists.
        
        # Actually, in teachers.py create_teacher: user['username'] = data['teacher_id'].
        # And auth.py login uses identity=str(user['_id']).
        # So we need to find the User to get the teacher_id (which is the username).
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if user and user.get('role') == 'teacher':
             teacher_profile = mongo.db.teachers.find_one({'teacher_id': user['username']})
             if teacher_profile and 'subject' in teacher_profile:
                 teaching_subject = teacher_profile['subject']
                 # Filter students who have this subject in enrolled_subjects
                 query['enrolled_subjects'] = teaching_subject
    
    students_cursor = mongo.db.students.find(query).skip(skip).limit(limit)
    students_list = list(students_cursor)
    
    # Calculate final_grade for each student based on their enrollment marks
    students = []
    for student in students_list:
        enrollments = list(mongo.db.enrollments.find({'student_id': student['student_id']}))
        graded_enrollments = [e for e in enrollments if e.get('marks') is not None]
        
        if graded_enrollments:
            total_marks = sum(e['marks'] for e in graded_enrollments)
            calculated_final_grade = round(total_marks / len(graded_enrollments), 2)
        else:
            calculated_final_grade = 0
        
        student_data = serialize_student(student)
        student_data['final_grade'] = calculated_final_grade
        student_data['total_courses'] = len(enrollments)
        student_data['graded_courses'] = len(graded_enrollments)
        students.append(student_data)
    
    total_count = mongo.db.students.count_documents(query)
    
    return jsonify({
        'students': students,
        'total': total_count,
        'count': len(students),
        'skip': skip,
        'limit': limit,
        'filter_subject': query.get('enrolled_subjects') # Return debug info
    }), 200


@students_bp.route('/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student(student_id):
    """
    Retrieve a single student by student_id.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
        description: Student ID (e.g., S001)
    responses:
      200:
        description: Student details
      404:
        description: Student not found
    """
    student = mongo.db.students.find_one({'student_id': student_id})
    
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    # Calculate final_grade as average of all course marks
    enrollments = list(mongo.db.enrollments.find({'student_id': student_id}))
    
    # Filter enrollments that have marks (not None/null)
    graded_enrollments = [e for e in enrollments if e.get('marks') is not None]
    
    if graded_enrollments:
        # Calculate average
        total_marks = sum(e['marks'] for e in graded_enrollments)
        calculated_final_grade = round(total_marks / len(graded_enrollments), 2)
    else:
        # No grades yet, use 0 or keep original
        calculated_final_grade = 0
    
    # Serialize student and override final_grade with calculated value
    student_data = serialize_student(student)
    student_data['final_grade'] = calculated_final_grade
    student_data['total_courses'] = len(enrollments)
    student_data['graded_courses'] = len(graded_enrollments)
    
    return jsonify({
        'student': student_data
    }), 200


@students_bp.route('/<student_id>', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_student(student_id):
    """
    Update a student's information.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            age:
              type: integer
            gender:
              type: string
            study_time:
              type: integer
            absences:
              type: integer
            parental_support:
              type: string
            internet_access:
              type: boolean
            final_grade:
              type: integer
    responses:
      200:
        description: Student updated successfully
      404:
        description: Student not found
      400:
        description: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    existing = mongo.db.students.find_one({'student_id': student_id})
    if not existing:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    try:
        validated_data = validate_student_data(data, partial=True)
        
        if 'student_id' in validated_data:
            del validated_data['student_id']
        
        validated_data['updated_at'] = datetime.utcnow()
        
        mongo.db.students.update_one(
            {'student_id': student_id},
            {'$set': validated_data}
        )
        
        # Sync name change to users collection
        if 'name' in validated_data:
            mongo.db.users.update_one(
                {'student_id': student_id},
                {'$set': {'full_name': validated_data['name']}}
            )
        
        student = mongo.db.students.find_one({'student_id': student_id})
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': serialize_student(student)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': str(e.messages)
        }), 400


@students_bp.route('/<student_id>', methods=['DELETE'])
@jwt_required()
@handle_exceptions
def delete_student(student_id):
    """
    Delete a student.
    ---
    tags:
      - Students
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
    responses:
      200:
        description: Student deleted successfully
      404:
        description: Student not found
    """
    existing = mongo.db.students.find_one({'student_id': student_id})
    if not existing:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    # Delete from students collection
    mongo.db.students.delete_one({'student_id': student_id})
    
    # Delete from users collection (associated account)
    mongo.db.users.delete_one({'student_id': student_id})
    
    return jsonify({
        'message': f'Student {student_id} and associated account deleted successfully'
    }), 200


@students_bp.route('/predict/<student_id>', methods=['GET'])
@jwt_required()
@handle_exceptions
def predict_performance(student_id):
    """
    Predict student pass/fail performance.
    ---
    tags:
      - Students
      - Predictions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        required: true
        type: string
    responses:
      200:
        description: Prediction result
      404:
        description: Student not found
    """
    student = mongo.db.students.find_one({'student_id': student_id})
    
    if not student:
        return jsonify({
            'error': 'Not Found',
            'message': f'Student with ID {student_id} not found'
        }), 404
    
    prediction = predict_student_performance(student)
    
    return jsonify({
        'prediction': prediction
    }), 200

@students_bp.route('/<student_id>/grades', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_student_grades(student_id):
    """
    Get grades/enrollments for a student.
    """
    # Check if student exists
    if not mongo.db.students.find_one({'student_id': student_id}):
        return jsonify({'error': 'Student not found'}), 404

    # Get enrollments
    enrollments = list(mongo.db.enrollments.find({'student_id': student_id}))
    
    grades = []
    for enrollment in enrollments:
        # Get course details for teacher name
        course = mongo.db.courses.find_one({'course_id': enrollment['course_id']})
        
        grades.append({
            'course_id': enrollment['course_id'],
            'course_name': enrollment.get('course_name', course.get('name') if course else 'Unknown'),
            'teacher_id': enrollment.get('teacher_id'),
            'teacher_name': course.get('teacher_name') if course else 'Unknown',
            'marks': enrollment.get('marks'),
            'enrolled_at': enrollment.get('enrolled_at')
        })
        
    return jsonify({'grades': grades}), 200
