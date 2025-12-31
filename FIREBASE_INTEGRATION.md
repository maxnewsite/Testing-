# Firebase Integration Guide

This document explains the Firebase integration in the PickFu platform, including authentication, Firestore database, Firebase Storage, and Cloud Messaging.

## Overview

Firebase is integrated as a complementary service alongside PostgreSQL for:
- **Authentication**: Firebase Auth for OAuth providers (Google, Facebook, etc.)
- **Real-time Data**: Firestore for real-time profile sync
- **File Storage**: Firebase Storage as an alternative to S3
- **Push Notifications**: Firebase Cloud Messaging (FCM)

## Architecture

### Dual Database Strategy

The platform uses both PostgreSQL and Firestore:
- **PostgreSQL**: Primary database for transactional data, polls, responses
- **Firestore**: Secondary database for user profiles, real-time updates

Data flows: PostgreSQL → Sync Service → Firestore

### Why Both?

- **PostgreSQL**: ACID transactions, complex queries, analytics
- **Firestore**: Real-time sync, offline support, scalability
- **Best of both worlds**: Reliability + real-time features

## Setup Instructions

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add Project"
3. Enter project name (e.g., "pickfu-platform")
4. Enable Google Analytics (optional)
5. Create project

### 2. Enable Firebase Services

#### Authentication
1. Go to Authentication → Sign-in method
2. Enable Email/Password
3. Enable Google (optional)
4. Add authorized domains

#### Firestore Database
1. Go to Firestore Database
2. Click "Create database"
3. Choose "Start in test mode" (development) or "Start in production mode"
4. Select location (same as your app region)

#### Firebase Storage
1. Go to Storage
2. Click "Get started"
3. Choose security rules (test or production)
4. Select location

#### Cloud Messaging
1. Go to Cloud Messaging
2. Click "Get started"
3. Generate server key

### 3. Get Configuration Keys

#### For Backend (Admin SDK)

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save the JSON file as `firebase-credentials.json`
4. Add to backend directory (or set as environment variable)

#### For Frontend (Web SDK)

1. Go to Project Settings → General
2. Scroll to "Your apps"
3. Click "Add app" → Web
4. Register app and copy config

### 4. Configure Environment Variables

#### Backend (.env)

```bash
# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
# OR provide as JSON string:
FIREBASE_CREDENTIALS='{"type":"service_account","project_id":"your-project-id",...}'

FIREBASE_STORAGE_BUCKET=your-app.appspot.com
FIREBASE_DATABASE_URL=https://your-app.firebaseio.com
```

#### Frontend (.env.local)

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-app.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-app
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-app.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-ABCDEF123
```

## Firestore Collections Structure

### Users Collection
```
users/{uid}
  - id: number
  - email: string
  - full_name: string
  - role: string (client|panelist|admin)
  - is_active: boolean
  - created_at: timestamp
  - last_login: timestamp
```

### Panel Members Collection
```
panel_members/panel_{user_id}
  - id: number
  - user_id: number
  - email: string
  - full_name: string

  # Personal Details
  - date_of_birth: string
  - gender: string

  # Location
  - location_country: string
  - location_state: string
  - location_city: string
  - zip_code: string

  # Performance Metrics
  - total_responses: number
  - total_earnings: number
  - average_quality_score: number
  - wallet_balance: number

  # Demographics (map)
  - demographics: {
      income: { value: string, is_verified: boolean },
      education: { value: string, is_verified: boolean },
      ...
    }

  # Qualifications (array)
  - qualifications: [
      { type: string, name: string, is_passed: boolean, score: number }
    ]
```

### Clients Collection
```
clients/client_{user_id}
  - id: number
  - email: string
  - full_name: string

  # Company Info
  - company_name: string
  - industry: string
  - company_size: string

  # Research Preferences
  - research_goals: string
  - typical_poll_frequency: string
  - budget_range: string
  - target_demographics: array
```

### Polls Collection (for real-time updates)
```
polls/{poll_id}
  - id: number
  - title: string
  - status: string
  - response_count: number
  - target_responses: number
  - created_at: timestamp
```

## Data Sync Flow

### User Registration
1. User registers → PostgreSQL creates user record
2. Backend sync service → Firestore creates user profile
3. Frontend can now access real-time profile updates

### Profile Updates
1. Frontend updates Firestore profile (real-time)
2. Backend API webhook → PostgreSQL updates (persistent)
3. All connected clients see instant updates

### Panel Member Profile Sync
```python
# Backend example
from app.services.firebase_sync import firebase_sync

# After creating/updating panel member
firebase_sync.sync_panel_member(panel_member, user)
```

### Client Profile Sync
```python
# After updating client profile
firebase_sync.sync_client_profile(user, client_profile_dict)
```

## Frontend Usage

### Authentication

```typescript
import { useFirebaseAuth } from '@/hooks/useFirebaseAuth'

function LoginComponent() {
  const { loginWithEmail, loginWithGoogle } = useFirebaseAuth()

  // Email login
  await loginWithEmail(email, password)

  // Google login
  await loginWithGoogle()
}
```

### Profile Management

```typescript
import { useFirestorePanelProfile } from '@/hooks/useFirestoreProfile'

function PanelProfile() {
  const { profile, loading, updateProfile } = useFirestorePanelProfile(user?.uid)

  // Real-time profile updates
  console.log(profile?.walletBalance)

  // Update profile
  await updateProfile({
    gender: 'male',
    locationCountry: 'US'
  })
}
```

### File Upload

```typescript
import FirebaseStorageService from '@/lib/firebaseStorage'

// Upload image
const url = await FirebaseStorageService.uploadImage(
  file,
  'poll-images',
  (progress) => console.log(progress.progress + '%')
)

// Upload video
const videoUrl = await FirebaseStorageService.uploadVideo(
  videoFile,
  'poll-videos'
)
```

## Security Rules

### Firestore Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Users can read their own profile
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }

    // Panel members can read/write their profile
    match /panel_members/{panelId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null &&
        resource.data.user_id == request.auth.uid;
    }

    // Clients can read/write their profile
    match /clients/{clientId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null &&
        resource.data.id == request.auth.uid;
    }

    // Polls are publicly readable
    match /polls/{pollId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

### Storage Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /poll-images/{imageId} {
      allow read: if true;
      allow write: if request.auth != null &&
        request.resource.size < 10 * 1024 * 1024 &&
        request.resource.contentType.matches('image/.*');
    }

    match /poll-videos/{videoId} {
      allow read: if true;
      allow write: if request.auth != null &&
        request.resource.size < 100 * 1024 * 1024 &&
        request.resource.contentType.matches('video/.*');
    }
  }
}
```

## Push Notifications

### Backend (Send Notification)

```python
from app.core.firebase_config import firebase_service

# Send to single device
firebase_service.send_notification(
    token="device_fcm_token",
    title="New Survey Available",
    body="A survey matching your profile is ready",
    data={"poll_id": "123"}
)

# Send to multiple devices
firebase_service.send_multicast_notification(
    tokens=["token1", "token2"],
    title="Weekly Earnings Update",
    body="You earned $25 this week!"
)
```

### Frontend (Receive Notification)

```typescript
import { messaging } from '@/lib/firebase'
import { getToken, onMessage } from 'firebase/messaging'

// Request permission and get token
const token = await getToken(messaging, {
  vapidKey: 'YOUR_VAPID_KEY'
})

// Listen for messages
onMessage(messaging, (payload) => {
  console.log('Message received:', payload)
  // Show notification
})
```

## Best Practices

### 1. Sync Strategy
- Always write to PostgreSQL first (source of truth)
- Sync to Firestore asynchronously
- Handle sync failures gracefully

### 2. Real-time Updates
- Use Firestore for profile data (changes frequently)
- Keep transactional data in PostgreSQL
- Sync important updates both ways

### 3. Error Handling
- Log Firebase errors but don't fail app
- Fall back to PostgreSQL if Firebase unavailable
- Retry failed syncs with exponential backoff

### 4. Security
- Always validate on backend
- Use Firebase Security Rules
- Never expose admin credentials client-side

### 5. Cost Optimization
- Use Firebase for active users only
- Archive old data to PostgreSQL
- Set appropriate cache expiration
- Use compound queries efficiently

## Troubleshooting

### Firebase Not Initialized
- Check credentials file path
- Verify environment variables
- Check Firebase project status

### Sync Not Working
- Verify Firestore rules allow write
- Check network connectivity
- Review backend logs

### File Upload Fails
- Check Storage rules
- Verify file size limits
- Check file type restrictions

### Notifications Not Received
- Verify FCM token is valid
- Check notification permissions
- Review browser console

## Monitoring

### Firebase Console
- Authentication: Monitor user signups/logins
- Firestore: Track read/write operations
- Storage: Monitor storage usage
- Cloud Messaging: Check delivery rates

### Backend Logs
```python
# Enable Firebase logging
import logging
logging.getLogger('firebase_admin').setLevel(logging.DEBUG)
```

## Migration Guide

### Existing Users
1. Run migration script to sync existing PostgreSQL users to Firestore
2. Update user profiles with Firebase UIDs
3. Enable Firebase authentication

### Example Migration Script
```python
from app.models.user import User
from app.services.firebase_sync import firebase_sync
from sqlalchemy.orm import Session

def migrate_users_to_firebase(db: Session):
    users = db.query(User).all()
    for user in users:
        try:
            firebase_sync.sync_user(user)
            if user.panel_member:
                firebase_sync.sync_panel_member(user.panel_member, user)
        except Exception as e:
            print(f"Failed to sync user {user.id}: {e}")
```

## Support

For Firebase-specific issues:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Support](https://firebase.google.com/support)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/firebase)

For platform-specific integration:
- Check backend logs in `backend/logs/`
- Review Firestore console for data sync
- Test with Firebase Emulator Suite for development
