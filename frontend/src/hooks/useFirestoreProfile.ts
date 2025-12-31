'use client'

import { useState, useEffect } from 'react'
import { doc, setDoc, getDoc, onSnapshot, updateDoc } from 'firebase/firestore'
import { db } from '@/lib/firebase'

export interface PanelMemberProfile {
  id?: number
  userId?: number
  email?: string
  fullName?: string
  // Personal Details
  dateOfBirth?: string
  gender?: string
  // Location
  locationCountry?: string
  locationState?: string
  locationCity?: string
  zipCode?: string
  // Status
  isQualified?: boolean
  qualificationLevel?: number
  isSuspended?: boolean
  // Performance Metrics
  totalResponses?: number
  totalEarnings?: number
  averageQualityScore?: number
  responseRate?: number
  completionRate?: number
  // Wallet
  walletBalance?: number
  // Demographics
  demographics?: Record<string, any>
  // Qualifications
  qualifications?: any[]
  // Metadata
  joinedAt?: string
  lastActiveAt?: string
  profileCompleteness?: number
  syncedAt?: string
}

export interface ClientProfile {
  id?: number
  email?: string
  fullName?: string
  // Company Information
  companyName?: string
  industry?: string
  companySize?: string
  // Research Preferences
  researchGoals?: string
  typicalPollFrequency?: string
  budgetRange?: string
  targetDemographics?: string[]
  preferredPanelSize?: number
  notificationPreferences?: Record<string, any>
  // Metadata
  createdAt?: string
  lastLogin?: string
  syncedAt?: string
}

export function useFirestorePanelProfile(uid: string | null) {
  const [profile, setProfile] = useState<PanelMemberProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!uid) {
      setProfile(null)
      setLoading(false)
      return
    }

    // Set up real-time listener
    const unsubscribe = onSnapshot(
      doc(db, 'panel_members', `panel_${uid}`),
      (doc) => {
        if (doc.exists()) {
          setProfile(doc.data() as PanelMemberProfile)
        } else {
          setProfile(null)
        }
        setLoading(false)
      },
      (err) => {
        setError(err.message)
        setLoading(false)
      }
    )

    return () => unsubscribe()
  }, [uid])

  const updateProfile = async (updates: Partial<PanelMemberProfile>) => {
    if (!uid) throw new Error('No user ID provided')

    try {
      await updateDoc(doc(db, 'panel_members', `panel_${uid}`), {
        ...updates,
        syncedAt: new Date().toISOString(),
      })
      return true
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  const saveProfile = async (profileData: PanelMemberProfile) => {
    if (!uid) throw new Error('No user ID provided')

    try {
      await setDoc(
        doc(db, 'panel_members', `panel_${uid}`),
        {
          ...profileData,
          syncedAt: new Date().toISOString(),
        },
        { merge: true }
      )
      return true
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return {
    profile,
    loading,
    error,
    updateProfile,
    saveProfile,
  }
}

export function useFirestoreClientProfile(uid: string | null) {
  const [profile, setProfile] = useState<ClientProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!uid) {
      setProfile(null)
      setLoading(false)
      return
    }

    // Set up real-time listener
    const unsubscribe = onSnapshot(
      doc(db, 'clients', `client_${uid}`),
      (doc) => {
        if (doc.exists()) {
          setProfile(doc.data() as ClientProfile)
        } else {
          setProfile(null)
        }
        setLoading(false)
      },
      (err) => {
        setError(err.message)
        setLoading(false)
      }
    )

    return () => unsubscribe()
  }, [uid])

  const updateProfile = async (updates: Partial<ClientProfile>) => {
    if (!uid) throw new Error('No user ID provided')

    try:
      await updateDoc(doc(db, 'clients', `client_${uid}`), {
        ...updates,
        syncedAt: new Date().toISOString(),
      })
      return true
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  const saveProfile = async (profileData: ClientProfile) => {
    if (!uid) throw new Error('No user ID provided')

    try {
      await setDoc(
        doc(db, 'clients', `client_${uid}`),
        {
          ...profileData,
          syncedAt: new Date().toISOString(),
        },
        { merge: true }
      )
      return true
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return {
    profile,
    loading,
    error,
    updateProfile,
    saveProfile,
  }
}
