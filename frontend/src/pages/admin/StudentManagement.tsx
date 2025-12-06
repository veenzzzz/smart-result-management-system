import React, { useState, useEffect } from 'react'
import { Plus, Search, Edit, Trash2, Eye } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Badge from '@/components/ui/Badge'
import { Student, Class } from '@/types'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'

const generateRandomPassword = (length = 10) => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789@$#!'
  let pwd = ''
  for (let i = 0; i < length; i++) {
    pwd += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return pwd
}

export default function StudentManagement() {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const { success, error } = useToast()
  const [newStudent, setNewStudent] = useState({ name: '', roll_no: '', class_id: '', dob: '', contact: '', password: '' })
  const [saving, setSaving] = useState(false)
  const [classes, setClasses] = useState<Class[]>([])
  const [loadingClasses, setLoadingClasses] = useState(true)

  useEffect(() => {
    fetchStudents()
    fetchClasses()
  }, [])

  const fetchStudents = async () => {
    try {
      const response = await api.get<Student[]>('/students')
      if (response.success && response.data) {
        setStudents(response.data)
      }
    } catch (err) {
      error('Failed to fetch students', 'Please try again later')
    } finally {
      setLoading(false)
    }
  }

  const fetchClasses = async () => {
    try {
      const response = await api.get<Class[]>('/classes')
      if (response.success && response.data) {
        setClasses(response.data)
      }
    } catch (err) {
      error('Failed to fetch classes', 'Please try again later')
    } finally {
      setLoadingClasses(false)
    }
  }

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newStudent.name || !newStudent.roll_no || !newStudent.password || !newStudent.class_id) {
      error('Missing fields', 'Name, Roll No, Class and Password are required')
      return
    }
    setSaving(true)
    try {
      const payload: any = {
        name: newStudent.name,
        roll_no: newStudent.roll_no.toUpperCase(),
        class_id: parseInt(newStudent.class_id, 10),
        dob: newStudent.dob || '2000-01-01',
        contact: newStudent.contact || '',
        password: newStudent.password,
      }
      const res = await api.post('/students', payload)
      if (res.success) {
        success('Student added successfully')
        setShowAddForm(false)
        setNewStudent({ name: '', roll_no: '', class_id: '', dob: '', contact: '', password: '' })
        fetchStudents()
      } else {
        error('Failed to add student', res.error)
      }
    } catch (e) {
      error('Failed to add student', 'Please try again later')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this student?')) {
      return
    }

    try {
      const response = await api.delete(`/students/${id}`)
      if (response.success) {
        success('Student deleted successfully')
        fetchStudents()
      } else {
        error('Failed to delete student', response.error)
      }
    } catch (err) {
      error('Failed to delete student', 'Please try again later')
    }
  }

  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.roll_no.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Student Management</h1>
          <p className="text-gray-600">Manage student records and information</p>
        </div>
        <Button onClick={() => setShowAddForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Student
        </Button>
      </div>

      {showAddForm && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Add Student</h3>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input label="Name" value={newStudent.name} onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })} required />
                <Input label="Roll No" value={newStudent.roll_no} onChange={(e) => setNewStudent({ ...newStudent, roll_no: e.target.value.toUpperCase() })} required />
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">Class</label>
                  <select
                    className="input"
                    value={newStudent.class_id}
                    onChange={(e) => setNewStudent({ ...newStudent, class_id: e.target.value })}
                    required
                    disabled={loadingClasses}
                  >
                    <option value="">{loadingClasses ? 'Loading classes...' : 'Select a class'}</option>
                    {classes.map((cls) => (
                      <option key={cls.id} value={cls.id.toString()}>
                        {cls.class_name}{cls.course_name ? ` - ${cls.course_name}` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <Input label="DOB" type="date" value={newStudent.dob} onChange={(e) => setNewStudent({ ...newStudent, dob: e.target.value })} />
                <Input label="Contact" value={newStudent.contact} onChange={(e) => setNewStudent({ ...newStudent, contact: e.target.value })} />
                <div className="space-y-1">
                  <label className="block text-sm font-medium text-gray-700">Student Password</label>
                  <div className="flex space-x-2">
                    <Input
                      type="text"
                      value={newStudent.password}
                      onChange={(e) => setNewStudent({ ...newStudent, password: e.target.value })}
                      placeholder="Create or generate a password"
                      className="flex-1"
                      required
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setNewStudent({ ...newStudent, password: generateRandomPassword() })}
                    >
                      Generate
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500">Share this password with the student; you can update it later from Student Management if needed.</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button type="submit" loading={saving}>Save</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                  <Search className="w-4 h-4" />
                </span>
                <Input
                  placeholder="Search students by name or roll number..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Students Table */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">
            Students ({filteredStudents.length})
          </h3>
        </CardHeader>
        <CardContent>
          {filteredStudents.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Roll Number</TableHead>
                  <TableHead>Class</TableHead>
                  <TableHead>Course</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell className="font-medium">{student.name}</TableCell>
                    <TableCell>
                      <Badge variant="primary">{student.roll_no}</Badge>
                    </TableCell>
                    <TableCell>{student.class_name || 'N/A'}</TableCell>
                    <TableCell>{student.course_name || 'N/A'}</TableCell>
                    <TableCell>{student.contact || 'N/A'}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" onClick={() => alert(`${student.name} - ${student.roll_no}`)}>
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={async () => {
                            const name = prompt('Update name', student.name)
                            if (name === null) return
                            const contact = prompt('Update contact', student.contact || '')
                            if (contact === null) return
                            const res = await api.put(`/students/${student.id}`, { name, contact })
                            if (res.success) {
                              success('Student updated')
                              fetchStudents()
                            } else {
                              error('Failed to update student', res.error)
                            }
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDelete(student.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No students found</p>
              {searchTerm && (
                <p className="text-sm">Try adjusting your search terms</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


