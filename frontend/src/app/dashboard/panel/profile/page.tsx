'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi, panelApi } from '@/lib/api'
import { User } from '@/types'

export default function PanelProfile() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState({
    date_of_birth: '',
    gender: '',
    location_country: '',
    location_state: '',
    location_city: '',
    zip_code: '',
  })
  const [demographics, setDemographics] = useState({
    income: '',
    education: '',
    employment_status: '',
    marital_status: '',
    household_size: '',
    ethnicity: '',
    occupation: '',
    interests: [] as string[],
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [userRes, profileRes] = await Promise.all([
        authApi.me(),
        panelApi.getProfile().catch(() => ({ data: null })),
      ])
      setUser(userRes.data)

      if (profileRes.data) {
        setProfile({
          date_of_birth: profileRes.data.date_of_birth || '',
          gender: profileRes.data.gender || '',
          location_country: profileRes.data.location_country || '',
          location_state: profileRes.data.location_state || '',
          location_city: profileRes.data.location_city || '',
          zip_code: profileRes.data.zip_code || '',
        })
      }
    } catch (error) {
      router.push('/login')
    }
  }

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')

    try {
      // Save basic profile
      await panelApi.updateProfile(profile)

      // Save demographics
      for (const [category, value] of Object.entries(demographics)) {
        if (value && !Array.isArray(value)) {
          await panelApi.addDemographic({ category, value })
        }
      }

      setMessage('Profile updated successfully!')
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const interests = [
    'Technology', 'Fashion', 'Food & Cooking', 'Travel', 'Sports', 'Music',
    'Gaming', 'Health & Fitness', 'Books', 'Movies & TV', 'Art & Design',
    'Business', 'Finance', 'Education', 'Home & Garden', 'Pets'
  ]

  const toggleInterest = (interest: string) => {
    setDemographics(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }))
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard/panel" className="text-xl font-bold">
                PickFu Panel Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900">Panel Member Profile</h2>
          <p className="text-gray-600 mt-2">
            Complete your profile to qualify for more surveys and earn more
          </p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {message}
          </div>
        )}

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Profile Information</h3>
          </div>

          <form onSubmit={handleSaveProfile} className="p-6 space-y-8">
            {/* Basic Information */}
            <div>
              <h4 className="text-md font-semibold mb-4">Basic Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth *
                  </label>
                  <input
                    type="date"
                    value={profile.date_of_birth}
                    onChange={(e) => setProfile({ ...profile, date_of_birth: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gender *
                  </label>
                  <select
                    value={profile.gender}
                    onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non-binary">Non-binary</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Location Information */}
            <div>
              <h4 className="text-md font-semibold mb-4">Location</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Country *
                  </label>
                  <select
                    value={profile.location_country}
                    onChange={(e) => setProfile({ ...profile, location_country: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select country</option>
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="UK">United Kingdom</option>
                    <option value="AU">Australia</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State/Province *
                  </label>
                  <input
                    type="text"
                    value={profile.location_state}
                    onChange={(e) => setProfile({ ...profile, location_state: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., California"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City *
                  </label>
                  <input
                    type="text"
                    value={profile.location_city}
                    onChange={(e) => setProfile({ ...profile, location_city: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., San Francisco"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ZIP/Postal Code *
                  </label>
                  <input
                    type="text"
                    value={profile.zip_code}
                    onChange={(e) => setProfile({ ...profile, zip_code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 94102"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Demographics */}
            <div>
              <h4 className="text-md font-semibold mb-4">Demographics</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Household Income
                  </label>
                  <select
                    value={demographics.income}
                    onChange={(e) => setDemographics({ ...demographics, income: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select income range</option>
                    <option value="<25k">Less than $25,000</option>
                    <option value="25k-50k">$25,000 - $50,000</option>
                    <option value="50k-75k">$50,000 - $75,000</option>
                    <option value="75k-100k">$75,000 - $100,000</option>
                    <option value="100k-150k">$100,000 - $150,000</option>
                    <option value="150k+">$150,000+</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Education Level
                  </label>
                  <select
                    value={demographics.education}
                    onChange={(e) => setDemographics({ ...demographics, education: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select education</option>
                    <option value="high-school">High School</option>
                    <option value="some-college">Some College</option>
                    <option value="associates">Associate's Degree</option>
                    <option value="bachelors">Bachelor's Degree</option>
                    <option value="masters">Master's Degree</option>
                    <option value="doctorate">Doctorate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Employment Status
                  </label>
                  <select
                    value={demographics.employment_status}
                    onChange={(e) => setDemographics({ ...demographics, employment_status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select status</option>
                    <option value="employed-full">Employed (Full-time)</option>
                    <option value="employed-part">Employed (Part-time)</option>
                    <option value="self-employed">Self-employed</option>
                    <option value="unemployed">Unemployed</option>
                    <option value="student">Student</option>
                    <option value="retired">Retired</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marital Status
                  </label>
                  <select
                    value={demographics.marital_status}
                    onChange={(e) => setDemographics({ ...demographics, marital_status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select status</option>
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                    <option value="divorced">Divorced</option>
                    <option value="widowed">Widowed</option>
                    <option value="domestic-partnership">Domestic Partnership</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Household Size
                  </label>
                  <select
                    value={demographics.household_size}
                    onChange={(e) => setDemographics({ ...demographics, household_size: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select size</option>
                    <option value="1">1 person</option>
                    <option value="2">2 people</option>
                    <option value="3">3 people</option>
                    <option value="4">4 people</option>
                    <option value="5+">5+ people</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ethnicity
                  </label>
                  <select
                    value={demographics.ethnicity}
                    onChange={(e) => setDemographics({ ...demographics, ethnicity: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select ethnicity</option>
                    <option value="caucasian">Caucasian</option>
                    <option value="african-american">African American</option>
                    <option value="hispanic">Hispanic/Latino</option>
                    <option value="asian">Asian</option>
                    <option value="native-american">Native American</option>
                    <option value="pacific-islander">Pacific Islander</option>
                    <option value="mixed">Mixed</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Interests */}
            <div>
              <h4 className="text-md font-semibold mb-4">Interests & Hobbies</h4>
              <p className="text-sm text-gray-600 mb-4">
                Select all that apply to help us match you with relevant surveys
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {interests.map((interest) => (
                  <button
                    key={interest}
                    type="button"
                    onClick={() => toggleInterest(interest)}
                    className={`px-4 py-2 rounded-lg border-2 text-sm font-medium transition ${
                      demographics.interests.includes(interest)
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : 'bg-white border-gray-300 text-gray-700 hover:border-blue-400'
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
              <Link
                href="/dashboard/panel"
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Back to Dashboard
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
