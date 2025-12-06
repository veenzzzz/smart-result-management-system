import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/layout/Layout'
import StudentLayout from '@/components/layout/StudentLayout'
import LoginPage from './pages/LoginPage'
import AdminDashboard from './pages/AdminDashboard'
import StudentManagement from './pages/admin/StudentManagement'
import CourseManagement from './pages/admin/CourseManagement'
import SubjectManagement from './pages/admin/SubjectManagement'
import ResultEntry from './pages/admin/ResultEntry'
import ResultView from './pages/student/ResultView'
import Reports from './pages/admin/Reports'
import Settings from './pages/Settings'

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Protected Admin/Staff Routes */}
            <Route element={
              <ProtectedRoute roles={['admin', 'staff']}>
                <Layout />
              </ProtectedRoute>
            }>
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/students" element={<StudentManagement />} />
              <Route path="/admin/courses" element={<CourseManagement />} />
              <Route path="/admin/subjects" element={<SubjectManagement />} />
              <Route path="/admin/results" element={<ResultEntry />} />
              <Route path="/admin/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/" element={<Navigate to="/admin" replace />} />
            </Route>

            {/* Protected Student Routes */}
            <Route element={
              <ProtectedRoute roles={['student']}>
                <StudentLayout />
              </ProtectedRoute>
            }>
              <Route path="/student/results" element={<ResultView />} />
              <Route path="/student" element={<Navigate to="/student/results" replace />} />
            </Route>
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </ToastProvider>
    </AuthProvider>
  )
}

export default App