import React, { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { api } from '@/utils/api'
import { useToast } from '@/contexts/ToastContext'

export default function Settings() {
  const { success, error } = useToast()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (localStorage.getItem('theme') as any) || 'light')
  const [instName, setInstName] = useState(localStorage.getItem('inst_name') || '')
  const [instAddress, setInstAddress] = useState(localStorage.getItem('inst_address') || '')
  const [instWebsite, setInstWebsite] = useState(localStorage.getItem('inst_website') || '')
  const [grading, setGrading] = useState<'LETTER' | 'PERCENT' | 'CGPA'>(() => (localStorage.getItem('grading') as any) || 'LETTER')
  const [passing, setPassing] = useState<number>(() => parseInt(localStorage.getItem('passing') || '40'))
  const [notifyStudentAdded, setNotifyStudentAdded] = useState(localStorage.getItem('notify_student_added') === '1')
  const [notifyResultPublished, setNotifyResultPublished] = useState(localStorage.getItem('notify_result_published') === '1')
  const [notifyCourseUpdates, setNotifyCourseUpdates] = useState(localStorage.getItem('notify_course_updates') === '1')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.put('/user/profile', { name, email })
      if (res.success) success('Profile saved')
      else error('Failed to save profile', res.error)
    } catch (e) {
      error('Failed to save profile')
    }
  }

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!password) return
    try {
      const res = await api.post('/auth/change-password', { new_password: password })
      if (res.success) { success('Password changed'); setPassword('') }
      else error('Failed to change password', res.error)
    } catch (e) {
      error('Failed to change password')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Profile Management</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={saveProfile} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
              <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <Button type="submit">Save Profile</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Theme Customization</h3>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input type="radio" name="theme" checked={theme==='light'} onChange={() => setTheme('light')} />
              <span>Light</span>
            </label>
            <label className="flex items-center space-x-2">
              <input type="radio" name="theme" checked={theme==='dark'} onChange={() => setTheme('dark')} />
              <span>Dark</span>
            </label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Institute Information</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={(e) => {
            e.preventDefault()
            localStorage.setItem('inst_name', instName)
            localStorage.setItem('inst_address', instAddress)
            localStorage.setItem('inst_website', instWebsite)
            success('Institute info saved')
          }} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Institute Name" value={instName} onChange={(e) => setInstName(e.target.value)} placeholder="Your institute" />
              <Input label="Website" value={instWebsite} onChange={(e) => setInstWebsite(e.target.value)} placeholder="https://example.edu" />
              <div className="md:col-span-2">
                <Input label="Address" value={instAddress} onChange={(e) => setInstAddress(e.target.value)} placeholder="Street, City, State" />
              </div>
            </div>
            <Button type="submit">Save Institute Info</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Academic Configuration</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={(e) => {
            e.preventDefault()
            localStorage.setItem('grading', grading)
            localStorage.setItem('passing', String(passing))
            success('Academic settings saved')
          }} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Grading System</label>
                <select className="input" value={grading} onChange={(e) => setGrading(e.target.value as any)}>
                  <option value="LETTER">A/B/C</option>
                  <option value="PERCENT">Percentage</option>
                  <option value="CGPA">CGPA</option>
                </select>
              </div>
              <Input label="Passing Criteria (%)" type="number" value={String(passing)} onChange={(e) => setPassing(parseInt(e.target.value || '0'))} />
            </div>
            <Button type="submit">Save Academic Settings</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={(e) => {
            e.preventDefault()
            localStorage.setItem('notify_student_added', notifyStudentAdded ? '1' : '0')
            localStorage.setItem('notify_result_published', notifyResultPublished ? '1' : '0')
            localStorage.setItem('notify_course_updates', notifyCourseUpdates ? '1' : '0')
            success('Notification preferences saved')
          }} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className="flex items-center space-x-2"><input type="checkbox" checked={notifyStudentAdded} onChange={(e) => setNotifyStudentAdded(e.target.checked)} /><span>Student added</span></label>
              <label className="flex items-center space-x-2"><input type="checkbox" checked={notifyResultPublished} onChange={(e) => setNotifyResultPublished(e.target.checked)} /><span>Result published</span></label>
              <label className="flex items-center space-x-2"><input type="checkbox" checked={notifyCourseUpdates} onChange={(e) => setNotifyCourseUpdates(e.target.checked)} /><span>Course updates</span></label>
            </div>
            <Button type="submit">Save Notification Settings</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Backup & Restore</h3>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-3">
            <Button variant="outline" onClick={() => {
              const settings = {
                theme,
                inst_name: instName,
                inst_address: instAddress,
                inst_website: instWebsite,
                grading,
                passing,
                notify_student_added: notifyStudentAdded,
                notify_result_published: notifyResultPublished,
                notify_course_updates: notifyCourseUpdates,
              }
              const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = 'settings-backup.json'
              a.click()
              URL.revokeObjectURL(url)
            }}>Export Settings</Button>
            <label className="inline-flex items-center space-x-2">
              <input type="file" accept="application/json" onChange={(e) => {
                const file = e.target.files?.[0]
                if (!file) return
                const reader = new FileReader()
                reader.onload = () => {
                  try {
                    const data = JSON.parse(String(reader.result))
                    if (data.theme) { setTheme(data.theme) }
                    if (typeof data.inst_name === 'string') setInstName(data.inst_name)
                    if (typeof data.inst_address === 'string') setInstAddress(data.inst_address)
                    if (typeof data.inst_website === 'string') setInstWebsite(data.inst_website)
                    if (data.grading) setGrading(data.grading)
                    if (data.passing) setPassing(parseInt(String(data.passing)))
                    setNotifyStudentAdded(!!data.notify_student_added)
                    setNotifyResultPublished(!!data.notify_result_published)
                    setNotifyCourseUpdates(!!data.notify_course_updates)
                    success('Settings imported (not yet saved)')
                  } catch {
                    error('Invalid settings file')
                  }
                }
                reader.readAsText(file)
              }} />
              <span>Import Settings</span>
            </label>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Account Security</h3>
        </CardHeader>
        <CardContent>
          <form onSubmit={changePassword} className="space-y-4">
            <Input label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <div>
              <Button type="submit">Change Password</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}


