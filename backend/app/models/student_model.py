"""
Student model with schema and validation.
Defines the structure for student records in MongoDB.
"""
from marshmallow import Schema, fields, validate, ValidationError


class StudentSchema(Schema):
    """Schema for student validation and serialization."""
    student_id = fields.Str(required=True, validate=validate.Length(min=1))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=5, max=100))
    gender = fields.Str(required=True, validate=validate.OneOf(['Male', 'Female', 'Other']))
    study_time = fields.Int(required=True, validate=validate.Range(min=0, max=168))
    absences = fields.Int(required=True, validate=validate.Range(min=0))
    parental_support = fields.Str(required=True, validate=validate.OneOf(['low', 'medium', 'high']))
    internet_access = fields.Bool(required=True)
    final_grade = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    attendance_log = fields.List(fields.Dict(), required=False)
    enrolled_subjects = fields.List(fields.String(), required=False) # Made optional for backward compat, but seeded data has it
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class StudentUpdateSchema(Schema):
    """Schema for updating student - all fields optional."""
    student_id = fields.Str(validate=validate.Length(min=1))
    name = fields.Str(validate=validate.Length(min=1, max=100))
    age = fields.Int(validate=validate.Range(min=5, max=100))
    gender = fields.Str(validate=validate.OneOf(['Male', 'Female', 'Other']))
    study_time = fields.Int(validate=validate.Range(min=0, max=168))
    absences = fields.Int(validate=validate.Range(min=0))
    parental_support = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    internet_access = fields.Bool()
    final_grade = fields.Int(validate=validate.Range(min=0, max=100))
    attendance_log = fields.List(fields.Dict())
    enrolled_subjects = fields.List(fields.String())


def validate_student_data(data, partial=False):
    """Validate student data against schema."""
    if partial:
        schema = StudentUpdateSchema()
    else:
        schema = StudentSchema()
    
    return schema.load(data)


def serialize_student(student):
    """Serialize student document for JSON response."""
    if student is None:
        return None
    
    student['_id'] = str(student['_id'])
    return student


def predict_student_performance(student):
    """
    Predict student performance using a weighted heuristic algorithm.
    Simulates a linear regression model based on key academic indicators.
    """
    # 1. Base factors
    current_grade = student.get('final_grade', 0)
    study_time = student.get('study_time', 0)
    absences = student.get('absences', 0)
    
    # 2. Categorical modifiers
    support_map = {'low': -5, 'medium': 0, 'high': 5}
    parental_support = student.get('parental_support', 'medium')
    support_score = support_map.get(parental_support, 0)
    
    internet_access = student.get('internet_access', True)
    internet_score = 5 if internet_access else -2

    # 3. Weighted Algorithm
    # Formula: 50% Current Grade + Impact of Habits
    # Habits: Study Time (+2/hr), Absences (-1.5/day), Support/Internet
    
    habit_score = (study_time * 2.0) - (absences * 1.5) + support_score + internet_score
    
    # Calculate predicted next grade (Base assumption: average student starts around 60 without info)
    # We blend the current performance with the habit trajectory
    predicted_grade = (current_grade * 0.6) + (habit_score * 0.4) + 20 
    
    # Clamp result
    predicted_grade = max(0, min(100, predicted_grade))
    
    # 4. Generate Insight
    prediction = 'pass' if predicted_grade >= 40 else 'fail'
    
    risk_level = 'high'
    if predicted_grade >= 70:
        risk_level = 'low'
    elif predicted_grade >= 40:
        risk_level = 'medium'

    # 5. Confidence (simulated based on data completeness/variance)
    # Higher study time usually yields higher confidence in the result
    confidence = min(0.95, 0.70 + (study_time * 0.02))

    return {
        'student_id': student.get('student_id'),
        'name': student.get('name'),
        'current_grade': current_grade,
        'predicted_grade': round(predicted_grade, 1),
        'prediction': prediction,
        'confidence': round(confidence, 2),
        'risk_level': risk_level,
        'factors': {
            'study_impact': round(study_time * 2.0, 1),
            'absence_penalty': round(absences * -1.5, 1)
        }
    }
