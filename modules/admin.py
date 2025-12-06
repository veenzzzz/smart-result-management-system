import sys
import os
from tabulate import tabulate

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import create_connection
from utils.helpers import *
from utils.validators import *
from utils.grade_calc import calculate_grade
from modules.auth import AuthManager

class AdminModule:
    def __init__(self, auth_manager):
        self.auth = auth_manager
    
    # ==================== STUDENT MANAGEMENT ====================
    
    def add_student(self):
        """Add a new student"""
        clear_screen()
        print_header("ADD NEW STUDENT")
        
        name = get_input("Enter student name")
        if not name:
            return
        
        # Validate and get roll number
        while True:
            roll_no = get_input("Enter roll number")
            if not roll_no:
                return
            
            roll_no = roll_no.upper()
            valid, msg = validate_roll_no(roll_no)
            if not valid:
                print(f"❌ {msg}")
                continue
            
            # Check if roll number already exists
            if self._roll_no_exists(roll_no):
                print("❌ Roll number already exists. Please use a different one.")
                continue
            
            break
        
        # Get class
        classes = self._get_all_classes()
        if not classes:
            print("❌ No classes available. Please create a class first.")
            pause()
            return
        
        print("\nAvailable Classes:")
        for cls in classes:
            print(f"  [{cls[0]}] {cls[1]} - {cls[2]}")
        
        class_id = get_input("Enter class ID", int)
        if class_id is None:
            return
        
        # Validate date of birth
        while True:
            dob = get_input("Enter date of birth (YYYY-MM-DD)")
            if not dob:
                return
            
            valid, msg = validate_date(dob)
            if not valid:
                print(f"❌ {msg}")
                continue
            break
        
        # Validate contact
        while True:
            contact = get_input("Enter contact number", allow_empty=True)
            
            if contact:
                valid, msg = validate_contact(contact)
                if not valid:
                    print(f"❌ {msg}")
                    continue
            break
        
        # Get password
        while True:
            password = get_input("Enter password for student")
            if not password:
                return
            
            valid, msg = validate_password(password)
            if not valid:
                print(f"❌ {msg}")
                continue
            break
        
        # Hash password
        hashed_password = self.auth.hash_password(password)
        
        # Insert student
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO students (name, roll_no, class_id, dob, contact, password)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, roll_no, class_id, dob, contact, hashed_password))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Added student: {name} ({roll_no})")
            
            print(f"\n✅ Student added successfully!")
            print(f"   Name: {name}")
            print(f"   Roll No: {roll_no}")
            
        except Exception as e:
            print(f"❌ Error adding student: {e}")
        finally:
            conn.close()
        
        pause()
    
    def view_all_students(self):
        """View all students"""
        clear_screen()
        print_header("ALL STUDENTS")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.student_id, s.name, s.roll_no, c.class_name, co.course_name, s.contact
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN courses co ON c.course_id = co.course_id
                ORDER BY s.roll_no
            """)
            
            students = cursor.fetchall()
            
            if not students:
                print("\n📭 No students found.")
            else:
                headers = ["ID", "Name", "Roll No", "Class", "Course", "Contact"]
                print("\n" + tabulate(students, headers=headers, tablefmt="grid"))
                print(f"\nTotal Students: {len(students)}")
            
        except Exception as e:
            print(f"❌ Error fetching students: {e}")
        finally:
            conn.close()
        
        pause()
    
    def edit_student(self):
        """Edit student details"""
        clear_screen()
        print_header("EDIT STUDENT")
        
        roll_no = get_input("Enter student roll number to edit")
        if not roll_no:
            return
        
        roll_no = roll_no.upper()
        
        # Get student details
        student = self._get_student_by_roll_no(roll_no)
        if not student:
            print(f"❌ Student with roll number {roll_no} not found.")
            pause()
            return
        
        student_id, name, old_roll_no, class_id, dob, contact = student
        
        print(f"\nCurrent Details:")
        print(f"  Name: {name}")
        print(f"  Roll No: {old_roll_no}")
        print(f"  Class ID: {class_id}")
        print(f"  DOB: {dob}")
        print(f"  Contact: {contact}")
        
        print("\n(Press Enter to keep current value)")
        
        new_name = get_input(f"New name [{name}]", allow_empty=True) or name
        new_contact = get_input(f"New contact [{contact}]", allow_empty=True) or contact
        
        # Update student
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE students
                SET name = ?, contact = ?
                WHERE student_id = ?
            """, (new_name, new_contact, student_id))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Updated student: {old_roll_no}")
            
            print("\n✅ Student updated successfully!")
            
        except Exception as e:
            print(f"❌ Error updating student: {e}")
        finally:
            conn.close()
        
        pause()
    
    def delete_student(self):
        """Delete a student"""
        clear_screen()
        print_header("DELETE STUDENT")
        
        roll_no = get_input("Enter student roll number to delete")
        if not roll_no:
            return
        
        roll_no = roll_no.upper()
        
        # Get student details
        student = self._get_student_by_roll_no(roll_no)
        if not student:
            print(f"❌ Student with roll number {roll_no} not found.")
            pause()
            return
        
        student_id, name, _, _, _, _ = student
        
        print(f"\n⚠️ You are about to delete:")
        print(f"   Name: {name}")
        print(f"   Roll No: {roll_no}")
        
        if not confirm_action("\nAre you sure you want to delete this student?"):
            print("❌ Deletion cancelled.")
            pause()
            return
        
        # Delete student
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Deleted student: {name} ({roll_no})")
            
            print("\n✅ Student deleted successfully!")
            
        except Exception as e:
            print(f"❌ Error deleting student: {e}")
        finally:
            conn.close()
        
        pause()
    
    # ==================== COURSE/CLASS MANAGEMENT ====================
    
    def add_course(self):
        """Add a new course"""
        clear_screen()
        print_header("ADD NEW COURSE")
        
        course_name = get_input("Enter course name")
        if not course_name:
            return
        
        duration = get_input("Enter course duration (e.g., 4 years)")
        if not duration:
            return
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO courses (course_name, duration)
                VALUES (?, ?)
            """, (course_name, duration))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Added course: {course_name}")
            
            print(f"\n✅ Course '{course_name}' added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding course: {e}")
        finally:
            conn.close()
        
        pause()
    
    def add_class(self):
        """Add a new class"""
        clear_screen()
        print_header("ADD NEW CLASS")
        
        # Show available courses
        courses = self._get_all_courses()
        if not courses:
            print("❌ No courses available. Please create a course first.")
            pause()
            return
        
        print("\nAvailable Courses:")
        for course in courses:
            print(f"  [{course[0]}] {course[1]} - {course[2]}")
        
        course_id = get_input("\nEnter course ID", int)
        if course_id is None:
            return
        
        class_name = get_input("Enter class name (e.g., 10-A, 12-B)")
        if not class_name:
            return
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO classes (class_name, course_id)
                VALUES (?, ?)
            """, (class_name, course_id))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Added class: {class_name}")
            
            print(f"\n✅ Class '{class_name}' added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding class: {e}")
        finally:
            conn.close()
        
        pause()
    
    def view_courses_and_classes(self):
        """View all courses and classes"""
        clear_screen()
        print_header("COURSES AND CLASSES")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            # Get courses
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            
            if not courses:
                print("\n📭 No courses found.")
            else:
                print("\n📚 COURSES:")
                headers = ["ID", "Course Name", "Duration"]
                print(tabulate(courses, headers=headers, tablefmt="grid"))
            
            # Get classes
            cursor.execute("""
                SELECT c.class_id, c.class_name, co.course_name
                FROM classes c
                LEFT JOIN courses co ON c.course_id = co.course_id
            """)
            classes = cursor.fetchall()
            
            if not classes:
                print("\n📭 No classes found.")
            else:
                print("\n🏫 CLASSES:")
                headers = ["ID", "Class Name", "Course"]
                print(tabulate(classes, headers=headers, tablefmt="grid"))
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
        finally:
            conn.close()
        
        pause()
    
    # ==================== SUBJECT MANAGEMENT ====================
    
    def add_subject(self):
        """Add a new subject"""
        clear_screen()
        print_header("ADD NEW SUBJECT")
        
        # Show available classes
        classes = self._get_all_classes()
        if not classes:
            print("❌ No classes available. Please create a class first.")
            pause()
            return
        
        print("\nAvailable Classes:")
        for cls in classes:
            print(f"  [{cls[0]}] {cls[1]}")
        
        class_id = get_input("\nEnter class ID", int)
        if class_id is None:
            return
        
        subject_name = get_input("Enter subject name")
        if not subject_name:
            return
        
        max_marks = get_input("Enter maximum marks", int)
        if max_marks is None or max_marks <= 0:
            print("❌ Maximum marks must be greater than 0.")
            pause()
            return
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO subjects (subject_name, class_id, max_marks)
                VALUES (?, ?, ?)
            """, (subject_name, class_id, max_marks))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Added subject: {subject_name}")
            
            print(f"\n✅ Subject '{subject_name}' added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding subject: {e}")
        finally:
            conn.close()
        
        pause()
    
    def view_all_subjects(self):
        """View all subjects"""
        clear_screen()
        print_header("ALL SUBJECTS")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.subject_id, s.subject_name, c.class_name, s.max_marks
                FROM subjects s
                LEFT JOIN classes c ON s.class_id = c.class_id
                ORDER BY c.class_name, s.subject_name
            """)
            
            subjects = cursor.fetchall()
            
            if not subjects:
                print("\n📭 No subjects found.")
            else:
                headers = ["ID", "Subject Name", "Class", "Max Marks"]
                print("\n" + tabulate(subjects, headers=headers, tablefmt="grid"))
                print(f"\nTotal Subjects: {len(subjects)}")
            
        except Exception as e:
            print(f"❌ Error fetching subjects: {e}")
        finally:
            conn.close()
        
        pause()
    
    # ==================== RESULT MANAGEMENT ====================
    
    def enter_marks(self):
        """Enter marks for a student"""
        clear_screen()
        print_header("ENTER MARKS")
        
        roll_no = get_input("Enter student roll number")
        if not roll_no:
            return
        
        roll_no = roll_no.upper()
        
        # Get student details
        student = self._get_student_by_roll_no(roll_no)
        if not student:
            print(f"❌ Student with roll number {roll_no} not found.")
            pause()
            return
        
        student_id, name, _, class_id, _, _ = student
        
        print(f"\nStudent: {name}")
        print(f"Roll No: {roll_no}")
        
        # Get subjects for this class
        subjects = self._get_subjects_by_class(class_id)
        if not subjects:
            print("❌ No subjects found for this class.")
            pause()
            return
        
        print("\nAvailable Subjects:")
        for subj in subjects:
            print(f"  [{subj[0]}] {subj[1]} (Max: {subj[2]})")
        
        subject_id = get_input("\nEnter subject ID", int)
        if subject_id is None:
            return
        
        # Get max marks for this subject
        max_marks = None
        for subj in subjects:
            if subj[0] == subject_id:
                max_marks = subj[2]
                break
        
        if max_marks is None:
            print("❌ Invalid subject ID.")
            pause()
            return
        
        # Get marks
        while True:
            marks = get_input(f"Enter marks obtained (Max: {max_marks})", int)
            if marks is None:
                return
            
            valid, msg = validate_marks(marks, max_marks)
            if not valid:
                print(f"❌ {msg}")
                continue
            break
        
        semester = get_input("Enter semester (e.g., Semester 1, Annual)")
        if not semester:
            return
        
        # Calculate grade
        grade, _ = calculate_grade(marks, max_marks)
        
        # Check if result already exists
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT result_id FROM results
                WHERE student_id = ? AND subject_id = ? AND semester = ?
            """, (student_id, subject_id, semester))
            
            existing = cursor.fetchone()
            
            if existing:
                if not confirm_action("Result already exists. Do you want to update it?"):
                    print("❌ Operation cancelled.")
                    pause()
                    return
                
                # Update existing result
                cursor.execute("""
                    UPDATE results
                    SET marks_obtained = ?, grade = ?, published = 1
                    WHERE result_id = ?
                """, (marks, grade, existing[0]))
                
                action = "Updated"
            else:
                # Insert new result
                cursor.execute("""
                    INSERT INTO results (student_id, subject_id, marks_obtained, grade, semester, published)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (student_id, subject_id, marks, grade, semester))
                
                action = "Added"
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"{action} marks for {roll_no}")
            
            print(f"\n✅ Marks {action.lower()} successfully!")
            print(f"   Marks: {marks}/{max_marks}")
            print(f"   Grade: {grade}")
            
        except Exception as e:
            print(f"❌ Error entering marks: {e}")
        finally:
            conn.close()
        
        pause()
    
    def publish_results(self):
        """Publish or unpublish results"""
        clear_screen()
        print_header("PUBLISH/UNPUBLISH RESULTS")
        
        semester = get_input("Enter semester to publish/unpublish")
        if not semester:
            return
        
        print("\n[1] Publish Results")
        print("[2] Unpublish Results")
        
        choice = get_input("\nEnter choice", int)
        if choice not in [1, 2]:
            print("❌ Invalid choice.")
            pause()
            return
        
        published = 1 if choice == 1 else 0
        action = "publish" if choice == 1 else "unpublish"
        
        if not confirm_action(f"Are you sure you want to {action} results for {semester}?"):
            print("❌ Operation cancelled.")
            pause()
            return
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE results
                SET published = ?
                WHERE semester = ?
            """, (published, semester))
            
            affected = cursor.rowcount
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"{action.capitalize()}ed results for {semester}")
            
            print(f"\n✅ Results {action}ed successfully!")
            print(f"   Affected records: {affected}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            conn.close()
        
        pause()
    
    # ==================== USER MANAGEMENT ====================
    
    def create_staff_account(self):
        """Create a new staff account"""
        clear_screen()
        print_header("CREATE STAFF ACCOUNT")
        
        # Validate username
        while True:
            username = get_input("Enter username")
            if not username:
                return
            
            valid, msg = validate_username(username)
            if not valid:
                print(f"❌ {msg}")
                continue
            
            # Check if username exists
            if self._username_exists(username):
                print("❌ Username already exists. Please choose another.")
                continue
            
            break
        
        # Get password
        while True:
            password = get_input("Enter password")
            if not password:
                return
            
            valid, msg = validate_password(password)
            if not valid:
                print(f"❌ {msg}")
                continue
            break
        
        # Get role
        print("\n[1] Admin")
        print("[2] Staff")
        
        role_choice = get_input("\nSelect role", int)
        if role_choice not in [1, 2]:
            print("❌ Invalid choice.")
            pause()
            return
        
        role = "admin" if role_choice == 1 else "staff"
        
        # Hash password
        hashed_password = self.auth.hash_password(password)
        
        # Insert user
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, hashed_password, role))
            
            conn.commit()
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Created {role} account: {username}")
            
            print(f"\n✅ {role.capitalize()} account created successfully!")
            print(f"   Username: {username}")
            
        except Exception as e:
            print(f"❌ Error creating account: {e}")
        finally:
            conn.close()
        
        pause()
    
    def view_activity_logs(self):
        """View system activity logs"""
        clear_screen()
        print_header("ACTIVITY LOGS")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT l.log_id, u.username, l.action, l.timestamp
                FROM logs l
                LEFT JOIN users u ON l.user_id = u.user_id
                ORDER BY l.timestamp DESC
                LIMIT 50
            """)
            
            logs = cursor.fetchall()
            
            if not logs:
                print("\n📭 No activity logs found.")
            else:
                headers = ["ID", "User", "Action", "Timestamp"]
                print("\n" + tabulate(logs, headers=headers, tablefmt="grid"))
                print(f"\nShowing last 50 activities")
            
        except Exception as e:
            print(f"❌ Error fetching logs: {e}")
        finally:
            conn.close()
        
        pause()
    
    # ==================== HELPER METHODS ====================
    
    def _roll_no_exists(self, roll_no):
        """Check if roll number exists"""
        conn = create_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students WHERE roll_no = ?", (roll_no,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _username_exists(self, username):
        """Check if username exists"""
        conn = create_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _get_student_by_roll_no(self, roll_no):
        """Get student details by roll number"""
        conn = create_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT student_id, name, roll_no, class_id, dob, contact
            FROM students
            WHERE roll_no = ?
        """, (roll_no,))
        
        student = cursor.fetchone()
        conn.close()
        
        return student
    
    def _get_all_courses(self):
        """Get all courses"""
        conn = create_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        conn.close()
        
        return courses
    
    def _get_all_classes(self):
        """Get all classes"""
        conn = create_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.class_id, c.class_name, co.course_name
            FROM classes c
            LEFT JOIN courses co ON c.course_id = co.course_id
        """)
        classes = cursor.fetchall()
        conn.close()
        
        return classes
    
    def _get_subjects_by_class(self, class_id):
        """Get subjects for a class"""
        conn = create_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subject_id, subject_name, max_marks
            FROM subjects
            WHERE class_id = ?
        """, (class_id,))
        subjects = cursor.fetchall()
        conn.close()
        
        return subjects