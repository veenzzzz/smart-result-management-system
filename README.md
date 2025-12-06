# 🎓 Online Result Tracker System

A comprehensive command-line based result management system for educational institutions with separate modules for Admin/Staff and Students.

## ✨ Features

### Admin/Staff Module
- **Student Management**: Add, view, edit, and delete student records
- **Course/Class Management**: Create and manage courses and classes
- **Subject Management**: Add and manage subjects with maximum marks
- **Result Management**: 
  - Enter and update marks for students
  - Automated grade calculation (A+, A, B, C, D, F)
  - Publish/unpublish results
- **Report Generation**:
  - Individual student reports
  - Class-wise performance reports
  - Merit lists (top performers)
- **User Management**: Create staff accounts with role-based access
- **Security & Audit**: Activity logging and password management

### Student Module
- **Secure Login**: Login using roll number and password
- **View Results**: View semester-wise marks, grades, and percentages
- **Download Mark Sheet**: Generate and save mark sheets as text files
- **Change Password**: Update account password

## 🛠️ Technology Stack

- **Language**: Python 3.x
- **Database**: SQLite3
- **Libraries**:
  - bcrypt (password hashing)
  - tabulate (table formatting)
  - reportlab (PDF generation - optional)

## 📦 Installation

1. **Clone or download the repository**

2. **Install required dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py
```

## 🚀 Getting Started

### First Time Setup

1. Run the application - it will automatically create the database and tables
2. A default admin account is created:
   - **Username**: `admin`
   - **Password**: `admin123`
   - ⚠️ **Important**: Change this password after first login!

### Admin Workflow

1. **Login** as admin
2. **Create Courses** (e.g., "Bachelor of Science", "4 years")
3. **Create Classes** (e.g., "10-A", "12-B") and link to courses
4. **Add Subjects** (e.g., "Mathematics", max marks: 100) for each class
5. **Add Students** with roll numbers and passwords
6. **Enter Marks** for students in each subject
7. **Publish Results** to make them visible to students
8. **Generate Reports** as needed

### Student Workflow

1. **Login** using roll number and password (provided by admin)
2. **View Results** to see marks, grades, and percentages
3. **Download Mark Sheet** for record keeping

## 📊 Grade Calculation

The system automatically calculates grades based on percentage:

| Percentage | Grade | Description |
|------------|-------|-------------|
| 90-100%    | A+    | Outstanding |
| 80-89%     | A     | Excellent   |
| 70-79%     | B     | Good        |
| 60-69%     | C     | Average     |
| 50-59%     | D     | Below Average |
| Below 50%  | F     | Fail        |

## 📁 Project Structure

```
online_result_tracker/
│
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── database/
│   ├── db_setup.py        # Database initialization
│   └── result_tracker.db  # SQLite database (auto-created)
│
├── modules/
│   ├── auth.py            # Authentication logic
│   ├── admin.py           # Admin module functions
│   ├── student.py         # Student module functions
│   └── reports.py         # Report generation
│
└── utils/
    ├── helpers.py         # Utility functions
    ├── validators.py      # Input validation
    └── grade_calc.py      # Grade calculation logic
```

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Role-Based Access**: Separate access levels for admin, staff, and students
- **Activity Logging**: All admin actions are logged with timestamps
- **Input Validation**: Comprehensive validation for all user inputs
- **Published Results**: Students can only view published results

## 📝 Database Schema

### Tables
- **users**: Admin and staff accounts
- **students**: Student information and credentials
- **courses**: Course definitions
- **classes**: Class definitions linked to courses
- **subjects**: Subject definitions with max marks
- **results**: Student marks and grades
- **logs**: System activity logs

## 🎯 Usage Examples

### Adding a Student
1. Select "Add New Student" from admin menu
2. Enter student name, roll number, class, DOB, contact
3. Set a password for the student
4. Student can now login with roll number and password

### Entering Marks
1. Select "Enter/Update Marks"
2. Enter student roll number
3. Select subject
4. Enter marks obtained
5. Grade is automatically calculated and saved

### Publishing Results
1. Select "Publish/Unpublish Results"
2. Enter semester name
3. Choose to publish or unpublish
4. Students can now view published results

## 🔧 Troubleshooting

### Database Connection Issues
- Ensure the `database` directory exists
- Check file permissions for the database file

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.6 or higher

### Login Issues
- For admin: Use default credentials (admin/admin123) on first run
- For students: Ensure the student account has been created by admin

## 🌟 Future Enhancements

- Web-based interface using Flask/Django
- Email notifications for result publication
- Performance graphs and charts
- Export to Excel/CSV
- Attendance tracking
- Mobile app support

## 📄 License

This project is created for educational purposes.

## 👥 Support

For issues or questions, please refer to the documentation or contact your system administrator.

---

**Made with ❤️ for educational institutions**