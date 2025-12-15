"""
Authentication routes.
Handles user registration, login, logout, and JWT management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    get_jwt
)
from app import mongo
from app.utils.auth_helper import (
    hash_password,
    verify_password,
    generate_tokens,
    validate_user_data
)
from app.utils.decorators import handle_exceptions
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@handle_exceptions
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - email
            - role
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "password123"
            email:
              type: string
              example: "john@example.com"
            role:
              type: string
              enum: [student, teacher, admin]
              example: "student"
            student_id:
              type: string
              description: Required if role is student
              example: "S001"
            full_name:
              type: string
              example: "John Doe"
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Username already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    validated_data, error = validate_user_data(data)
    if error:
        return jsonify({'error': 'Validation Error', 'message': error}), 400
    
    existing_user = mongo.db.users.find_one({'username': validated_data['username']})
    if existing_user:
        return jsonify({
            'error': 'Conflict',
            'message': 'Username already exists'
        }), 409
    
    existing_email = mongo.db.users.find_one({'email': validated_data['email']})
    if existing_email:
        return jsonify({
            'error': 'Conflict',
            'message': 'Email already exists'
        }), 409
    
    # If role is student, ensure student_id is provided
    if validated_data['role'] == 'student' and 'student_id' not in data:
        return jsonify({
            'error': 'Validation Error',
            'message': 'student_id is required for student role'
        }), 400
    
    # If role is teacher, ensure subject is provided (frontend should send it)
    # Block admin registration
    if validated_data['role'] == 'admin':
         return jsonify({
            'error': 'Forbidden',
            'message': 'Admin registration is restricted'
        }), 403

    hashed_pwd = hash_password(validated_data['password'])
    
    # Default approval status
    is_approved = True
    if validated_data['role'] == 'teacher':
        is_approved = False  # Teachers need approval
    
    user_doc = {
        'username': validated_data['username'],
        'password': hashed_pwd,
        'email': validated_data['email'],
        'role': validated_data['role'],
        'full_name': data.get('full_name', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'is_active': True,
        'is_approved': is_approved, # New flag
        'cv_url': None # New field for CV
    }
    
    if 'student_id' in data:
        user_doc['student_id'] = data['student_id']
        
        # Check if student_id already exists in students collection
        if mongo.db.students.find_one({'student_id': data['student_id']}):
            return jsonify({
                'error': 'Conflict',
                'message': f"Student ID {data['student_id']} already exists"
            }), 409
    
    result = mongo.db.users.insert_one(user_doc)
    
    # If role is student, create entry in students collection
    if validated_data['role'] == 'student':
        student_doc = {
            'student_id': data['student_id'],
            'name': data.get('full_name', validated_data['username']),
            'age': 0,  # Default
            'gender': 'Other',  # Default
            'study_time': 0,
            'absences': 0,
            'parental_support': 'medium',
            'internet_access': False,
            'final_grade': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.students.insert_one(student_doc)

        # Handle course enrollments (if provided)
        courses_to_enroll = data.get('courses', [])
        if courses_to_enroll:
            if len(courses_to_enroll) > 5:
                # This should ideally be caught before user creation, but for now we limit to first 5 or error.
                # Since user is already created, we just enroll the first 5 and warn? 
                # Better: slice to 5.
                courses_to_enroll = courses_to_enroll[:5]
            
            enrollments = []
            for cid in courses_to_enroll:
                course = mongo.db.courses.find_one({'course_id': cid})
                if course:
                    enrollments.append({
                        'student_id': data['student_id'],
                        'course_id': course['course_id'],
                        'course_name': course['name'],
                        'teacher_id': course['teacher_id'],
                        'marks': None,
                        'enrolled_at': datetime.utcnow()
                    })
            
            if enrollments:
                mongo.db.enrollments.insert_many(enrollments)


    # If role is teacher, create entry in teachers collection
    elif validated_data['role'] == 'teacher':
        teacher_doc = {
            'teacher_id': validated_data['username'],
            'name': data.get('full_name', validated_data['username']),
            'email': validated_data['email'],
            'subject': data.get('subject', 'General'), # Capture subject
            'phone': '',
            'qualification': '',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        mongo.db.teachers.insert_one(teacher_doc)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(result.inserted_id),
        'username': validated_data['username'],
        'role': validated_data['role']
    }), 201


@auth_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    """
    Login and get JWT tokens.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Username and password are required'
        }), 400
    
    # Find user
    user = mongo.db.users.find_one({'username': data['username']})
    
    if not user:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid username or password'
        }), 401
    
    if not user.get('is_active', True):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Account is deactivated'
        }), 401
    
    if not verify_password(data['password'], user['password']):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid username or password'
        }), 401
    
    tokens = generate_tokens(str(user['_id']), user['role'])
    
    # Log successful login
    from flask import current_app
    current_app.logger.info(f"User {user['username']} logged in successfully")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user.get('full_name', ''),
            'student_id': user.get('student_id', None),
            'profile_picture': user.get('profile_picture', None),
            'is_approved': user.get('is_approved', True), # Return approval status
            'cv_url': user.get('cv_url', None)
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@handle_exceptions
def refresh():
    """
    Refresh access token using refresh token.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token
      401:
        description: Invalid refresh token
    """
    current_user_id = get_jwt_identity()
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'User not found'
        }), 401
    
    access_token = create_access_token(
        identity=current_user_id,
        additional_claims={'role': user['role']}
    )
    
    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@handle_exceptions
def logout():
    """
    Logout user.
    In JWT stateless authentication, actual logout is handled by client.
    This endpoint logs the logout event and provides confirmation.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
      401:
        description: Invalid token
    """
    try:
        # Get JWT identity
        current_user_id = get_jwt_identity()
        
        # Get user information for logging
        from bson.objectid import ObjectId
        user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        
        if user:
            # Log the logout event
            from flask import current_app
            current_app.logger.info(f"User {user['username']} (ID: {current_user_id}) logged out successfully")
            
            # Optionally update last logout time in user document
            mongo.db.users.update_one(
                {'_id': ObjectId(current_user_id)},
                {'$set': {'last_logout': datetime.utcnow()}}
            )
        
        return jsonify({
            'message': 'Logout successful',
            'logout_time': datetime.utcnow().isoformat(),
            'instruction': 'Please delete the JWT token on client side to complete logout'
        }), 200
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Logout error: {str(e)}")
        
        return jsonify({
            'error': 'Logout failed',
            'message': 'An error occurred during logout'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_current_user():
    """
    Get current user information.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Not Found',
            'message': 'User not found'
        }), 404
    
    return jsonify({
        'user': {
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user.get('full_name', ''),
            'student_id': user.get('student_id', None),
            'created_at': user.get('created_at', None),
            'is_active': user.get('is_active', True),
            'last_logout': user.get('last_logout', None),
            'profile_picture': user.get('profile_picture', None),
            'is_approved': user.get('is_approved', True),
            'cv_url': user.get('cv_url', None)
        }
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@handle_exceptions
def change_password():
    """
    Change user password.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              example: "oldpassword123"
            new_password:
              type: string
              example: "newpassword123"
    responses:
      200:
        description: Password changed successfully
      400:
        description: Invalid current password
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Current password and new password are required'
        }), 400
    
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({
            'error': 'Not Found',
            'message': 'User not found'
        }), 404
    
    # Verify current password
    if not verify_password(data['current_password'], user['password']):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Current password is incorrect'
        }), 401
    
    # Validate new password
    if len(data['new_password']) < 6:
        return jsonify({
            'error': 'Validation Error',
            'message': 'New password must be at least 6 characters long'
        }), 400
    
    # Hash new password
    new_hashed_password = hash_password(data['new_password'])
    
    # Update password
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {
            '$set': {
                'password': new_hashed_password,
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    # Log password change
    from flask import current_app
    current_app.logger.info(f"User {user['username']} changed password successfully")
    
    return jsonify({
        'message': 'Password changed successfully',
        'changed_at': datetime.utcnow().isoformat()
    }), 200
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
@handle_exceptions
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    from bson.objectid import ObjectId
    user = mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    update_data = {}
    if 'full_name' in data:
        update_data['full_name'] = data['full_name']
    
    # Handle profile picture (Base64 string expected)
    if 'profile_picture' in data:
        update_data['profile_picture'] = data['profile_picture']

    if 'email' in data and data['email'] != user['email']:
        existing = mongo.db.users.find_one({'email': data['email']})
        if existing:
            return jsonify({'error': 'Email already in use'}), 409
        update_data['email'] = data['email']
        
    if not update_data:
        return jsonify({'message': 'No changes made'}), 200
        
    update_data['updated_at'] = datetime.utcnow()
    
    mongo.db.users.update_one(
        {'_id': ObjectId(current_user_id)},
        {'$set': update_data}
    )
    
    # Return updated user object
    updated_user = {
        'user_id': str(user['_id']),
        'username': user['username'],
        'email': update_data.get('email', user['email']),
        'role': user['role'],
        'full_name': update_data.get('full_name', user.get('full_name', '')),
        'profile_picture': update_data.get('profile_picture', user.get('profile_picture'))
    }
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': updated_user
    }), 200


@auth_bp.route('/upload-picture', methods=['POST'])
@jwt_required()
@handle_exceptions
def upload_picture():
    # Imports at the top
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    from bson.objectid import ObjectId
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # File Validation
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
    # Check file size (e.g. 5MB limit)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 5 * 1024 * 1024:
         return jsonify({'error': 'File too large. Max size is 5MB'}), 400

    # File processing
    filename = secure_filename(file.filename)
    unique_filename = f'profile_{get_jwt_identity()}_{int(datetime.utcnow().timestamp())}_{filename}'
    
    # Ensure upload folder exists
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    relative_path = f'/static/uploads/{unique_filename}'
    
    mongo.db.users.update_one(
        {'_id': ObjectId(get_jwt_identity())},
        {'$set': {'profile_picture': relative_path}}
    )
    
    return jsonify({
        'message': 'Profile picture uploaded successfully',
        'profile_picture': relative_path
    }), 200


@auth_bp.route('/remove-picture', methods=['POST'])
@jwt_required()
@handle_exceptions
def remove_picture():
    """
    Remove profile picture.
    """
    from bson.objectid import ObjectId
    mongo.db.users.update_one(
        {'_id': ObjectId(get_jwt_identity())},
        {'$set': {'profile_picture': None}}
    )
    
    return jsonify({
        'message': 'Profile picture removed successfully'
    }), 200


@auth_bp.route('/upload-cv', methods=['POST'])
@jwt_required()
@handle_exceptions
def upload_cv():
    """
    Upload CV for teacher approval.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        from bson.objectid import ObjectId
        
        filename = secure_filename(file.filename)
        unique_filename = f'CV_{get_jwt_identity()}_{int(datetime.utcnow().timestamp())}_{filename}'
        
        # Ensure cv upload folder exists
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'cvs')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        relative_path = f'/static/uploads/cvs/{unique_filename}'
        
        mongo.db.users.update_one(
            {'_id': ObjectId(get_jwt_identity())},
            {'$set': {'cv_url': relative_path}}
        )
        
        return jsonify({
            'message': 'CV uploaded successfully',
            'cv_url': relative_path
        }), 200


@auth_bp.route('/pending-teachers', methods=['GET'])
@jwt_required()
@handle_exceptions
def get_pending_teachers():
    """
    Get all teachers with is_approved=False.
    Admin only.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403

    from bson.objectid import ObjectId
    # Find all users with role 'teacher' and is_approved=False
    users = list(mongo.db.users.find({'role': 'teacher', 'is_approved': False}))
    
    pending = []
    for u in users:
         # Get teacher details for subject etc.
         teacher_profile = mongo.db.teachers.find_one({'teacher_id': u['username']})
         
         pending.append({
             'user_id': str(u['_id']),
             'username': u['username'],
             'full_name': u.get('full_name', ''),
             'email': u['email'],
             'subject': teacher_profile.get('subject', 'General') if teacher_profile else 'Unknown',
             'cv_url': u.get('cv_url'),
             'created_at': u.get('created_at')
         })

    return jsonify({'pending_teachers': pending}), 200


@auth_bp.route('/approve-teacher/<user_id>', methods=['POST'])
@jwt_required()
@handle_exceptions
def approve_teacher(user_id):
    """
    Approve a pending teacher.
    Admin only.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403

    from bson.objectid import ObjectId
    result = mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'is_approved': True}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'Teacher approved successfully'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
@handle_exceptions
def forgot_password():
    """
    Initiate password reset.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
    responses:
      200:
        description: Reset token generated
      404:
        description: Email not found
    """
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
        
    user = mongo.db.users.find_one({'email': data['email']})
    
    if not user:
        return jsonify({'error': 'Email not found'}), 404
        
    # Generate reset token (valid for 15 minutes)
    from datetime import timedelta
    reset_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=timedelta(minutes=15),
        additional_claims={'type': 'reset'}
    )
    
    # In a real app, send this via email. Here we return it.
    return jsonify({
        'message': 'Password reset initiated',
        'reset_token': reset_token,
        'instruction': 'Use this token to reset your password'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
@handle_exceptions
def reset_password():
    """
    Reset password using token.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - new_password
          properties:
            new_password:
              type: string
    responses:
      200:
        description: Password reset successful
      400:
        description: Invalid password
    """
    claims = get_jwt()
    if claims.get('type') != 'reset':
        return jsonify({'error': 'Invalid token type'}), 400
        
    data = request.get_json()
    if not data or 'new_password' not in data:
        return jsonify({'error': 'New password is required'}), 400
        
    if len(data['new_password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
    user_id = get_jwt_identity()
    hashed_pwd = hash_password(data['new_password'])
    
    from bson.objectid import ObjectId
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$set': {
                'password': hashed_pwd,
                'updated_at': datetime.utcnow()
            }
        }
    )
    
    return jsonify({'message': 'Password reset successful. Please login.'}), 200

