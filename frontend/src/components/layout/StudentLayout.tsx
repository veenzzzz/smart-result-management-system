import React from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import Button from '@/components/ui/Button'

export default function StudentLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user || user.role !== 'student') {
    return null
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-900">{user.name || user.username}</p>
            <p className="text-xs font-medium text-primary-600 uppercase tracking-wide">Student</p>
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl p-6">
        <Outlet />
      </main>
    </div>
  )
}

