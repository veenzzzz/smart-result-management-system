def calculate_grade(marks, max_marks):
    """Calculate grade based on percentage"""
    if max_marks == 0:
        return 'N/A', 0.0
    
    percentage = (marks / max_marks) * 100
    
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
    
    return grade, round(percentage, 2)

def calculate_overall_grade(total_marks, total_max_marks):
    """Calculate overall grade for all subjects"""
    return calculate_grade(total_marks, total_max_marks)

def get_grade_description(grade):
    """Get description for a grade"""
    descriptions = {
        'A+': 'Outstanding',
        'A': 'Excellent',
        'B': 'Good',
        'C': 'Average',
        'D': 'Below Average',
        'F': 'Fail'
    }
    return descriptions.get(grade, 'N/A')

def is_passing_grade(grade):
    """Check if grade is passing"""
    return grade in ['A+', 'A', 'B', 'C', 'D']