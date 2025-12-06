import sys
import os
from tabulate import tabulate

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import create_connection
from utils.helpers import *
from utils.grade_calc import *

class StudentModule:
    def __init__(self, student_id):
        self.student_id = student_id
        self.student_info = self._get_student_info()
    
    def _get_student_info(self):
        """Get student information"""
        conn = create_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT s.name, s.roll_no, c.class_name, co.course_name
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN courses co ON c.course_id = co.course_id
                WHERE s.student_id = ?
            """, (self.student_id,))
            
            return cursor.fetchone()
        finally:
            conn.close()
    
    def view_results(self):
        """View student results"""
        clear_screen()
        print_header("MY RESULTS")
        
        if not self.student_info:
            print("❌ Student information not found.")
            pause()
            return
        
        name, roll_no, class_name, course_name = self.student_info
        
        print(f"\nStudent Name: {name}")
        print(f"Roll Number: {roll_no}")
        print(f"Class: {class_name}")
        print(f"Course: {course_name}")
        print_separator()
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            # Get all semesters
            cursor.execute("""
                SELECT DISTINCT semester
                FROM results
                WHERE student_id = ? AND published = 1
                ORDER BY semester
            """, (self.student_id,))
            
            semesters = cursor.fetchall()
            
            if not semesters:
                print("\n📭 No published results found.")
                pause()
                return
            
            for semester_tuple in semesters:
                semester = semester_tuple[0]
                
                print(f"\n📊 {semester}")
                print_separator()
                
                # Get results for this semester
                cursor.execute("""
                    SELECT sub.subject_name, sub.max_marks, r.marks_obtained, r.grade
                    FROM results r
                    JOIN subjects sub ON r.subject_id = sub.subject_id
                    WHERE r.student_id = ? AND r.semester = ? AND r.published = 1
                    ORDER BY sub.subject_name
                """, (self.student_id, semester))
                
                results = cursor.fetchall()
                
                if results:
                    # Calculate totals
                    total_marks = sum(r[2] for r in results)
                    total_max = sum(r[1] for r in results)
                    
                    # Display results table
                    table_data = []
                    for subject, max_marks, marks, grade in results:
                        percentage = (marks / max_marks * 100) if max_marks > 0 else 0
                        table_data.append([subject, marks, max_marks, f"{percentage:.2f}%", grade])
                    
                    headers = ["Subject", "Marks", "Max Marks", "Percentage", "Grade"]
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                    
                    # Calculate overall
                    overall_grade, overall_percentage = calculate_overall_grade(total_marks, total_max)
                    result_status = "PASS" if is_passing_grade(overall_grade) else "FAIL"
                    
                    print(f"\n{'─' * 50}")
                    print(f"Total Marks: {total_marks}/{total_max}")
                    print(f"Overall Percentage: {overall_percentage}%")
                    print(f"Overall Grade: {overall_grade} ({get_grade_description(overall_grade)})")
                    print(f"Result: {result_status} {'🎉' if result_status == 'PASS' else '❌'}")
                    print(f"{'─' * 50}")
        
        except Exception as e:
            print(f"❌ Error fetching results: {e}")
        finally:
            conn.close()
        
        pause()
    
    def download_marksheet(self):
        """Generate and save mark sheet as text file"""
        clear_screen()
        print_header("DOWNLOAD MARK SHEET")
        
        if not self.student_info:
            print("❌ Student information not found.")
            pause()
            return
        
        name, roll_no, class_name, course_name = self.student_info
        
        # Ask for semester
        semester = get_input("Enter semester to download (or press Enter for all)")
        
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed.")
            pause()
            return
        
        cursor = conn.cursor()
        
        try:
            # Get results
            if semester:
                cursor.execute("""
                    SELECT sub.subject_name, sub.max_marks, r.marks_obtained, r.grade, r.semester
                    FROM results r
                    JOIN subjects sub ON r.subject_id = sub.subject_id
                    WHERE r.student_id = ? AND r.semester = ? AND r.published = 1
                    ORDER BY sub.subject_name
                """, (self.student_id, semester))
            else:
                cursor.execute("""
                    SELECT sub.subject_name, sub.max_marks, r.marks_obtained, r.grade, r.semester
                    FROM results r
                    JOIN subjects sub ON r.subject_id = sub.subject_id
                    WHERE r.student_id = ? AND r.published = 1
                    ORDER BY r.semester, sub.subject_name
                """, (self.student_id,))
            
            results = cursor.fetchall()
            
            if not results:
                print("\n📭 No published results found.")
                pause()
                return
            
            # Generate mark sheet content
            content = []
            content.append("=" * 70)
            content.append("MARK SHEET".center(70))
            content.append("=" * 70)
            content.append("")
            content.append(f"Student Name: {name}")
            content.append(f"Roll Number: {roll_no}")
            content.append(f"Class: {class_name}")
            content.append(f"Course: {course_name}")
            content.append("-" * 70)
            
            # Group by semester
            current_semester = None
            semester_results = []
            
            for subject, max_marks, marks, grade, sem in results:
                if current_semester != sem:
                    if semester_results:
                        # Print previous semester
                        content.extend(self._format_semester_results(current_semester, semester_results))
                        semester_results = []
                    
                    current_semester = sem
                
                semester_results.append((subject, max_marks, marks, grade))
            
            # Print last semester
            if semester_results:
                content.extend(self._format_semester_results(current_semester, semester_results))
            
            content.append("=" * 70)
            content.append(f"Generated on: {get_current_timestamp()}")
            content.append("=" * 70)
            
            # Save to file
            filename = f"marksheet_{roll_no}_{semester if semester else 'all'}.txt"
            filename = filename.replace(" ", "_")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            print(f"\n✅ Mark sheet saved as: {filename}")
            print("\n📄 Mark Sheet Preview:")
            print_separator()
            print('\n'.join(content[:30]))  # Show first 30 lines
            if len(content) > 30:
                print("\n... (truncated)")
            
        except Exception as e:
            print(f"❌ Error generating mark sheet: {e}")
        finally:
            conn.close()
        
        pause()
    
    def _format_semester_results(self, semester, results):
        """Format results for a semester"""
        lines = []
        lines.append("")
        lines.append(f"SEMESTER: {semester}")
        lines.append("-" * 70)
        
        # Table header
        lines.append(f"{'Subject':<30} {'Marks':<15} {'Grade':<10} {'Percentage':<15}")
        lines.append("-" * 70)
        
        total_marks = 0
        total_max = 0
        
        for subject, max_marks, marks, grade in results:
            percentage = (marks / max_marks * 100) if max_marks > 0 else 0
            lines.append(f"{subject:<30} {marks}/{max_marks:<12} {grade:<10} {percentage:.2f}%")
            total_marks += marks
            total_max += max_marks
        
        lines.append("-" * 70)
        
        # Calculate overall
        overall_grade, overall_percentage = calculate_overall_grade(total_marks, total_max)
        result_status = "PASS" if is_passing_grade(overall_grade) else "FAIL"
        
        lines.append(f"Total: {total_marks}/{total_max}")
        lines.append(f"Overall Percentage: {overall_percentage}%")
        lines.append(f"Overall Grade: {overall_grade} ({get_grade_description(overall_grade)})")
        lines.append(f"Result: {result_status}")
        lines.append("")
        
        return lines