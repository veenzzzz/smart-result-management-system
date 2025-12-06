import React, { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'

type Course = { id: number; course_name: string; course_code?: string; credits?: number; duration?: string; department?: string }

export default function CourseManagement() {
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [credits, setCredits] = useState('')
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(false)
  const { success, error } = useToast()
  const [department, setDepartment] = useState('')

  const fetchCourses = async () => {
    const res = await api.get<Course[]>('/courses')
    if (res.success && res.data) setCourses(res.data)
  }

  useEffect(() => {
    fetchCourses()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate inputs
    if (!name || !name.trim()) { 
      error('Missing field', 'Course Name is required')
      return 
    }
    if (!code || !code.trim()) { 
      error('Missing field', 'Course Code is required')
      return 
    }
    if (!credits || credits.trim() === '') { 
      error('Missing field', 'Credits is required')
      return 
    }
    
    const c = parseInt(credits)
    if (isNaN(c) || !Number.isFinite(c) || c <= 0) { 
      error('Invalid credits', 'Credits must be a positive number')
      return 
    }
    
    setLoading(true)
    try {
      const res = await api.post('/courses', { 
        course_name: name.trim(), 
        course_code: code.trim().toUpperCase(), 
        credits: c, 
        department: department.trim() 
      })
      
      if (res.success) {
        success('Course added successfully')
        setName('')
        setCode('')
        setCredits('')
        setDepartment('')
        fetchCourses()
      } else {
        const errorMsg = res.error || 'Unknown error occurred'
        error('Failed to add course', errorMsg)
        console.error('Course creation error:', errorMsg)
      }
    } catch (err: any) {
      const errorMsg = err?.message || err?.error || 'Network error - please check if backend is running'
      error('Failed to add course', errorMsg)
      console.error('Course creation exception:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Course Management</h1>
        <p className="text-gray-600">Manage courses and classes</p>
      </div>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">➕ Add Course</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Input label="Course Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Bachelor of Science" required />
              <Input label="Course Code" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="e.g., BSC" required />
              <Input label="Credits" type="number" value={credits} onChange={(e) => setCredits(e.target.value)} placeholder="e.g., 120" required />
              <Input label="Department" value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="e.g., Science" />
            </div>
            <Button type="submit" loading={loading}><Plus className="w-4 h-4 mr-2"/>Add Course</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Courses</h3>
        </CardHeader>
        <CardContent>
          {courses.length === 0 ? (
            <p className="text-gray-600">No courses yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Credits</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {courses.map((c) => (
                    <tr key={c.id}>
                      <td className="px-4 py-2">{c.course_name}</td>
                      <td className="px-4 py-2">{c.course_code || '-'}</td>
                      <td className="px-4 py-2">{c.credits ?? '-'}</td>
                      <td className="px-4 py-2">{c.department || '-'}</td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={async () => {
                              const course_name = prompt('Update course name', c.course_name) || c.course_name
                              const course_code = prompt('Update course code', c.course_code || '') || c.course_code
                              const credits = prompt('Update credits', String(c.credits ?? '')) || String(c.credits ?? '')
                              const department = prompt('Update department', c.department || '') || c.department
                              const res = await api.put(`/courses/${c.id}`, { course_name, course_code, credits, department })
                              if (res.success) { success('Course updated'); fetchCourses() } else { error('Failed to update course', res.error) }
                            }}
                          >Edit</Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={async () => {
                              if (!confirm('Delete this course?')) return
                              const res = await api.delete(`/courses/${c.id}`)
                              if (res.success) { success('Course deleted'); fetchCourses() } else { error('Failed to delete course', res.error) }
                            }}
                          >Delete</Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


