# 🚀 Quick Start Guide

## Installation & First Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python main.py
```

The application will automatically:
- Create the database
- Initialize all tables
- Create a default admin account

## 🔑 Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change this password immediately after first login!

## 📖 Quick Tutorial

### For Administrators

#### 1. First Login
```
[1] Admin/Staff Login
Username: admin
Password: admin123
```

#### 2. Create a Course
```
[5] Add Course
Course Name: Bachelor of Science
Duration: 4 years
```

#### 3. Create a Class
```
[6] Add Class
Course ID: 1
Class Name: 10-A
```

#### 4. Add Subjects
```
[8] Add Subject
Class ID: 1
Subject Name: Mathematics
Maximum Marks: 100
```

Repeat for other subjects (Science, English, etc.)

#### 5. Add Students
```
[1] Add New Student
Name: John Doe
Roll Number: R001
Class ID: 1
DOB: 2005-01-15
Contact: 1234567890
Password: student123
```

#### 6. Enter Marks
```
[10] Enter/Update Marks
Roll Number: R001
Subject ID: 1
Marks: 85
Semester: Semester 1
```

#### 7. Publish Results
```
[11] Publish/Unpublish Results
Semester: Semester 1
[1] Publish Results
```

### For Students

#### 1. Login
```
[2] Student Login
Roll Number: R001
Password: student123
```

#### 2. View Results
```
[1] View Results
```

#### 3. Download Mark Sheet
```
[2] Download Mark Sheet
Semester: Semester 1 (or press Enter for all)
```

## 💡 Tips

### For Admins
- Create courses and classes before adding students
- Add all subjects for a class before entering marks
- Remember to publish results after entering all marks
- Use the merit list feature to identify top performers
- Check activity logs regularly for security

### For Students
- Keep your password secure
- Download mark sheets for your records
- Contact admin if you can't see published results
- Change your password regularly

## 🎯 Common Tasks

### Change Password (Admin/Student)
```
[17] Change Password (Admin)
[3] Change Password (Student)

Current Password: ****
New Password: ****
Confirm Password: ****
```

### Create Staff Account
```
[15] Create Staff Account
Username: staff1
Password: staff123
Role: [2] Staff
```

### Generate Reports
```
[12] Student Report - Individual student performance
[13] Class Report - Class-wise analysis
[14] Merit List - Top performers
```

## ⚠️ Important Notes

1. **Roll Numbers**: Must be unique and at least 3 characters
2. **Passwords**: Minimum 6 characters
3. **Marks**: Cannot exceed maximum marks for subject
4. **Published Results**: Only published results are visible to students
5. **Data Backup**: Regularly backup the `database/result_tracker.db` file

## 🔧 Troubleshooting

### "Database connection failed"
- Check if `database` folder exists
- Ensure you have write permissions

### "Invalid username or password"
- Verify credentials are correct
- Check if account exists (admin should create student accounts)

### "No results found"
- Ensure marks have been entered
- Check if results are published
- Verify correct semester name

## 📞 Need Help?

Refer to the full README.md for detailed documentation.

---

**Happy Result Tracking! 🎓**