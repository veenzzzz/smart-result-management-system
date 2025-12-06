import sys
import os
from tabulate import tabulate

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import create_connection
from utils.helpers import *
from utils.grade_calc import *

class ReportModule:
    def __init__(self, auth_manager):
        self.auth = auth_manager
    
    def generate_student_report(self):
        """Generate individual student report"""
        clear_screen()
        print_header("STUDENT REPORT")
        
        roll_no = get_input("Enter student roll number")
        if not roll_no:
            return
        
        roll_no = roll_no.upper()
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            # Get student info
            cursor.execute("""
                SELECT s.name, s.roll_no, c.class_name, co.course_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN courses co ON c.course_id = co.course_id
                WHERE s.roll_no = ?
            """, (roll_no,))
            
            student = cursor.fetchone()
            
            if not student:
                print(f"❌ Student with roll number {roll_no} not found.")
                pause()
                return
            
            name, roll_no, class_name, course_name = student
            
            print(f"\nStudent: {name}")
            print(f"Roll No: {roll_no}")
            print(f"Class: {class_name}")
            print(f"Course: {course_name}")
            print_separator()
            
            # Get all results
            cursor.execute("""
                SELECT r.semester, sub.subject_name, sub.max_marks, r.marks_obtained, r.grade
                FROM results r
                JOIN subjects sub ON r.subject_id = sub.subject_id
                JOIN students s ON r.student_id = s.student_id
                WHERE s.roll_no = ?
                ORDER BY r.semester, sub.subject_name
            """, (roll_no,))
            
            results = cursor.fetchall()
            
            if not results:
                print("\n📭 No results found for this student.")
                pause()
                return
            
            # Group by semester
            current_semester = None
            semester_data = []
            
            for semester, subject, max_marks, marks, grade in results:
                if current_semester != semester:
                    if semester_data:
                        self._print_semester_data(current_semester, semester_data)
                        semester_data = []
                    current_semester = semester
                
                semester_data.append([subject, marks, max_marks, grade])
            
            # Print last semester
            if semester_data:
                self._print_semester_data(current_semester, semester_data)
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Generated report for {roll_no}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        finally:
            conn.close()
        
        pause()
    
    def generate_class_report(self):
        """Generate class-wise report"""
        clear_screen()
        print_header("CLASS REPORT")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            # Get all classes
            cursor.execute("""
                SELECT c.class_id, c.class_name, co.course_name
                FROM classes c
                LEFT JOIN courses co ON c.course_id = co.course_id
            """)
            
            classes = cursor.fetchall()
            
            if not classes:
                print("❌ No classes found.")
                pause()
                return
            
            print("\nAvailable Classes:")
            for cls in classes:
                print(f"  [{cls[0]}] {cls[1]} - {cls[2]}")
            
            class_id = get_input("\nEnter class ID", int)
            if class_id is None:
                return
            
            semester = get_input("Enter semester")
            if not semester:
                return
            
            # Get class name
            class_name = None
            for cls in classes:
                if cls[0] == class_id:
                    class_name = cls[1]
                    break
            
            print(f"\n📊 Class Report: {class_name} - {semester}")
            print_separator()
            
            # Get all students in class with results
            cursor.execute("""
                SELECT s.roll_no, s.name,
                       SUM(r.marks_obtained) as total_marks,
                       SUM(sub.max_marks) as total_max
                FROM students s
                LEFT JOIN results r ON s.student_id = r.student_id AND r.semester = ?
                LEFT JOIN subjects sub ON r.subject_id = sub.subject_id
                WHERE s.class_id = ?
                GROUP BY s.student_id
                ORDER BY total_marks DESC
            """, (semester, class_id))
            
            students = cursor.fetchall()
            
            if not students:
                print("\n📭 No students found in this class.")
                pause()
                return
            
            # Display results
            table_data = []
            rank = 1
            
            for roll_no, name, total_marks, total_max in students:
                if total_marks is not None and total_max is not None:
                    grade, percentage = calculate_overall_grade(total_marks, total_max)
                    status = "PASS" if is_passing_grade(grade) else "FAIL"
                    table_data.append([rank, roll_no, name, total_marks, total_max, 
                                     f"{percentage}%", grade, status])
                    rank += 1
                else:
                    table_data.append(["-", roll_no, name, "-", "-", "-", "-", "No Results"])
            
            headers = ["Rank", "Roll No", "Name", "Total", "Max", "Percentage", "Grade", "Status"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            print(f"\nTotal Students: {len(students)}")
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Generated class report for {class_name}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
        finally:
            conn.close()
        
        pause()
    
    def generate_merit_list(self):
        """Generate merit list (top performers)"""
        clear_screen()
        print_header("MERIT LIST")
        
        semester = get_input("Enter semester")
        if not semester:
            return
        
        top_n = get_input("Enter number of top students to display (default: 10)", int)
        if top_n is None:
            top_n = 10
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.roll_no, s.name, c.class_name,
                       SUM(r.marks_obtained) as total_marks,
                       SUM(sub.max_marks) as total_max
                FROM students s
                JOIN results r ON s.student_id = r.student_id
                JOIN subjects sub ON r.subject_id = sub.subject_id
                LEFT JOIN classes c ON s.class_id = c.class_id
                WHERE r.semester = ? AND r.published = 1
                GROUP BY s.student_id
                ORDER BY total_marks DESC
                LIMIT ?
            """, (semester, top_n))
            
            students = cursor.fetchall()
            
            if not students:
                print(f"\n📭 No results found for {semester}.")
                pause()
                return
            
            print(f"\n🏆 TOP {top_n} STUDENTS - {semester}")
            print_separator()
            
            table_data = []
            rank = 1
            
            for roll_no, name, class_name, total_marks, total_max in students:
                grade, percentage = calculate_overall_grade(total_marks, total_max)
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else ""
                table_data.append([f"{rank} {medal}", roll_no, name, class_name, 
                                 total_marks, total_max, f"{percentage}%", grade])
                rank += 1
            
            headers = ["Rank", "Roll No", "Name", "Class", "Total", "Max", "Percentage", "Grade"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Log activity
            self.auth.log_activity(self.auth.get_current_user_id(), 
                                 f"Generated merit list for {semester}")
            
        except Exception as e:
            print(f"❌ Error generating merit list: {e}")
        finally:
            conn.close()
        
        pause()
    
    def _print_semester_data(self, semester, data):
        """Print semester results"""
        print(f"\n📊 {semester}")
        print_separator()
        
        headers = ["Subject", "Marks", "Max Marks", "Grade"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
        # Calculate totals
        total_marks = sum(row[1] for row in data)
        total_max = sum(row[2] for row in data)
        
        grade, percentage = calculate_overall_grade(total_marks, total_max)
        status = "PASS" if is_passing_grade(grade) else "FAIL"
        
        print(f"\nTotal: {total_marks}/{total_max}")
        print(f"Percentage: {percentage}%")
        print(f"Grade: {grade}")
        print(f"Status: {status}")