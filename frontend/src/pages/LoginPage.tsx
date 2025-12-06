import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, Eye, EyeOff, RefreshCcw } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { api } from '@/utils/api'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [authMode, setAuthMode] = useState<'admin' | 'student'>('admin')
  const [captchaValue, setCaptchaValue] = useState('')
  const [captchaInput, setCaptchaInput] = useState('')
  const [captchaLoading, setCaptchaLoading] = useState(false)

  const { login } = useAuth()
  const { error: showError } = useToast()
  const navigate = useNavigate()
  const isStudentMode = authMode === 'student'

  useEffect(() => {
    if (isStudentMode) {
      refreshCaptcha()
    } else {
      setCaptchaValue('')
      setCaptchaInput('')
    }
  }, [isStudentMode])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.username.trim()) {
      newErrors.username = isStudentMode ? 'USN/Roll Number is required' : 'Username is required'
    }

    if (!isStudentMode && !formData.password.trim()) {
      newErrors.password = 'Password is required'
    }

    if (isStudentMode) {
      if (!captchaValue) {
        newErrors.captcha = 'Captcha not ready, please refresh'
      } else if (!captchaInput.trim()) {
        newErrors.captcha = 'Captcha is required'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const refreshCaptcha = async () => {
    setCaptchaLoading(true)
    try {
      const res = await api.get<{ captcha: string }>('/auth/captcha')
      if (res.success && res.data?.captcha) {
        setCaptchaValue(res.data.captcha)
        setCaptchaInput('')
        setErrors(prev => ({ ...prev, captcha: '' }))
      } else {
        showError('Captcha Error', res.error || 'Unable to load captcha')
      }
    } catch (err) {
      showError('Captcha Error', 'Unable to load captcha')
    } finally {
      setCaptchaLoading(false)
    }
  }

  const handleModeChange = (mode: 'admin' | 'student') => {
    setAuthMode(mode)
    setErrors({})
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    try {
      const payload = {
        username: formData.username.trim(),
        password: isStudentMode ? 'STUDENT_CAPTCHA' : formData.password,
        mode: isStudentMode ? 'student_captcha' : 'default',
        captcha: isStudentMode ? captchaInput.trim().toUpperCase() : undefined,
      }

      const loggedInUser = await login(payload)
      if (loggedInUser) {
        const destination = loggedInUser.role === 'student' ? '/student/results' : '/admin'
        navigate(destination, { replace: true })
        if (isStudentMode) {
          setCaptchaInput('')
          setCaptchaValue('')
        }
      } else {
        showError('Login Failed', 'Invalid username or password')
        if (isStudentMode) {
          refreshCaptcha()
        }
      }
    } catch (err) {
      showError('Login Failed', 'An error occurred during login')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const handleCaptchaChange = (value: string) => {
    setCaptchaInput(value.toUpperCase())
    if (errors.captcha) {
      setErrors(prev => ({ ...prev, captcha: '' }))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-primary-600 rounded-lg flex items-center justify-center">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Welcome to ResultHub
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Choose the correct portal to access your marks or manage records
          </p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex p-1 bg-gray-100 rounded-lg">
              {(['admin', 'student'] as const).map(mode => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => handleModeChange(mode)}
                  className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition ${
                    authMode === mode
                      ? 'bg-white text-primary-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {mode === 'admin' ? 'Teacher / Admin' : 'Student'}
                </button>
              ))}
            </div>
            <div className="mt-4">
              <h3 className="text-lg font-medium text-gray-900">
                {isStudentMode ? 'Student Sign In' : 'Teacher/Admin Sign In'}
              </h3>
              <p className="text-sm text-gray-600">
                {isStudentMode
                  ? 'Log in with your USN/Roll Number to view your latest marks'
                  : 'Log in with your staff credentials to manage student records'}
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <Input
                label={isStudentMode ? 'USN / Roll Number' : 'Username'}
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                error={errors.username}
                placeholder={isStudentMode ? 'e.g. 1SG20CS001' : 'Enter your username'}
                required
              />

              {isStudentMode ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Captcha</label>
                    <div className="mt-2 flex items-center space-x-3">
                      <div className="flex-1">
                        <div className="font-mono text-lg tracking-[0.4rem] px-4 py-2 bg-gray-100 border rounded-lg text-center select-none">
                          {captchaValue || '------'}
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={refreshCaptcha}
                        loading={captchaLoading}
                      >
                        <RefreshCcw className="w-4 h-4 mr-2" />
                        Refresh
                      </Button>
                    </div>
                  </div>
                  <Input
                    label="Enter Captcha"
                    name="captcha"
                    type="text"
                    value={captchaInput}
                    onChange={(e) => handleCaptchaChange(e.target.value)}
                    error={errors.captcha}
                    placeholder="Type the characters shown above"
                    maxLength={8}
                    required
                  />
                </div>
              ) : (
                <div className="relative">
                  <Input
                    label="Password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleChange}
                    error={errors.password}
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                loading={loading}
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-medium text-blue-900 mb-2">Need to know:</h4>
              {isStudentMode ? (
                <ul className="text-xs text-blue-700 space-y-1 list-disc list-inside">
                  <li>Use your registered USN/Roll Number</li>
                  <li>Complete the captcha challenge to access your marks</li>
                  <li>Results are read-only and update instantly after teachers publish</li>
                </ul>
              ) : (
                <div className="text-xs text-blue-700 space-y-1">
                  <p><strong>Admin:</strong> admin / admin123</p>
                  <p><strong>Staff:</strong> Use the credentials assigned by the system admin</p>
                  <p>All updates you make are immediately visible to students.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}