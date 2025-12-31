'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { analyticsApi, pollsApi, authApi } from '@/lib/api'
import { Poll, User } from '@/types'

export default function ClientDashboard() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [polls, setPolls] = useState<Poll[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [userRes, pollsRes, statsRes] = await Promise.all([
        authApi.me(),
        pollsApi.list(),
        analyticsApi.dashboard(),
      ])
      setUser(userRes.data)
      setPolls(pollsRes.data)
      setStats(statsRes.data)
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

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">PickFu Client Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard/client/profile"
                className="text-gray-700 hover:text-gray-900"
              >
                Profile
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
          <p className="text-gray-600 mt-2">Manage your polls and view insights</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Polls</div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {stats.total_polls}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Active Polls</div>
              <div className="mt-2 text-3xl font-bold text-blue-600">
                {stats.active_polls}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Responses</div>
              <div className="mt-2 text-3xl font-bold text-green-600">
                {stats.total_responses_collected}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-500">Total Spent</div>
              <div className="mt-2 text-3xl font-bold text-purple-600">
                ${stats.total_spent?.toFixed(2)}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mb-8">
          <Link
            href="/dashboard/client/polls/create"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
          >
            Create New Poll
          </Link>
        </div>

        {/* Polls List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Your Polls</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {polls.length === 0 ? (
              <div className="px-6 py-12 text-center text-gray-500">
                No polls yet. Create your first poll to get started!
              </div>
            ) : (
              polls.map((poll) => (
                <div key={poll.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <Link
                        href={`/dashboard/client/polls/${poll.id}`}
                        className="text-lg font-medium text-blue-600 hover:text-blue-800"
                      >
                        {poll.title}
                      </Link>
                      <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          poll.status === 'active' ? 'bg-green-100 text-green-800' :
                          poll.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                          poll.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {poll.status.toUpperCase()}
                        </span>
                        <span>{poll.response_count} / {poll.target_responses} responses</span>
                        <span>{poll.completion_rate.toFixed(1)}% completion</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">
                        Created {new Date(poll.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
