"""
Service to synchronize database records with Firebase Firestore.
Ensures all user profiles are backed up and accessible via Firebase.
"""
from datetime import datetime
from typing import Optional
from app.core.firebase_config import firebase_service
from app.models.user import User
from app.models.panel import PanelMember
from sqlalchemy.orm import Session


class FirebaseSync:
    """Sync service for Firebase Firestore"""

    def __init__(self):
        self.firebase = firebase_service

    def sync_user(self, user: User, firebase_uid: Optional[str] = None) -> bool:
        """
        Sync user to Firestore.

        Args:
            user: User model instance
            firebase_uid: Optional Firebase UID (if different from email-based UID)

        Returns:
            bool: True if successful
        """
        if not self.firebase.initialized:
            return False

        # Use Firebase UID or create one from user ID
        uid = firebase_uid or f"user_{user.id}"

        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, "value") else user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "synced_at": datetime.utcnow().isoformat(),
        }

        return self.firebase.save_user_profile(uid, user_data)

    def sync_panel_member(
        self, panel_member: PanelMember, user: User, firebase_uid: Optional[str] = None
    ) -> bool:
        """
        Sync panel member profile to Firestore with all fields.

        Args:
            panel_member: PanelMember model instance
            user: Associated User instance
            firebase_uid: Optional Firebase UID

        Returns:
            bool: True if successful
        """
        if not self.firebase.initialized:
            return False

        uid = firebase_uid or f"panel_{panel_member.id}"

        # Build comprehensive profile data
        profile_data = {
            # Basic Info
            "id": panel_member.id,
            "user_id": panel_member.user_id,
            "email": user.email,
            "full_name": user.full_name,
            # Personal Details
            "date_of_birth": panel_member.date_of_birth.isoformat()
            if panel_member.date_of_birth
            else None,
            "gender": panel_member.gender,
            # Location
            "location_country": panel_member.location_country,
            "location_state": panel_member.location_state,
            "location_city": panel_member.location_city,
            "zip_code": panel_member.zip_code,
            # Status
            "is_qualified": panel_member.is_qualified,
            "qualification_level": panel_member.qualification_level,
            "is_suspended": panel_member.is_suspended,
            "suspension_reason": panel_member.suspension_reason,
            # Performance Metrics
            "total_responses": panel_member.total_responses,
            "total_earnings": float(panel_member.total_earnings),
            "average_quality_score": float(panel_member.average_quality_score),
            "response_rate": float(panel_member.response_rate),
            "completion_rate": float(panel_member.completion_rate),
            # Wallet
            "wallet_balance": float(panel_member.wallet_balance),
            # Metadata
            "joined_at": panel_member.joined_at.isoformat()
            if panel_member.joined_at
            else None,
            "last_active_at": panel_member.last_active_at.isoformat()
            if panel_member.last_active_at
            else None,
            "profile_completeness": float(panel_member.profile_completeness),
            "synced_at": datetime.utcnow().isoformat(),
        }

        # Add demographics if available
        if panel_member.demographics:
            demographics = {}
            for demo in panel_member.demographics:
                demographics[demo.category] = {
                    "value": demo.value,
                    "is_verified": demo.is_verified,
                    "verified_at": demo.verified_at.isoformat()
                    if demo.verified_at
                    else None,
                }
            profile_data["demographics"] = demographics

        # Add qualifications if available
        if panel_member.qualifications:
            qualifications = []
            for qual in panel_member.qualifications:
                qualifications.append(
                    {
                        "type": qual.qualification_type,
                        "name": qual.qualification_name,
                        "is_passed": qual.is_passed,
                        "score": float(qual.score) if qual.score else None,
                        "taken_at": qual.taken_at.isoformat() if qual.taken_at else None,
                        "expires_at": qual.expires_at.isoformat()
                        if qual.expires_at
                        else None,
                    }
                )
            profile_data["qualifications"] = qualifications

        return self.firebase.save_panel_member_profile(uid, profile_data)

    def sync_client_profile(
        self, user: User, client_profile: dict, firebase_uid: Optional[str] = None
    ) -> bool:
        """
        Sync client profile to Firestore with all fields.

        Args:
            user: User instance
            client_profile: Dictionary with client-specific fields
            firebase_uid: Optional Firebase UID

        Returns:
            bool: True if successful
        """
        if not self.firebase.initialized:
            return False

        uid = firebase_uid or f"client_{user.id}"

        # Build comprehensive client profile
        profile_data = {
            # Basic Info
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            # Company Information
            "company_name": client_profile.get("company_name"),
            "industry": client_profile.get("industry"),
            "company_size": client_profile.get("company_size"),
            # Research Preferences
            "research_goals": client_profile.get("research_goals"),
            "typical_poll_frequency": client_profile.get("typical_poll_frequency"),
            "budget_range": client_profile.get("budget_range"),
            # Additional Fields
            "target_demographics": client_profile.get("target_demographics", []),
            "preferred_panel_size": client_profile.get("preferred_panel_size"),
            "notification_preferences": client_profile.get(
                "notification_preferences", {}
            ),
            # Metadata
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "synced_at": datetime.utcnow().isoformat(),
        }

        # Add poll statistics if available
        if "poll_stats" in client_profile:
            profile_data["poll_stats"] = client_profile["poll_stats"]

        return self.firebase.save_client_profile(uid, profile_data)

    def sync_poll_to_firestore(self, poll_data: dict, poll_id: int) -> bool:
        """Sync poll data to Firestore for real-time updates"""
        if not self.firebase.initialized:
            return False

        try:
            self.firebase.db.collection("polls").document(str(poll_id)).set(
                poll_data, merge=True
            )
            return True
        except Exception as e:
            print(f"Failed to sync poll: {e}")
            return False

    def sync_response_to_firestore(self, response_data: dict, response_id: int) -> bool:
        """Sync response data to Firestore"""
        if not self.firebase.initialized:
            return False

        try:
            self.firebase.db.collection("responses").document(str(response_id)).set(
                response_data, merge=True
            )
            return True
        except Exception as e:
            print(f"Failed to sync response: {e}")
            return False

    def calculate_profile_completeness(self, panel_member: PanelMember) -> float:
        """
        Calculate profile completeness percentage.

        Args:
            panel_member: PanelMember instance

        Returns:
            float: Completeness percentage (0-100)
        """
        required_fields = [
            panel_member.date_of_birth,
            panel_member.gender,
            panel_member.location_country,
            panel_member.location_state,
            panel_member.location_city,
            panel_member.zip_code,
        ]

        completed = sum(1 for field in required_fields if field)
        base_score = (completed / len(required_fields)) * 60  # 60% for basic fields

        # Additional 20% for demographics
        demo_score = 0
        if panel_member.demographics:
            demo_count = len(panel_member.demographics)
            demo_score = min(demo_count / 5 * 20, 20)  # Max 20% for 5+ demographics

        # Additional 20% for qualifications
        qual_score = 0
        if panel_member.qualifications:
            passed_quals = sum(
                1 for q in panel_member.qualifications if q.is_passed
            )
            qual_score = min(passed_quals / 3 * 20, 20)  # Max 20% for 3+ qualifications

        return min(base_score + demo_score + qual_score, 100.0)


# Global sync service instance
firebase_sync = FirebaseSync()
