import { useState, useEffect } from 'react'
import { Save } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'

import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Badge from '@/components/ui/Badge'
import { Student, Subject } from '@/types'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'
import { calculatePercentage, getGradeFromPercentage } from '@/utils/helpers'

export default function ResultEntry() {
  const [students, setStudents] = useState<Student[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null)
  const [marks, setMarks] = useState('')
  const [semester, setSemester] = useState('')
  const [loading, setLoading] = useState(true)
  const { success, error } = useToast()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [studentsRes, subjectsRes] = await Promise.all([
        api.get<Student[]>('/students'),
        api.get<Subject[]>('/subjects')
      ])

      if (studentsRes.success && studentsRes.data) {
        setStudents(studentsRes.data)
      }
      if (subjectsRes.success && subjectsRes.data) {
        setSubjects(subjectsRes.data)
      }
    } catch (err) {
      error('Failed to fetch data', 'Please try again later')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedStudent || !selectedSubject || !marks || !semester) {
      error('Please fill in all fields', 'All fields are required')
      return
    }

    const marksNum = parseInt(marks)
    if (marksNum > selectedSubject.max_marks) {
      error('Invalid marks', `Marks cannot exceed ${selectedSubject.max_marks}`)
      return
    }

    try {
      const response = await api.post('/results', {
        student_id: selectedStudent.id,
        subject_id: selectedSubject.id,
        marks_obtained: marksNum,
        semester: semester
      })

      if (response.success) {
        success('Marks entered successfully')
        setMarks('')
        setSelectedStudent(null)
        setSelectedSubject(null)
      } else {
        error('Failed to enter marks', response.error)
      }
    } catch (err) {
      error('Failed to enter marks', 'Please try again later')
    }
  }

  const calculateGrade = () => {
    if (!selectedSubject || !marks) return ''
    const percentage = calculatePercentage(parseInt(marks), selectedSubject.max_marks)
    return getGradeFromPercentage(percentage)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Result Entry</h1>
        <p className="text-gray-600">Enter and manage student marks</p>
      </div>

      {/* Entry Form */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Enter Marks</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Student
                </label>
                <select
                  className="input"
                  value={selectedStudent?.id || ''}
                  onChange={(e) => {
                    const student = students.find(s => s.id === parseInt(e.target.value))
                    setSelectedStudent(student || null)
                  }}
                  required
                >
                  <option value="">Choose a student...</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.name} ({student.roll_no})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Subject
                </label>
                <select
                  className="input"
                  value={selectedSubject?.id || ''}
                  onChange={(e) => {
                    const subject = subjects.find(s => s.id === parseInt(e.target.value))
                    setSelectedSubject(subject || null)
                  }}
                  required
                >
                  <option value="">Choose a subject...</option>
                  {subjects.map(subject => (
                    <option key={subject.id} value={subject.id}>
                      {subject.subject_name} (Max: {subject.max_marks})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Input
                  label="Marks Obtained"
                  type="number"
                  value={marks}
                  onChange={(e) => setMarks(e.target.value)}
                  placeholder="Enter marks..."
                  max={selectedSubject?.max_marks}
                  required
                />
              </div>

              <div>
                <Input
                  label="Semester"
                  value={semester}
                  onChange={(e) => setSemester(e.target.value)}
                  placeholder="e.g., Semester 1, Annual"
                  required
                />
              </div>
            </div>

            {selectedSubject && marks && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Grade Preview</h4>
                <div className="flex items-center space-x-4">
                  <span>Marks: {marks}/{selectedSubject.max_marks}</span>
                  <span>Percentage: {calculatePercentage(parseInt(marks), selectedSubject.max_marks)}%</span>
                  <Badge variant="success">{calculateGrade()}</Badge>
                </div>
              </div>
            )}

            <Button type="submit" className="w-full md:w-auto">
              <Save className="w-4 h-4 mr-2" />
              Save Marks
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Recent Entries */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Recent Entries</h3>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <p>Recent entries will appear here</p>
            <p className="text-sm">This feature will be implemented with the backend API</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
