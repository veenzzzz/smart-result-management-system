import bcrypt
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import create_connection
from utils.helpers import get_current_timestamp

class AuthManager:
    def __init__(self):
        self.current_user = None
        self.current_role = None
    
    def hash_password(self, password):
        """Hash a password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def admin_login(self, username, password):
        """Login for admin/staff"""
        conn = create_connection()
        if conn is None:
            return False, "Database connection failed."
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT user_id, username, password, role
                FROM users
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            
            if user is None:
                return False, "Invalid username or password."
            
            user_id, username, hashed_password, role = user
            
            if self.verify_password(password, hashed_password):
                self.current_user = user_id
                self.current_role = role
                
                # Log the login
                self.log_activity(user_id, f"User {username} logged in")
                
                return True, f"Welcome, {username}!"
            else:
                return False, "Invalid username or password."
                
        except Exception as e:
            return False, f"Login error: {e}"
        finally:
            conn.close()
    
    def student_login(self, roll_no, password):
        """Login for students"""
        conn = create_connection()
        if conn is None:
            return False, "Database connection failed.", None
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT student_id, name, roll_no, password, class_id
                FROM students
                WHERE roll_no = ?
            """, (roll_no.upper(),))
            
            student = cursor.fetchone()
            
            if student is None:
                return False, "Invalid roll number or password.", None
            
            student_id, name, roll_no, hashed_password, class_id = student
            
            if self.verify_password(password, hashed_password):
                self.current_user = student_id
                self.current_role = 'student'
                
                return True, f"Welcome, {name}!", student_id
            else:
                return False, "Invalid roll number or password.", None
                
        except Exception as e:
            return False, f"Login error: {e}", None
        finally:
            conn.close()
    
    def logout(self):
        """Logout current user"""
        if self.current_user and self.current_role != 'student':
            self.log_activity(self.current_user, "User logged out")
        
        self.current_user = None
        self.current_role = None
    
    def change_password(self, old_password, new_password):
        """Change password for current user"""
        if not self.current_user:
            return False, "No user logged in."
        
        conn = create_connection()
        if conn is None:
            return False, "Database connection failed."
        
        cursor = conn.cursor()
        
        try:
            if self.current_role == 'student':
                cursor.execute("SELECT password FROM students WHERE student_id = ?", (self.current_user,))
            else:
                cursor.execute("SELECT password FROM users WHERE user_id = ?", (self.current_user,))
            
            result = cursor.fetchone()
            if not result:
                return False, "User not found."
            
            current_hash = result[0]
            
            if not self.verify_password(old_password, current_hash):
                return False, "Current password is incorrect."
            
            new_hash = self.hash_password(new_password)
            
            if self.current_role == 'student':
                cursor.execute("UPDATE students SET password = ? WHERE student_id = ?", 
                             (new_hash, self.current_user))
            else:
                cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", 
                             (new_hash, self.current_user))
                self.log_activity(self.current_user, "Password changed")
            
            conn.commit()
            return True, "Password changed successfully!"
            
        except Exception as e:
            return False, f"Error changing password: {e}"
        finally:
            conn.close()
    
    def log_activity(self, user_id, action):
        """Log user activity"""
        conn = create_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO logs (user_id, action, timestamp)
                VALUES (?, ?, ?)
            """, (user_id, action, get_current_timestamp()))
            
            conn.commit()
        except Exception as e:
            print(f"⚠️ Logging error: {e}")
        finally:
            conn.close()
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return self.current_user is not None
    
    def get_current_user_id(self):
        """Get current user ID"""
        return self.current_user
    
    def get_current_role(self):
        """Get current user role"""
        return self.current_role