#!/usr/bin/env python3
"""
ResultHub Backend API
Flask API server for the ResultHub frontend
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import bcrypt
import os
import sys
import random
from datetime import datetime
from functools import wraps

# Add the parent directory to the path to import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from database.db_setup import create_connection
from modules.auth import AuthManager
from utils.helpers import get_current_timestamp

app = Flask(__name__)
app.secret_key = 'resulthub-secret-key-2024'
CORS(app, supports_credentials=True)

# Initialize auth manager
auth_manager = AuthManager()

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_logged_in():
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    """Decorator to restrict endpoints to specific roles"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not auth_manager.is_logged_in():
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            role = auth_manager.get_current_role()
            if role not in allowed_roles:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def get_db_connection():
    """Get database connection"""
    return create_connection()

def generate_captcha_code(length=6):
    """Generate a simple captcha string without easily confused characters"""
    charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choices(charset, k=length))

def get_student_user_data(student_id):
    """Fetch student profile info for auth responses"""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.roll_no, c.class_name, co.course_name
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
        LEFT JOIN courses co ON c.course_id = co.course_id
        WHERE s.student_id = ?
    """, (student_id,))
    student = cursor.fetchone()
    conn.close()
    if student:
        return {
            'id': student_id,
            'username': student[1],
            'role': 'student',
            'name': student[0],
            'roll_no': student[1],
            'class_name': student[2],
            'course_name': student[3]
        }
    return None

# ==================== AUTHENTICATION ROUTES ====================
@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        ok = conn is not None
        if conn:
            conn.close()
        return jsonify({'success': ok, 'data': {'status': 'ok' if ok else 'db_error'}}), (200 if ok else 500)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/captcha', methods=['GET'])
def get_captcha():
    """Return a captcha code for student login"""
    code = generate_captcha_code()
    session['captcha_code'] = code
    return jsonify({'success': True, 'data': {'captcha': code}})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        login_mode = (data.get('mode') or 'default').strip()
        
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'}), 400

        if login_mode == 'student_captcha':
            captcha_value = (data.get('captcha') or '').strip().upper()
            expected_captcha = (session.get('captcha_code') or '').strip().upper()

            if not expected_captcha:
                return jsonify({'success': False, 'error': 'Captcha expired. Please refresh and try again.'}), 400
            if not captcha_value:
                return jsonify({'success': False, 'error': 'Captcha is required for student login'}), 400
            if captcha_value != expected_captcha:
                return jsonify({'success': False, 'error': 'Invalid captcha. Please try again.'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'success': False, 'error': 'Database connection failed'}), 500

            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, name, roll_no
                FROM students
                WHERE UPPER(roll_no) = ?
            """, (username.upper(),))
            student = cursor.fetchone()
            conn.close()

            if not student:
                return jsonify({'success': False, 'error': 'Student record not found'}), 404

            student_id, student_name, roll_no = student
            auth_manager.current_user = student_id
            auth_manager.current_role = 'student'
            auth_manager.log_activity(student_id, f"Student {roll_no} logged in via captcha")
            session.pop('captcha_code', None)

            user_data = get_student_user_data(student_id)
            if user_data:
                return jsonify({'success': True, 'data': user_data, 'message': f'Welcome, {student_name}!'})
            return jsonify({'success': False, 'error': 'Failed to load student profile'}), 500

        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Try admin login first
        success, message = auth_manager.admin_login(username, password)
        if success:
            user_data = {
                'id': auth_manager.get_current_user_id(),
                'username': username,
                'role': auth_manager.get_current_role(),
                'name': username
            }
            return jsonify({'success': True, 'data': user_data, 'message': message})
        
        # Try student login
        success, message, student_id = auth_manager.student_login(username, password)
        if success:
            user_data = get_student_user_data(student_id)
            if user_data:
                return jsonify({'success': True, 'data': user_data, 'message': message})
            return jsonify({'success': False, 'error': 'Failed to load student profile'}), 500
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    try:
        auth_manager.logout()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password for current user"""
    try:
        data = request.get_json()
        new_password = (data.get('new_password') or '').strip()
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        user_id = auth_manager.get_current_user_id()
        role = auth_manager.get_current_role()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        if role == 'student':
            cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", (bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()), user_id))
        else:
            cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()), user_id))
        conn.commit()
        auth_manager.log_activity(user_id, 'Changed password')
        conn.close()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        user_id = auth_manager.get_current_user_id()
        role = auth_manager.get_current_role()
        
        if role == 'student':
            cursor.execute("""
                SELECT s.name, s.roll_no, c.class_name, co.course_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN courses co ON c.course_id = co.course_id
                WHERE s.student_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                user_data = {
                    'id': user_id,
                    'username': result[1],  # roll_no
                    'role': 'student',
                    'name': result[0],
                    'roll_no': result[1],
                    'class_name': result[2],
                    'course_name': result[3]
                }
            else:
                return jsonify({'success': False, 'error': 'User not found'}), 404
        else:
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                user_data = {
                    'id': user_id,
                    'username': result[0],
                    'role': role,
                    'name': result[0]
                }
            else:
                return jsonify({'success': False, 'error': 'User not found'}), 404
        
        conn.close()
        return jsonify({'success': True, 'data': user_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user's profile (name/email for admins/staff)"""
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        user_id = auth_manager.get_current_user_id()
        role = auth_manager.get_current_role()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        if role == 'student':
            # students don't have email field in schema; update name only
            if not name:
                return jsonify({'success': False, 'error': 'name is required'}), 400
            cursor.execute("UPDATE students SET name = ? WHERE student_id = ?", (name, user_id))
        else:
            # users table doesn't have email column; store in logs as name only for now
            if not name:
                return jsonify({'success': False, 'error': 'name is required'}), 400
            cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (name, user_id))
        conn.commit()
        auth_manager.log_activity(user_id, 'Updated profile')
        conn.close()
        return jsonify({'success': True, 'message': 'Profile updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== DASHBOARD ROUTES ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        total_classes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subjects")
        total_subjects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM results WHERE published = 1")
        published_results = cursor.fetchone()[0]
        
        # Get recent activities
        cursor.execute("""
            SELECT l.log_id, u.username, l.action, l.timestamp
            FROM logs l
            LEFT JOIN users u ON l.user_id = u.user_id
            ORDER BY l.timestamp DESC
            LIMIT 10
        """)
        activities = cursor.fetchall()
        
        recent_activities = []
        for activity in activities:
            recent_activities.append({
                'id': activity[0],
                'username': activity[1],
                'action': activity[2],
                'timestamp': activity[3]
            })
        
        conn.close()
        
        stats = {
            'total_students': total_students,
            'total_classes': total_classes,
            'total_subjects': total_subjects,
            'published_results': published_results,
            'recent_activities': recent_activities
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== COURSES & CLASSES ROUTES ====================

@app.route('/api/courses', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_courses():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("""
            SELECT course_id, course_name, duration,
                   COALESCE(course_code, ''), COALESCE(credits, 0), COALESCE(department, '')
            FROM courses
            ORDER BY course_name
        """)
        rows = cursor.fetchall()
        conn.close()
        data = [
            {
                'id': r[0],
                'course_name': r[1],
                'duration': r[2],
                'course_code': r[3],
                'credits': r[4],
                'department': r[5],
            } for r in rows
        ]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/courses', methods=['POST'])
@login_required
@roles_required('admin', 'staff')
def create_course():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        name = (data.get('course_name') or '').strip()
        code = (data.get('course_code') or '').strip().upper()
        credits = data.get('credits')
        duration = (data.get('duration') or '').strip() or 'N/A'
        department = (data.get('department') or '').strip()

        if not name:
            return jsonify({'success': False, 'error': 'Course name is required'}), 400
        if not code:
            return jsonify({'success': False, 'error': 'Course code is required'}), 400
        try:
            credits_int = int(credits)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Credits must be a number'}), 400
        if credits_int <= 0:
            return jsonify({'success': False, 'error': 'Credits must be greater than 0'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Check for duplicate course_code (case-insensitive)
        cursor.execute("SELECT COUNT(*) FROM courses WHERE UPPER(COALESCE(course_code, '')) = ?", (code,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'error': f'Course code "{code}" already exists. Please use a different code.'}), 400

        try:
            cursor.execute(
                """
                INSERT INTO courses (course_name, duration, course_code, credits, department)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, duration, code, credits_int, department),
            )
            course_id = cursor.lastrowid
            conn.commit()
            
            auth_manager.log_activity(
                auth_manager.get_current_user_id(),
                f"Added course: {name} ({code})"
            )
            conn.close()
            return jsonify({'success': True, 'data': {'id': course_id}, 'message': 'Course created successfully'})
        except sqlite3.IntegrityError as e:
            conn.close()
            error_msg = str(e)
            if 'UNIQUE constraint' in error_msg or 'course_code' in error_msg.lower():
                return jsonify({'success': False, 'error': 'Course code already exists. Please use a different code.'}), 400
            return jsonify({'success': False, 'error': f'Database constraint error: {error_msg}'}), 400
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'error': f'Failed to create course: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@login_required
@roles_required('admin', 'staff')
def update_course(course_id):
    try:
        data = request.get_json()
        allowed = { 'course_name', 'course_code', 'credits', 'department', 'duration' }
        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        if 'credits' in fields:
            try:
                fields['credits'] = int(fields['credits'])
            except (TypeError, ValueError):
                return jsonify({'success': False, 'error': 'credits must be a number'}), 400
        if 'course_code' in fields and not fields['course_code']:
            return jsonify({'success': False, 'error': 'course_code cannot be empty'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        # Check exists
        cursor.execute("SELECT course_id FROM courses WHERE course_id = ?", (course_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        # Unique code check if updating code
        if 'course_code' in fields:
            cursor.execute("SELECT COUNT(*) FROM courses WHERE UPPER(course_code) = ? AND course_id <> ?", (fields['course_code'].upper(), course_id))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return jsonify({'success': False, 'error': 'Course code already exists'}), 400
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        params = list(fields.values()) + [course_id]
        cursor.execute(f"UPDATE courses SET {set_clause} WHERE course_id = ?", params)
        conn.commit()
        auth_manager.log_activity(auth_manager.get_current_user_id(), f"Updated course {course_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Course updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'staff')
def delete_course(course_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        conn.commit()
        auth_manager.log_activity(auth_manager.get_current_user_id(), f"Deleted course {course_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Course deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classes', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_classes():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.class_id, c.class_name, c.course_id, co.course_name
            FROM classes c
            LEFT JOIN courses co ON c.course_id = co.course_id
            ORDER BY co.course_name, c.class_name
        """)
        rows = cursor.fetchall()
        conn.close()
        data = [
            {
                'id': r[0],
                'class_name': r[1],
                'course_id': r[2],
                'course_name': r[3],
            } for r in rows
        ]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STUDENT ROUTES ====================

@app.route('/api/students', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_students():
    """Get all students"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.name, s.roll_no, s.class_id, s.dob, s.contact,
                   c.class_name, co.course_name
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN courses co ON c.course_id = co.course_id
            ORDER BY s.roll_no
        """)
        
        students = cursor.fetchall()
        conn.close()
        
        student_list = []
        for student in students:
            student_list.append({
                'id': student[0],
                'name': student[1],
                'roll_no': student[2],
                'class_id': student[3],
                'dob': student[4],
                'contact': student[5],
                'class_name': student[6],
                'course_name': student[7]
            })
        
        return jsonify({'success': True, 'data': student_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/students', methods=['POST'])
@login_required
@roles_required('admin', 'staff')
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'roll_no', 'class_id', 'dob', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Check if roll number already exists
        cursor.execute("SELECT COUNT(*) FROM students WHERE roll_no = ?", (data['roll_no'].upper(),))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Roll number already exists'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Insert student
        cursor.execute("""
            INSERT INTO students (name, roll_no, class_id, dob, contact, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['name'],
            data['roll_no'].upper(),
            data['class_id'],
            data['dob'],
            data.get('contact', ''),
            hashed_password
        ))
        
        conn.commit()
        
        # Log activity
        auth_manager.log_activity(
            auth_manager.get_current_user_id(),
            f"Added student: {data['name']} ({data['roll_no']})"
        )
        
        conn.close()
        return jsonify({'success': True, 'message': 'Student created successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'staff')
def delete_student(student_id):
    """Delete a student"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Get student info for logging
        cursor.execute("SELECT name, roll_no FROM students WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return jsonify({'success': False, 'error': 'Student not found'}), 404
        
        # Delete student
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        
        # Log activity
        auth_manager.log_activity(
            auth_manager.get_current_user_id(),
            f"Deleted student: {student[0]} ({student[1]})"
        )
        
        conn.close()
        return jsonify({'success': True, 'message': 'Student deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required
@roles_required('admin', 'staff')
def update_student(student_id):
    """Update student basic info"""
    try:
        data = request.get_json()
        allowed = { 'name', 'contact' }
        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        # Ensure student exists
        cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Student not found'}), 404
        # Build dynamic update
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        params = list(fields.values()) + [student_id]
        cursor.execute(f"UPDATE students SET {set_clause} WHERE student_id = ?", params)
        conn.commit()
        auth_manager.log_activity(auth_manager.get_current_user_id(), f"Updated student {student_id}")
        conn.close()
        return jsonify({'success': True, 'message': 'Student updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SUBJECT ROUTES ====================

@app.route('/api/subjects', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_subjects():
    """Get all subjects"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.subject_id, s.subject_name, s.subject_code, s.class_id, s.max_marks,
                   c.class_name
            FROM subjects s
            LEFT JOIN classes c ON s.class_id = c.class_id
            ORDER BY c.class_name, s.subject_name
        """)
        
        subjects = cursor.fetchall()
        conn.close()
        
        subject_list = []
        for subject in subjects:
            subject_list.append({
                'id': subject[0],
                'subject_name': subject[1],
                'subject_code': subject[2],
                'class_id': subject[3],
                'max_marks': subject[4],
                'class_name': subject[5]
            })
        
        return jsonify({'success': True, 'data': subject_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects', methods=['POST'])
@login_required
@roles_required('admin', 'staff')
def create_subject():
    """Create a new subject"""
    try:
        data = request.get_json()

        subject_name = (data.get('subject_name') or '').strip()
        subject_code = (data.get('subject_code') or '').strip().upper() or None
        class_id = data.get('class_id')
        max_marks = data.get('max_marks')

        if not subject_name:
            return jsonify({'success': False, 'error': 'subject_name is required'}), 400
        try:
            max_marks_int = int(max_marks)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'max_marks must be a number'}), 400
        if max_marks_int <= 0:
            return jsonify({'success': False, 'error': 'max_marks must be greater than 0'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        # Prevent duplicate subject within same class by name
        cursor.execute(
            """
            SELECT COUNT(*) FROM subjects
            WHERE LOWER(subject_name) = LOWER(?) AND (class_id IS ? OR class_id = ?)
            """,
            (subject_name, None if class_id is None else None, class_id),
        )
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Subject already exists for this class'}), 400

        # Insert subject
        cursor.execute(
            """
            INSERT INTO subjects (subject_name, class_id, max_marks, subject_code)
            VALUES (?, ?, ?, ?)
            """,
            (subject_name, class_id, max_marks_int, subject_code),
        )
        conn.commit()

        # Log activity
        auth_manager.log_activity(
            auth_manager.get_current_user_id(),
            f"Added subject: {subject_name}"
        )

        conn.close()
        return jsonify({'success': True, 'message': 'Subject created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== RESULT ROUTES ====================

@app.route('/api/results', methods=['POST'])
@login_required
@roles_required('admin', 'staff')
def create_result():
    """Create a new result entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'subject_id', 'marks_obtained', 'semester']
        for field in required_fields:
            if data.get(field) is None:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        student_id_raw = data.get('student_id')
        subject_id_raw = data.get('subject_id')
        marks_raw = data.get('marks_obtained')

        try:
            student_id = int(student_id_raw)
            subject_id = int(subject_id_raw)
            marks_obtained = int(marks_raw)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Invalid numeric value supplied'}), 400
        
        semester = (data.get('semester') or '').strip()
        if not semester:
            return jsonify({'success': False, 'error': 'semester is required'}), 400

        published_flag = 1 if data.get('published', True) else 0

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        
        # Get subject max marks
        cursor.execute("SELECT max_marks FROM subjects WHERE subject_id = ?", (subject_id,))
        subject = cursor.fetchone()
        if not subject:
            conn.close()
            return jsonify({'success': False, 'error': 'Subject not found'}), 404
        
        max_marks = subject[0]
        if marks_obtained > max_marks:
            conn.close()
            return jsonify({'success': False, 'error': f'Marks cannot exceed {max_marks}'}), 400
        
        # Calculate grade
        percentage = (marks_obtained / max_marks) * 100
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 80:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B'
        elif percentage >= 60:
            grade = 'C'
        elif percentage >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        # Check if result already exists
        cursor.execute("""
            SELECT result_id FROM results
            WHERE student_id = ? AND subject_id = ? AND semester = ?
        """, (student_id, subject_id, semester))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing result
            cursor.execute("""
                UPDATE results
                SET marks_obtained = ?, grade = ?, published = ?
                WHERE result_id = ?
            """, (marks_obtained, grade, published_flag, existing[0]))
            action = "Updated"
        else:
            # Insert new result
            cursor.execute("""
                INSERT INTO results (student_id, subject_id, marks_obtained, grade, semester, published)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, subject_id, marks_obtained, grade, semester, published_flag))
            action = "Added"
        
        conn.commit()
        
        # Log activity
        auth_manager.log_activity(
            auth_manager.get_current_user_id(),
            f"{action} marks for student {student_id}"
        )
        
        conn.close()
        return jsonify({'success': True, 'message': f'Marks {action.lower()} successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/results/publish', methods=['PUT'])
@login_required
@roles_required('admin', 'staff')
def publish_results():
    """Publish or unpublish results for a semester"""
    try:
        data = request.get_json()
        semester = (data.get('semester') or '').strip()
        published = bool(data.get('published'))
        if not semester:
            return jsonify({'success': False, 'error': 'semester is required'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        cursor.execute("UPDATE results SET published = ? WHERE semester = ?", (1 if published else 0, semester))
        conn.commit()
        auth_manager.log_activity(auth_manager.get_current_user_id(), f"{'Published' if published else 'Unpublished'} results for {semester}")
        conn.close()
        return jsonify({'success': True, 'message': 'Results updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== REPORTS ====================

@app.route('/api/reports/summary', methods=['GET'])
@login_required
@roles_required('admin', 'staff')
def get_report_summary():
    """Return per-student totals, percentage, and overall grade, optionally filtered by semester"""
    try:
        semester = request.args.get('semester')
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()

        include_unpublished = request.args.get('include_unpublished') in ('1', 'true', 'True')
        base_query = (
            """
            SELECT s.student_id, s.name, s.roll_no,
                   SUM(r.marks_obtained) as total_marks,
                   SUM(sub.max_marks) as total_max,
                   COALESCE(r.semester, '') as semester
            FROM results r
            JOIN students s ON r.student_id = s.student_id
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE {published_clause}
            {semester_clause}
            GROUP BY s.student_id, r.semester
            ORDER BY s.roll_no
            """
        )
        published_clause = "(r.published = 1)" if not include_unpublished else "(1=1)"
        clause = "" if not semester else "AND r.semester = ?"
        cursor.execute(base_query.format(published_clause=published_clause, semester_clause=clause), (() if not semester else (semester,)))
        rows = cursor.fetchall()
        data = []
        for row in rows:
            student_id, name, roll_no, total_marks, total_max, sem = row
            total_marks = total_marks or 0
            total_max = total_max or 0
            percentage = (total_marks / total_max * 100) if total_max > 0 else 0
            if percentage >= 90:
                overall_grade = 'A+'
            elif percentage >= 80:
                overall_grade = 'A'
            elif percentage >= 70:
                overall_grade = 'B'
            elif percentage >= 60:
                overall_grade = 'C'
            elif percentage >= 50:
                overall_grade = 'D'
            else:
                overall_grade = 'F'
            data.append({
                'student_id': student_id,
                'name': name,
                'roll_no': roll_no,
                'total_marks': int(total_marks),
                'total_max': int(total_max),
                'percentage': round(percentage, 2),
                'grade': overall_grade,
                'semester': sem,
            })
        conn.close()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/student/<int:student_id>', methods=['GET'])
@login_required
def get_student_detailed_report(student_id):
    """Get detailed report for a specific student with all subject marks"""
    try:
        role = auth_manager.get_current_role()
        requester_id = auth_manager.get_current_user_id()
        if role == 'student' and student_id != requester_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        if role not in ('admin', 'staff', 'student'):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        semester = request.args.get('semester')
        include_unpublished = request.args.get('include_unpublished') in ('1', 'true', 'True')
        if role == 'student':
            include_unpublished = False
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        cursor = conn.cursor()
        
        # Get student info
        cursor.execute("""
            SELECT s.name, s.roll_no, c.class_name, co.course_name, co.course_code
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN courses co ON c.course_id = co.course_id
            WHERE s.student_id = ?
        """, (student_id,))
        
        student_info = cursor.fetchone()
        if not student_info:
            conn.close()
            return jsonify({'success': False, 'error': 'Student not found'}), 404
        
        name, roll_no, class_name, course_name, course_code = student_info
        
        # Get results with subject details
        query = """
            SELECT sub.subject_code, sub.subject_name, sub.max_marks, 
                   r.marks_obtained, r.grade, r.semester
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE r.student_id = ?
        """
        params = [student_id]
        
        if not include_unpublished:
            query += " AND r.published = 1"
        
        if semester:
            query += " AND r.semester = ?"
            params.append(semester)
        
        query += " ORDER BY r.semester, sub.subject_name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return jsonify({'success': False, 'error': 'No results found for this student'}), 404
        
        # Group by semester
        semester_data = {}
        for row in results:
            sub_code, sub_name, max_marks, marks_obt, grade, sem = row
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append({
                'subject_code': sub_code or '',
                'subject_name': sub_name,
                'max_marks': max_marks,
                'marks_obtained': marks_obt,
                'grade': grade
            })
        
        # Calculate totals for each semester
        report_data = []
        for sem, subjects in semester_data.items():
            total_marks = sum(s['marks_obtained'] for s in subjects)
            total_max = sum(s['max_marks'] for s in subjects)
            percentage = (total_marks / total_max * 100) if total_max > 0 else 0
            
            if percentage >= 90:
                overall_grade = 'A+'
            elif percentage >= 80:
                overall_grade = 'A'
            elif percentage >= 70:
                overall_grade = 'B'
            elif percentage >= 60:
                overall_grade = 'C'
            elif percentage >= 50:
                overall_grade = 'D'
            else:
                overall_grade = 'F'
            
            report_data.append({
                'semester': sem,
                'subjects': subjects,
                'total_marks': total_marks,
                'total_max': total_max,
                'percentage': round(percentage, 2),
                'grade': overall_grade,
                'result_status': 'PASS' if overall_grade != 'F' else 'FAIL'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'student': {
                    'name': name,
                    'roll_no': roll_no,
                    'class_name': class_name or '',
                    'course_name': course_name or '',
                    'course_code': course_code or ''
                },
                'reports': report_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== STUDENT RESULT ROUTES ====================

@app.route('/api/student/recent-results', methods=['GET'])
@login_required
def get_student_recent_results():
    """Get recent results for current student"""
    try:
        if auth_manager.get_current_role() != 'student':
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor()
        student_id = auth_manager.get_current_user_id()
        
        # Get recent results
        cursor.execute("""
            SELECT sub.subject_name, sub.max_marks, r.marks_obtained, r.grade, r.semester
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.subject_id
            WHERE r.student_id = ? AND r.published = 1
            ORDER BY r.semester DESC, sub.subject_name
        """, (student_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Group by semester
        semester_results = {}
        for result in results:
            semester = result[4]
            if semester not in semester_results:
                semester_results[semester] = []
            
            semester_results[semester].append({
                'subject_name': result[0],
                'max_marks': result[1],
                'marks_obtained': result[2],
                'grade': result[3],
                'semester': result[4]
            })
        
        # Convert to list format
        student_reports = []
        for semester, results_list in semester_results.items():
            total_marks = sum(r['marks_obtained'] for r in results_list)
            total_max = sum(r['max_marks'] for r in results_list)
            overall_percentage = (total_marks / total_max * 100) if total_max > 0 else 0
            
            if overall_percentage >= 90:
                overall_grade = 'A+'
            elif overall_percentage >= 80:
                overall_grade = 'A'
            elif overall_percentage >= 70:
                overall_grade = 'B'
            elif overall_percentage >= 60:
                overall_grade = 'C'
            elif overall_percentage >= 50:
                overall_grade = 'D'
            else:
                overall_grade = 'F'
            
            student_reports.append({
                'student': {'id': student_id},
                'results': results_list,
                'overall_percentage': round(overall_percentage, 2),
                'overall_grade': overall_grade,
                'result_status': 'PASS' if overall_grade != 'F' else 'FAIL'
            })
        
        return jsonify({'success': True, 'data': student_reports})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Initialize database
        from database.db_setup import initialize_database, create_default_admin
        print("Initializing database...")
        initialize_database()
        create_default_admin()
        
        print("ResultHub API Server Starting...")
        print("Database initialized")
        print("Default admin created (admin/admin123)")
        print("Server running at http://localhost:5000")
        print("Frontend should connect to http://localhost:3000")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure you're running from the project root directory")
        print("Check that all Python dependencies are installed")
        sys.exit(1)


