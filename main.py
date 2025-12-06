
#!/usr/bin/env python3
"""
Online Result Tracker System
Main entry point for the application
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_setup import initialize_database, create_default_admin
from modules.auth import AuthManager
from modules.admin import AdminModule
from modules.student import StudentModule
from modules.reports import ReportModule
from utils.helpers import *

class ResultTrackerSystem:
    def __init__(self):
        self.auth = AuthManager()
        self.admin_module = AdminModule(self.auth)
        self.report_module = ReportModule(self.auth)
        self.running = True
    
    def run(self):
        """Main application loop"""
        # Initialize database
        if not initialize_database():
            print("ERROR: Failed to initialize database. Exiting...")
            return
        
        create_default_admin()
        
        while self.running:
            self.show_main_menu()
    
    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        print_header("ONLINE RESULT TRACKER SYSTEM")
        
        print("\n[1] Admin/Staff Login")
        print("[2] Student Login")
        print("[3] Exit")
        print_separator()
        
        choice = get_input("Enter your choice", int)
        
        if choice == 1:
            self.admin_login()
        elif choice == 2:
            self.student_login()
        elif choice == 3:
            self.exit_system()
        else:
            print("ERROR: Invalid choice. Please try again.")
            pause()
    
    def admin_login(self):
        """Handle admin/staff login"""
        clear_screen()
        print_header("ADMIN/STAFF LOGIN")
        
        username = get_input("Enter username")
        if not username:
            return
        
        password = get_input("Enter password")
        if not password:
            return
        
        success, message = self.auth.admin_login(username, password)
        
        if success:
            print(f"\nSUCCESS: {message}")
            pause()
            self.admin_dashboard()
        else:
            print(f"\nERROR: {message}")
            pause()
    
    def admin_dashboard(self):
        """Admin dashboard menu"""
        while self.auth.is_logged_in() and self.auth.get_current_role() in ['admin', 'staff']:
            clear_screen()
            print_header("ADMIN DASHBOARD")
            
            print("\n📚 STUDENT MANAGEMENT")
            print("  [1] Add New Student")
            print("  [2] View All Students")
            print("  [3] Edit Student")
            print("  [4] Delete Student")
            
            print("\n🏫 COURSE/CLASS MANAGEMENT")
            print("  [5] Add Course")
            print("  [6] Add Class")
            print("  [7] View Courses & Classes")
            
            print("\n📖 SUBJECT MANAGEMENT")
            print("  [8] Add Subject")
            print("  [9] View All Subjects")
            
            print("\n📊 RESULT MANAGEMENT")
            print("  [10] Enter/Update Marks")
            print("  [11] Publish/Unpublish Results")
            
            print("\n📄 REPORT GENERATION")
            print("  [12] Student Report")
            print("  [13] Class Report")
            print("  [14] Merit List")
            
            print("\n👥 USER MANAGEMENT")
            print("  [15] Create Staff Account")
            print("  [16] View Activity Logs")
            
            print("\n⚙️ SETTINGS")
            print("  [17] Change Password")
            print("  [18] Logout")
            
            print_separator()
            
            choice = get_input("Enter your choice", int)
            
            if choice == 1:
                self.admin_module.add_student()
            elif choice == 2:
                self.admin_module.view_all_students()
            elif choice == 3:
                self.admin_module.edit_student()
            elif choice == 4:
                self.admin_module.delete_student()
            elif choice == 5:
                self.admin_module.add_course()
            elif choice == 6:
                self.admin_module.add_class()
            elif choice == 7:
                self.admin_module.view_courses_and_classes()
            elif choice == 8:
                self.admin_module.add_subject()
            elif choice == 9:
                self.admin_module.view_all_subjects()
            elif choice == 10:
                self.admin_module.enter_marks()
            elif choice == 11:
                self.admin_module.publish_results()
            elif choice == 12:
                self.report_module.generate_student_report()
            elif choice == 13:
                self.report_module.generate_class_report()
            elif choice == 14:
                self.report_module.generate_merit_list()
            elif choice == 15:
                self.admin_module.create_staff_account()
            elif choice == 16:
                self.admin_module.view_activity_logs()
            elif choice == 17:
                self.change_password()
            elif choice == 18:
                self.logout()
            else:
                print("ERROR: Invalid choice. Please try again.")
                pause()
    
    def student_login(self):
        """Handle student login"""
        clear_screen()
        print_header("STUDENT LOGIN")
        
        roll_no = get_input("Enter roll number")
        if not roll_no:
            return
        
        password = get_input("Enter password")
        if not password:
            return
        
        success, message, student_id = self.auth.student_login(roll_no, password)
        
        if success:
            print(f"\nSUCCESS: {message}")
            pause()
            self.student_dashboard(student_id)
        else:
            print(f"\nERROR: {message}")
            pause()
    
    def student_dashboard(self, student_id):
        """Student dashboard menu"""
        student_module = StudentModule(student_id)
        
        while self.auth.is_logged_in() and self.auth.get_current_role() == 'student':
            clear_screen()
            print_header("STUDENT PORTAL")
            
            if student_module.student_info:
                name, roll_no, class_name, course_name = student_module.student_info
                print(f"\nName: {name}")
                print(f"Roll No: {roll_no}")
                print(f"Class: {class_name}")
                print(f"Course: {course_name}")
            
            print_separator()
            
            print("\n[1] View Results")
            print("[2] Download Mark Sheet")
            print("[3] Change Password")
            print("[4] Logout")
            
            print_separator()
            
            choice = get_input("Enter your choice", int)
            
            if choice == 1:
                student_module.view_results()
            elif choice == 2:
                student_module.download_marksheet()
            elif choice == 3:
                self.change_password()
            elif choice == 4:
                self.logout()
            else:
                print("ERROR: Invalid choice. Please try again.")
                pause()
    
    def change_password(self):
        """Change password for current user"""
        clear_screen()
        print_header("CHANGE PASSWORD")
        
        old_password = get_input("Enter current password")
        if not old_password:
            return
        
        new_password = get_input("Enter new password")
        if not new_password:
            return
        
        confirm_password = get_input("Confirm new password")
        if not confirm_password:
            return
        
        if new_password != confirm_password:
            print("ERROR: Passwords do not match.")
            pause()
            return
        
        success, message = self.auth.change_password(old_password, new_password)
        
        if success:
            print(f"\nSUCCESS: {message}")
        else:
            print(f"\nERROR: {message}")
        
        pause()
    
    def logout(self):
        """Logout current user"""
        self.auth.logout()
        print("\nSUCCESS: Logged out successfully!")
        pause()
    
    def exit_system(self):
        """Exit the application"""
        clear_screen()
        print_header("THANK YOU")
        print("\nSUCCESS: Thank you for using Online Result Tracker System!")
        print("   Goodbye!\n")
        self.running = False

def main():
    """Main entry point"""
    try:
        app = ResultTrackerSystem()
        app.run()
    except KeyboardInterrupt:
        print("\n\nWARNING: Application interrupted by user.")
        print("Exiting...")
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred: {e}")
        print("Please contact system administrator.")

if __name__ == "__main__":
    main()