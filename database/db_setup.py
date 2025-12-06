import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get the database file path"""
    db_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(db_dir, 'result_tracker.db')

def create_connection():
    """Create a database connection"""
    try:
        conn = sqlite3.connect(get_db_path())
        return conn
    except sqlite3.Error as e:
        print(f"ERROR: Database connection error: {e}")
        return None

def initialize_database():
    """Initialize the database with all required tables"""
    conn = create_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'staff'))
            )
        """)
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                duration TEXT NOT NULL
            )
        """)

        # Ensure new columns exist on courses
        try:
            cursor.execute("PRAGMA table_info(courses)")
            course_cols = [row[1] for row in cursor.fetchall()]
            if 'course_code' not in course_cols:
                # Add column first, then create unique index if needed
                cursor.execute("ALTER TABLE courses ADD COLUMN course_code TEXT")
                # Create unique index separately (SQLite doesn't support UNIQUE in ALTER TABLE ADD COLUMN)
                try:
                    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_course_code ON courses(course_code) WHERE course_code IS NOT NULL")
                except sqlite3.Error:
                    pass
            if 'credits' not in course_cols:
                cursor.execute("ALTER TABLE courses ADD COLUMN credits INTEGER")
            if 'department' not in course_cols:
                cursor.execute("ALTER TABLE courses ADD COLUMN department TEXT")
        except sqlite3.Error as e:
            print(f"Warning: Could not add columns to courses table: {e}")
            pass
        
        # Create classes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                course_id INTEGER,
                FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE
            )
        """)
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL,
                class_id INTEGER,
                dob TEXT,
                contact TEXT,
                password TEXT NOT NULL,
                FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE SET NULL
            )
        """)
        
        # Create subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                class_id INTEGER,
                max_marks INTEGER NOT NULL,
                FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE CASCADE
            )
        """)

        # Ensure subject_code column exists on subjects table
        try:
            cursor.execute("PRAGMA table_info(subjects)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'subject_code' not in columns:
                cursor.execute("ALTER TABLE subjects ADD COLUMN subject_code TEXT")
        except sqlite3.Error:
            # If ALTER fails for any reason, continue without blocking init
            pass
        
        # Create results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject_id INTEGER,
                marks_obtained INTEGER NOT NULL,
                grade TEXT,
                semester TEXT,
                published INTEGER DEFAULT 0,
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            )
        """)
        
        # Create logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        
        conn.commit()
        print("SUCCESS: Database initialized successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"ERROR: Error creating tables: {e}")
        return False
    finally:
        conn.close()

def create_default_admin():
    """Create a default admin user if none exists"""
    import bcrypt
    
    conn = create_connection()
    if conn is None:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if admin exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create default admin
            password = "admin123"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, ("admin", hashed, "admin"))
            
            conn.commit()
            print("SUCCESS: Default admin created (username: admin, password: admin123)")
            return True
        
        return True
        
    except sqlite3.Error as e:
        print(f"ERROR: Error creating admin: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
    create_default_admin()