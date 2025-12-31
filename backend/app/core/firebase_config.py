"""
Firebase Admin SDK configuration and initialization.
"""
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage, messaging
from app.core.config import settings
import os
import json


class FirebaseService:
    """Firebase service for authentication, Firestore, and Storage"""

    def __init__(self):
        self.initialized = False
        self.db = None
        self.bucket = None
        self._initialize()

    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase credentials are provided
            firebase_creds = os.getenv("FIREBASE_CREDENTIALS")

            if firebase_creds:
                # Parse JSON credentials
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
            else:
                # Try to load from file
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    print("Firebase credentials not found. Firebase features disabled.")
                    return

            # Initialize Firebase app
            firebase_admin.initialize_app(
                cred,
                {
                    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
                },
            )

            # Get Firestore client
            self.db = firestore.client()

            # Get Storage bucket
            self.bucket = storage.bucket()

            self.initialized = True
            print("Firebase initialized successfully")

        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
            self.initialized = False

    # Authentication methods
    def create_user(self, email: str, password: str, display_name: str = None) -> dict:
        """Create a new Firebase user"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            user = auth.create_user(
                email=email, password=password, display_name=display_name
            )
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
            }
        except Exception as e:
            raise Exception(f"Failed to create Firebase user: {str(e)}")

    def verify_id_token(self, id_token: str) -> dict:
        """Verify Firebase ID token"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            raise Exception(f"Invalid token: {str(e)}")

    def get_user(self, uid: str) -> dict:
        """Get user by UID"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "email_verified": user.email_verified,
            }
        except Exception as e:
            raise Exception(f"User not found: {str(e)}")

    def delete_user(self, uid: str) -> bool:
        """Delete a Firebase user"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete user: {str(e)}")

    # Firestore methods
    def save_user_profile(self, uid: str, profile_data: dict) -> bool:
        """Save user profile to Firestore"""
        if not self.initialized:
            return False

        try:
            self.db.collection("users").document(uid).set(profile_data, merge=True)
            return True
        except Exception as e:
            print(f"Failed to save profile: {e}")
            return False

    def get_user_profile(self, uid: str) -> dict:
        """Get user profile from Firestore"""
        if not self.initialized:
            return None

        try:
            doc = self.db.collection("users").document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Failed to get profile: {e}")
            return None

    def save_panel_member_profile(self, uid: str, profile_data: dict) -> bool:
        """Save panel member profile to Firestore"""
        if not self.initialized:
            return False

        try:
            self.db.collection("panel_members").document(uid).set(
                profile_data, merge=True
            )
            return True
        except Exception as e:
            print(f"Failed to save panel profile: {e}")
            return False

    def get_panel_member_profile(self, uid: str) -> dict:
        """Get panel member profile from Firestore"""
        if not self.initialized:
            return None

        try:
            doc = self.db.collection("panel_members").document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Failed to get panel profile: {e}")
            return None

    def save_client_profile(self, uid: str, profile_data: dict) -> bool:
        """Save client profile to Firestore"""
        if not self.initialized:
            return False

        try:
            self.db.collection("clients").document(uid).set(profile_data, merge=True)
            return True
        except Exception as e:
            print(f"Failed to save client profile: {e}")
            return False

    def get_client_profile(self, uid: str) -> dict:
        """Get client profile from Firestore"""
        if not self.initialized:
            return None

        try:
            doc = self.db.collection("clients").document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Failed to get client profile: {e}")
            return None

    # Storage methods
    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        """Upload file to Firebase Storage"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def upload_from_memory(self, file_data: bytes, destination_blob_name: str, content_type: str = None) -> str:
        """Upload file from memory to Firebase Storage"""
        if not self.initialized:
            raise Exception("Firebase not initialized")

        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def delete_file(self, blob_name: str) -> bool:
        """Delete file from Firebase Storage"""
        if not self.initialized:
            return False

        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return False

    # Cloud Messaging methods
    def send_notification(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """Send push notification via FCM"""
        if not self.initialized:
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token,
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def send_multicast_notification(
        self, tokens: list, title: str, body: str, data: dict = None
    ) -> dict:
        """Send notification to multiple devices"""
        if not self.initialized:
            return {"success": 0, "failure": len(tokens)}

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                tokens=tokens,
            )
            response = messaging.send_multicast(message)
            return {"success": response.success_count, "failure": response.failure_count}
        except Exception as e:
            print(f"Failed to send multicast notification: {e}")
            return {"success": 0, "failure": len(tokens)}


# Global Firebase service instance
firebase_service = FirebaseService()
