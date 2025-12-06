import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  FileText, 
  BarChart3, 
  Settings,
  GraduationCap,
  ClipboardList
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  roles?: string[]
}

const navigation: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/admin',
    icon: LayoutDashboard,
    roles: ['admin', 'staff']
  },
  {
    label: 'Students',
    href: '/admin/students',
    icon: Users,
    roles: ['admin', 'staff']
  },
  {
    label: 'Courses',
    href: '/admin/courses',
    icon: BookOpen,
    roles: ['admin', 'staff']
  },
  {
    label: 'Subjects',
    href: '/admin/subjects',
    icon: FileText,
    roles: ['admin', 'staff']
  },
  {
    label: 'Results',
    href: '/admin/results',
    icon: ClipboardList,
    roles: ['admin', 'staff']
  },
  {
    label: 'Reports',
    href: '/admin/reports',
    icon: BarChart3,
    roles: ['admin', 'staff']
  },
  {
    label: 'My Results',
    href: '/student/results',
    icon: GraduationCap,
    roles: ['student']
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['admin', 'staff', 'student']
  }
]

export default function Sidebar() {
  const { user } = useAuth()

  const filteredNavigation = navigation.filter(item => 
    !item.roles || item.roles.includes(user?.role || '')
  )

  return (
    <aside className="w-64 bg-white shadow-sm border-r min-h-screen">
      <div className="p-6">
        <nav className="space-y-2">
          {filteredNavigation.map((item) => (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}