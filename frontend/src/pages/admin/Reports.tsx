import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'
import { FileText, Download, Printer, X, Eye } from 'lucide-react'

type SummaryRow = { student_id: number; name: string; roll_no: string; total_marks: number; total_max: number; percentage: number; grade: string; semester: string }

type DetailedReport = {
  student: {
    name: string
    roll_no: string
    class_name: string
    course_name: string
    course_code: string
  }
  reports: Array<{
    semester: string
    subjects: Array<{
      subject_code: string
      subject_name: string
      max_marks: number
      marks_obtained: number
      grade: string
    }>
    total_marks: number
    total_max: number
    percentage: number
    grade: string
    result_status: string
  }>
}

export default function Reports() {
  const [semester, setSemester] = useState('')
  const [rows, setRows] = useState<SummaryRow[]>([])
  const [loading, setLoading] = useState(false)
  const [includeUnpublished, setIncludeUnpublished] = useState(true) // Default to true to show all results
  const [selectedStudent, setSelectedStudent] = useState<number | null>(null)
  const [detailedReport, setDetailedReport] = useState<DetailedReport | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const { success, error } = useToast()

  const fetchSummary = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (semester) params.set('semester', semester)
      if (includeUnpublished) params.set('include_unpublished', '1')
      const qs = params.toString() ? `?${params.toString()}` : ''
      const res = await api.get<SummaryRow[]>(`/reports/summary${qs}`)
      if (res.success && res.data) {
        setRows(res.data)
      } else {
        setRows([])
      }
    } catch (err) {
      setRows([])
    } finally {
      setLoading(false)
    }
  }

  const fetchDetailedReport = async (studentId: number) => {
    setLoadingDetail(true)
    try {
      const params = new URLSearchParams()
      if (semester) params.set('semester', semester)
      if (includeUnpublished) params.set('include_unpublished', '1')
      const qs = params.toString() ? `?${params.toString()}` : ''
      const res = await api.get<DetailedReport>(`/reports/student/${studentId}${qs}`)
      if (res.success && res.data) {
        setDetailedReport(res.data)
        setSelectedStudent(studentId)
      } else {
        error('Failed to load report', res.error)
      }
    } catch (err: any) {
      error('Failed to load report', err?.message || 'Network error')
    } finally {
      setLoadingDetail(false)
    }
  }

  const exportToCSV = () => {
    if (!detailedReport) return
    const report = detailedReport.reports[0]
    const lines = [
      'SMART RESULT MANAGEMENT SYSTEM',
      'Student Performance Report',
      '',
      `Student Name: ${detailedReport.student.name}`,
      `Roll No: ${detailedReport.student.roll_no}`,
      `Course: ${detailedReport.student.course_name || detailedReport.student.course_code}`,
      `Semester: ${report.semester}`,
      '',
      'Subject Code,Subject Name,Marks,Grade'
    ]
    report.subjects.forEach(s => {
      lines.push(`${s.subject_code || ''},${s.subject_name},${s.marks_obtained},${s.grade}`)
    })
    lines.push('')
    lines.push(`Total Marks: ${report.total_marks} / ${report.total_max}`)
    lines.push(`Percentage: ${report.percentage}%`)
    lines.push(`Result: ${report.result_status}`)
    lines.push(`Grade: ${report.grade}`)
    lines.push(`Report Generated On: ${new Date().toLocaleDateString('en-GB')}`)
    
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${detailedReport.student.roll_no}_${report.semester}.csv`
    a.click()
    URL.revokeObjectURL(url)
    success('Report exported to CSV')
  }

  const exportToPDF = () => {
    if (!detailedReport) return
    const printWindow = window.open('', '_blank')
    if (!printWindow) return
    
    const report = detailedReport.reports[0]
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Student Report - ${detailedReport.student.name}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .header h1 { margin: 0; font-size: 24px; }
          .header h2 { margin: 5px 0; font-size: 18px; color: #666; }
          .student-info { margin: 20px 0; }
          .student-info p { margin: 5px 0; }
          table { width: 100%; border-collapse: collapse; margin: 20px 0; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
          .summary { margin-top: 20px; padding: 15px; background-color: #f9f9f9; }
          .summary p { margin: 5px 0; }
          .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>SMART RESULT MANAGEMENT SYSTEM</h1>
          <h2>Student Performance Report</h2>
        </div>
        <div class="student-info">
          <p><strong>Student Name:</strong> ${detailedReport.student.name}</p>
          <p><strong>Roll No:</strong> ${detailedReport.student.roll_no}</p>
          <p><strong>Course:</strong> ${detailedReport.student.course_name || detailedReport.student.course_code || 'N/A'}</p>
          <p><strong>Semester:</strong> ${report.semester}</p>
        </div>
        <table>
          <thead>
            <tr>
              <th>Subject Code</th>
              <th>Subject Name</th>
              <th>Marks</th>
              <th>Grade</th>
            </tr>
          </thead>
          <tbody>
            ${report.subjects.map(s => `
              <tr>
                <td>${s.subject_code || '-'}</td>
                <td>${s.subject_name}</td>
                <td>${s.marks_obtained}</td>
                <td>${s.grade}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div class="summary">
          <p><strong>Total Marks:</strong> ${report.total_marks} / ${report.total_max}</p>
          <p><strong>Percentage:</strong> ${report.percentage}%</p>
          <p><strong>Result:</strong> ${report.result_status} ${report.result_status === 'PASS' ? '✅' : '❌'}</p>
          <p><strong>Grade:</strong> ${report.grade}</p>
        </div>
        <div class="footer">
          <p>Report Generated On: ${new Date().toLocaleDateString('en-GB')}</p>
        </div>
      </body>
      </html>
    `
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.print()
  }

  const handlePrint = () => {
    exportToPDF()
  }

  useEffect(() => { 
    fetchSummary() 
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600">Generate and view various reports</p>
        </div>
          <div className="flex items-end space-x-3">
          <div className="w-56"><Input label="Semester (optional)" value={semester} onChange={(e) => setSemester(e.target.value)} placeholder="e.g., Semester 1" /></div>
          <label className="flex items-center space-x-2 text-sm text-gray-700 bg-yellow-50 px-3 py-2 rounded border border-yellow-200">
            <input type="checkbox" className="rounded" checked={includeUnpublished} onChange={(e) => setIncludeUnpublished(e.target.checked)} />
            <span className="font-medium">Include unpublished results</span>
          </label>
          <Button onClick={fetchSummary} disabled={loading}>📊 Generate Report</Button>
        </div>
      </div>

      {detailedReport && selectedStudent ? (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Detailed Report</h3>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" onClick={exportToCSV}>
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
                <Button variant="outline" size="sm" onClick={exportToPDF}>
                  <FileText className="w-4 h-4 mr-2" />
                  Export PDF
                </Button>
                <Button variant="outline" size="sm" onClick={handlePrint}>
                  <Printer className="w-4 h-4 mr-2" />
                  Print
                </Button>
                <Button variant="outline" size="sm" onClick={() => { setDetailedReport(null); setSelectedStudent(null) }}>
                  <X className="w-4 h-4 mr-2" />
                  Close
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {detailedReport.reports.map((report, idx) => (
              <div key={idx} className="space-y-6">
                <div className="text-center border-b-2 border-gray-300 pb-4">
                  <h2 className="text-2xl font-bold">SMART RESULT MANAGEMENT SYSTEM</h2>
                  <h3 className="text-lg text-gray-600 mt-2">Student Performance Report</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-4 py-4">
                  <div>
                    <p><strong>Student Name:</strong> {detailedReport.student.name}</p>
                    <p><strong>Roll No:</strong> {detailedReport.student.roll_no}</p>
                  </div>
                  <div>
                    <p><strong>Course:</strong> {detailedReport.student.course_name || detailedReport.student.course_code || 'N/A'}</p>
                    <p><strong>Semester:</strong> {report.semester}</p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="border border-gray-300 px-4 py-2 text-left">Subject Code</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Subject Name</th>
                        <th className="border border-gray-300 px-4 py-2 text-center">Marks</th>
                        <th className="border border-gray-300 px-4 py-2 text-center">Grade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.subjects.map((subject, sIdx) => (
                        <tr key={sIdx}>
                          <td className="border border-gray-300 px-4 py-2">{subject.subject_code || '-'}</td>
                          <td className="border border-gray-300 px-4 py-2">{subject.subject_name}</td>
                          <td className="border border-gray-300 px-4 py-2 text-center">{subject.marks_obtained}</td>
                          <td className="border border-gray-300 px-4 py-2 text-center">{subject.grade}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <p><strong>Total Marks:</strong> {report.total_marks} / {report.total_max}</p>
                  <p><strong>Percentage:</strong> {report.percentage}%</p>
                  <p><strong>Result:</strong> {report.result_status} {report.result_status === 'PASS' ? '✅' : '❌'}</p>
                  <p><strong>Grade:</strong> <Badge variant={report.grade === 'F' ? 'danger' : 'success'}>{report.grade}</Badge></p>
      </div>

                <div className="text-center text-sm text-gray-500 border-t pt-4">
                  <p>Report Generated On: {new Date().toLocaleDateString('en-GB')}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : (
      <Card>
        <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
        </CardHeader>
        <CardContent>
            <div className="mb-4">
              <Button
                variant="outline"
                onClick={() => {
                  const header = ['Roll No','Name','Total','Max','Percentage','Grade','Semester']
                  const lines = [header.join(',')]
                  rows.forEach(r => {
                    lines.push([r.roll_no, r.name, r.total_marks, r.total_max, r.percentage, r.grade, r.semester].join(','))
                  })
                  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = 'report_summary.csv'
                  a.click()
                  URL.revokeObjectURL(url)
                  success('Summary exported to CSV')
                }}
                disabled={rows.length === 0}
              >
                <Download className="w-4 h-4 mr-2" />
                Export Summary CSV
              </Button>
            </div>
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
              </div>
            ) : rows.length === 0 ? (
            <div className="text-center py-8 text-gray-600">
              <p className="mb-2 font-semibold text-lg">No data available.</p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4 text-left max-w-2xl mx-auto">
                <p className="text-sm font-medium text-blue-900 mb-2">To generate reports, make sure you have:</p>
                <ul className="text-sm list-disc list-inside space-y-1 text-blue-800">
                  <li>Added students in Student Management</li>
                  <li>Added subjects in Subject Management</li>
                  <li>Entered marks for students in Result Entry page</li>
                  {!includeUnpublished && (
                    <li className="font-semibold text-red-600">⚠️ Check "Include unpublished results" above to see all results (including unpublished ones)</li>
                  )}
                  {semester && <li>Results exist for semester: <strong>{semester}</strong></li>}
                </ul>
                {includeUnpublished && (
                  <p className="text-xs text-blue-600 mt-3 italic">💡 Tip: You're currently viewing all results (published and unpublished). Uncheck the box to see only published results.</p>
                )}
              </div>
            </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Roll No</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentage</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Semester</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {rows.map((r) => (
                      <tr key={r.student_id + r.semester} className="hover:bg-gray-50">
                        <td className="px-4 py-2">{r.roll_no}</td>
                        <td className="px-4 py-2">{r.name}</td>
                        <td className="px-4 py-2">{r.total_marks}/{r.total_max}</td>
                        <td className="px-4 py-2">{r.percentage}%</td>
                        <td className="px-4 py-2"><Badge variant={r.grade === 'F' ? 'danger' : 'success'}>{r.grade}</Badge></td>
                        <td className="px-4 py-2">{r.semester || '-'}</td>
                        <td className="px-4 py-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => fetchDetailedReport(r.student_id)}
                            disabled={loadingDetail}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View Report
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </CardContent>
      </Card>
      )}
    </div>
  )
}
