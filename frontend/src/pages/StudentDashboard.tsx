import { useState, useEffect } from 'react'
import { GraduationCap, Award, TrendingUp, FileText } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table'
import Badge from '@/components/ui/Badge'
import { StudentReport } from '@/types'
import { api } from '@/utils/api'
import { getGradeColor } from '@/utils/helpers'

export default function StudentDashboard() {
  const [recentResults, setRecentResults] = useState<StudentReport[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStudentData()
  }, [])

  const fetchStudentData = async () => {
    try {
      const response = await api.get<StudentReport[]>('/student/recent-results')
      if (response.success && response.data) {
        setRecentResults(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch student data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const overallStats = recentResults.reduce(
    (acc, report) => {
      acc.totalSubjects += report.results.length
      acc.passedSubjects += report.results.filter(r => r.grade !== 'F').length
      acc.averagePercentage += report.overall_percentage
      return acc
    },
    { totalSubjects: 0, passedSubjects: 0, averagePercentage: 0 }
  )

  const averagePercentage = overallStats.totalSubjects > 0 
    ? Math.round(overallStats.averagePercentage / recentResults.length)
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Dashboard</h1>
        <p className="text-gray-600">View your academic performance and results</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-blue-50">
                <GraduationCap className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Subjects</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.totalSubjects}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-green-50">
                <Award className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Passed Subjects</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.passedSubjects}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-purple-50">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Percentage</p>
                <p className="text-2xl font-bold text-gray-900">{averagePercentage}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Results */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Recent Results</h3>
        </CardHeader>
        <CardContent>
          {recentResults.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Semester</TableHead>
                  <TableHead>Subjects</TableHead>
                  <TableHead>Overall Grade</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentResults.map((report, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {report.results[0]?.semester || 'N/A'}
                    </TableCell>
                    <TableCell>{report.results.length}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={report.overall_grade === 'F' ? 'danger' : 'success'}
                        className={getGradeColor(report.overall_grade)}
                      >
                        {report.overall_grade}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={report.result_status === 'PASS' ? 'success' : 'danger'}
                      >
                        {report.result_status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">No results available yet</p>
              <p className="text-sm">Results will appear here once they are published by your teachers.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-blue-600" />
                <div>
                  <h4 className="font-medium text-gray-900">View All Results</h4>
                  <p className="text-sm text-gray-600">See detailed results for all semesters</p>
                </div>
              </div>
            </div>
            <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <div className="flex items-center space-x-3">
                <TrendingUp className="h-8 w-8 text-green-600" />
                <div>
                  <h4 className="font-medium text-gray-900">Download Marksheet</h4>
                  <p className="text-sm text-gray-600">Get your official marksheet</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
