'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { analyticsApi, responsesApi, authApi, panelApi } from '@/lib/api'
import { User } from '@/types'

export default function PanelDashboard() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [availablePolls, setAvailablePolls] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [panelProfile, setPanelProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [userRes, pollsRes, statsRes, profileRes] = await Promise.all([
        authApi.me(),
        responsesApi.available(),
        analyticsApi.dashboard(),
        panelApi.getProfile().catch(() => ({ data: null })),
      ])
      setUser(userRes.data)
      setAvailablePolls(pollsRes.data)
      setStats(statsRes.data)
      setPanelProfile(profileRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  // Redirect to profile setup if not completed
  if (!panelProfile) {
    router.push('/dashboard/panel/profile/setup')
    return null
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">PickFu Panel Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard/panel/profile"
                className="text-gray-700 hover:text-gray-900"
              >
                Profile
              </Link>
              <Link
                href="/dashboard/panel/earnings"
                className="text-gray-700 hover:text-gray-900"
              >
                Earnings
              </Link>
              <button
                onClick={() => {
                  localStorage.removeItem('access_token')
                  router.push('/login')
                }}
                className="text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.email}!
          </h2>
          <p className="text-gray-600 mt-2">
            Complete surveys and earn money for your opinions
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Earnings</div>
              <div className="mt-2 text-3xl font-bold text-green-600">
                ${stats.total_earnings?.toFixed(2) || '0.00'}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Wallet Balance</div>
              <div className="mt-2 text-3xl font-bold text-blue-600">
                ${stats.wallet_balance?.toFixed(2) || '0.00'}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Surveys Completed</div>
              <div className="mt-2 text-3xl font-bold text-purple-600">
                {stats.total_responses || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Quality Score</div>
              <div className="mt-2 text-3xl font-bold text-orange-600">
                {stats.average_quality_score?.toFixed(1) || '0.0'}
              </div>
            </div>
          </div>
        )}

        {/* Profile Completeness Alert */}
        {panelProfile && panelProfile.profile_completeness < 100 && (
          <div className="mb-8 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-1">
                <p className="text-sm text-yellow-700">
                  Your profile is {panelProfile.profile_completeness.toFixed(0)}% complete.
                  Complete your profile to qualify for more surveys!
                </p>
              </div>
              <div>
                <Link
                  href="/dashboard/panel/profile"
                  className="text-sm font-medium text-yellow-700 hover:text-yellow-600"
                >
                  Complete Profile →
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Available Surveys */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Available Surveys</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {availablePolls.length === 0 ? (
              <div className="px-6 py-12 text-center text-gray-500">
                No surveys available at the moment. Check back later!
              </div>
            ) : (
              availablePolls.map((poll) => (
                <div key={poll.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900">{poll.title}</h4>
                      <p className="mt-1 text-sm text-gray-600">{poll.description}</p>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {poll.estimated_duration_minutes} min
                        </span>
                        <span className="flex items-center text-green-600 font-medium">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          ${poll.reward?.toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <div>
                      <Link
                        href={`/dashboard/panel/surveys/${poll.id}`}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-block"
                      >
                        Start Survey
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Recent Activity</h3>
          </div>
          <div className="px-6 py-4">
            <p className="text-gray-500">Your recent survey completions will appear here.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
