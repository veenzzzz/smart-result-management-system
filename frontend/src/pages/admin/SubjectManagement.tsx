import React, { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { Subject } from '@/types'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'

export default function SubjectManagement() {
  const [subjectName, setSubjectName] = useState('')
  const [subjectCode, setSubjectCode] = useState('')
  const [maxMarks, setMaxMarks] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const { success, error } = useToast()

  const fetchSubjects = async () => {
    const res = await api.get<Subject[]>('/subjects')
    if (res.success && res.data) setSubjects(res.data)
  }

  useEffect(() => {
    fetchSubjects()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!subjectName || !maxMarks) {
      error('Please fill required fields', 'Subject Name and Marks are required')
      return
    }
    const marksNum = parseInt(maxMarks)
    if (Number.isNaN(marksNum) || marksNum <= 0) {
      error('Invalid marks', 'Marks must be a positive number')
      return
    }
    setSubmitting(true)
    const payload: any = {
      subject_name: subjectName,
      max_marks: marksNum,
    }
    if (subjectCode) payload.subject_code = subjectCode
    try {
      const res = await api.post('/subjects', payload)
      if (res.success) {
        success('Subject added successfully')
        setSubjectName('')
        setSubjectCode('')
        setMaxMarks('')
        fetchSubjects()
      } else {
        error('Failed to add subject', res.error)
      }
    } catch (e) {
      error('Failed to add subject', 'Please try again later')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Subject Management</h1>
        <p className="text-gray-600">Manage subjects and maximum marks</p>
      </div>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">➕ Add Subject</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Input
                label="Subject Name"
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
                placeholder="e.g., Mathematics"
                required
              />
              <Input
                label="Subject Code"
                value={subjectCode}
                onChange={(e) => setSubjectCode(e.target.value.toUpperCase())}
                placeholder="e.g., MATH101"
              />
              <Input
                label="Marks"
                type="number"
                value={maxMarks}
                onChange={(e) => setMaxMarks(e.target.value)}
                placeholder="e.g., 100"
                required
              />
            </div>
            <Button type="submit" loading={submitting}>
              <Plus className="w-4 h-4 mr-2" />
              Add Subject
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Subjects</h3>
        </CardHeader>
        <CardContent>
          {subjects.length === 0 ? (
            <p className="text-gray-600">No subjects yet. Add your first subject above.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Max Marks</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {subjects.map((s) => (
                    <tr key={s.id}>
                      <td className="px-4 py-2">{s.subject_name}</td>
                      <td className="px-4 py-2">{s.subject_code || '-'}</td>
                      <td className="px-4 py-2">{s.max_marks}</td>
                      <td className="px-4 py-2">{s.class_name || '-'}</td>
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


