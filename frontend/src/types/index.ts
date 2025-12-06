// User and Authentication Types
export interface User {
  id: number;
  username: string;
  role: 'admin' | 'staff' | 'student';
  name?: string;
}

export interface LoginCredentials {
  username: string;
  password?: string;
  mode?: 'default' | 'student_captcha';
  captcha?: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  message?: string;
}

// Student Types
export interface Student {
  id: number;
  name: string;
  roll_no: string;
  class_id: number;
  class_name?: string;
  course_name?: string;
  dob: string;
  contact?: string;
}

export interface CreateStudentRequest {
  name: string;
  roll_no: string;
  class_id: number;
  dob: string;
  contact?: string;
  password: string;
}

export interface UpdateStudentRequest {
  name?: string;
  contact?: string;
}

// Course and Class Types
export interface Course {
  id: number;
  course_name: string;
  duration: string;
}

export interface Class {
  id: number;
  class_name: string;
  course_id: number;
  course_name?: string;
}

export interface CreateCourseRequest {
  course_name: string;
  duration: string;
}

export interface CreateClassRequest {
  class_name: string;
  course_id: number;
}

// Subject Types
export interface Subject {
  id: number;
  subject_name: string;
  subject_code?: string;
  class_id: number;
  class_name?: string;
  max_marks: number;
}

export interface CreateSubjectRequest {
  subject_name: string;
  subject_code?: string;
  class_id: number;
  max_marks: number;
}

// Result Types
export interface Result {
  id: number;
  student_id: number;
  subject_id: number;
  marks_obtained: number;
  grade: string;
  semester: string;
  published: boolean;
  student_name?: string;
  subject_name?: string;
  max_marks?: number;
}

export interface CreateResultRequest {
  student_id: number;
  subject_id: number;
  marks_obtained: number;
  semester: string;
}

export interface PublishResultRequest {
  semester: string;
  published: boolean;
}

// Report Types
export interface StudentReport {
  student: Student;
  results: Result[];
  overall_percentage: number;
  overall_grade: string;
  result_status: 'PASS' | 'FAIL';
}

export interface ClassReport {
  class_name: string;
  course_name: string;
  total_students: number;
  passed_students: number;
  failed_students: number;
  average_percentage: number;
  top_performers: StudentReport[];
}

export interface MeritList {
  semester: string;
  students: StudentReport[];
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Dashboard Statistics
export interface DashboardStats {
  total_students: number;
  total_classes: number;
  total_subjects: number;
  published_results: number;
  recent_activities: ActivityLog[];
}

export interface ActivityLog {
  id: number;
  user_id: number;
  username?: string;
  action: string;
  timestamp: string;
}

// Grade Calculation
export interface GradeInfo {
  grade: string;
  percentage: number;
  description: string;
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface FormState<T> {
  data: T;
  errors: FormError[];
  loading: boolean;
}

// Navigation Types
export interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: string[];
}

// Chart Data Types
export interface ChartData {
  name: string;
  value: number;
  color?: string;
}

export interface PerformanceData {
  subject: string;
  marks: number;
  maxMarks: number;
  percentage: number;
  grade: string;
}