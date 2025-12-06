import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { api } from '@/utils/api'

interface SemesterReport {
  student: { id: number }
  results: { subject_name: string; max_marks: number; marks_obtained: number; grade: string; semester: string }[]
  overall_percentage: number
  overall_grade: string
  result_status: 'PASS' | 'FAIL'
}

export default function ResultView() {
  const [reports, setReports] = useState<SemesterReport[]>([])
  const [loading, setLoading] = useState(true)

  const fetchResults = async () => {
    setLoading(true)
    const res = await api.get<SemesterReport[]>('/student/recent-results')
    if (res.success && res.data) setReports(res.data)
    setLoading(false)
  }

  useEffect(() => {
    fetchResults()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Results</h1>
          <p className="text-gray-600">View your academic results and performance</p>
        </div>
        <Button onClick={fetchResults} disabled={loading}>
          📊 Generate Result
        </Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
        </div>
      ) : reports.length === 0 ? (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">No Published Results</h3>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">Your published results will appear here once available.</p>
          </CardContent>
        </Card>
      ) : (
        reports.map((report, idx) => (
          <Card key={idx}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Semester: {report.results[0]?.semester}</h3>
                <div className="flex items-center space-x-3">
                  <span>Total: {report.results.reduce((s, r) => s + r.marks_obtained, 0)}/
                    {report.results.reduce((s, r) => s + r.max_marks, 0)}</span>
                  <span>Percentage: {report.overall_percentage}%</span>
                  <Badge variant={report.result_status === 'PASS' ? 'success' : 'danger'}>
                    {report.overall_grade} ({report.result_status})
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marks</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {report.results.map((r, i) => (
                      <tr key={i}>
                        <td className="px-4 py-2">{r.subject_name}</td>
                        <td className="px-4 py-2">{r.marks_obtained} / {r.max_marks}</td>
                        <td className="px-4 py-2">{r.grade}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  )
}


