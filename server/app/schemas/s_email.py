from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional
import datetime
from typing import TypeVar

from config.settings import SERVER_DOMAIN

# Email Subjects in en and de
EMAIL_SUBJECTS = {
    "delete_membership": {"en": "Membership Deletion Notification", "de": "Mitgliedschaftslöschung"},
    "delete_session": {"en": "Course/Session Deletion Notification", "de": "Kurs-/Sitzungslöschung"},
    "rescheduled_session": {"en": "Course Session Rescheduling Notification", "de": "Kurs-Sitzungsneuplanung"},
    "cancel_session_occurrence": {"en": "Course Session Cancellation Notification", "de": "Kurs-Sitzungsabsage"},
    "reinstate_session_occurrence": {
        "en": "Session Occurrence Reinstatement Notification",
        "de": "Sitzungsterminwiederherstellung",
    },
    "email_verification": {"en": "Email Verification", "de": "E-Mail-Verifizierung"},
    "two_factor_auth": {"en": "Two-Factor Authentication", "de": "Zwei-Faktor-Authentifizierung"},
    "forgot_password": {"en": "Forgot Password", "de": "Passwort vergessen"},
    "cancelled_membership": {"en": "Cancelled Membership Notification", "de": "Abgebrochene Mitgliedschaft"},
    "update_membership": {"en": "Membership Update Notification", "de": "Mitgliedschaftsaktualisierung"},
    "membership_renewal": {"en": "Membership Renewal Notification", "de": "Mitgliedschaftsverlängerung"},
    "newsletter": {"en": "Newsletter", "de": "Newsletter"},
    "welcome_email": {"en": "Welcome to Our Service!", "de": "Willkommen bei unserem Service!"},
    "password_change": {"en": "Password Change Notification", "de": "Passwortänderung"},
    "username_change": {"en": "Username Change Notification", "de": "Benutzername geändert"},
    "email_change": {"en": "Email Change Notification", "de": "E-Mail-Address geändert"},
}


# Common Base Model
class BaseEmailModel(BaseModel):
    _TEMPLATE_NAME = "base_email"
    user_name: str
    user_email: str
    language: str = "en"
    logo_url: Optional[HttpUrl] = HttpUrl(f"http://{SERVER_DOMAIN}/static/logo.png")
    current_year: Optional[int] = datetime.datetime.now().year

    def get_template_name(self) -> str:
        return self._TEMPLATE_NAME


# 1. Update Membership
class UpdateMembershipModel(BaseEmailModel):
    _TEMPLATE_NAME = "update_membership"
    membership_name: str
    club_name: str
    renewal_link: str


# 2. Delete Membership
class DeleteMembershipModel(BaseEmailModel):
    _TEMPLATE_NAME = "delete_membership"
    membership_name: str
    club_name: str


# 3. Delete Session
class DeleteSessionModel(BaseEmailModel):
    _TEMPLATE_NAME = "delete_session"
    session_title: str
    club_name: str
    session_date: str


# 4. Rescheduled Session Occurrence
class OccurrenceChange(BaseModel):
    old_date: str
    new_date: str


class RescheduledSessionModel(BaseEmailModel):
    _TEMPLATE_NAME = "rescheduled_session"
    session_title: str
    club_name: str
    occurrence_change: List[OccurrenceChange]


# 5. Cancel Session Occurrence
class CancelSessionOccurrenceModel(BaseEmailModel):
    _TEMPLATE_NAME = "cancel_session_occurrence"
    session_title: str
    club_name: str
    session_dates: List[str]


# 6. Reinstate Session Occurrence
class ReinstateSessionOccurrenceModel(BaseEmailModel):
    _TEMPLATE_NAME = "reinstate_session_occurrence"
    session_title: str
    club_name: str
    session_dates: List[str]


# 7. Email Verification
class EmailVerificationModel(BaseEmailModel):
    _TEMPLATE_NAME = "email_verification"
    verification_url: str


# 8. Two-Factor Authentication
class TwoFactorAuthModel(BaseEmailModel):
    _TEMPLATE_NAME = "two_factor_auth"
    two_fa_code: str


# 9. Forgot Password
class ForgotPasswordModel(BaseEmailModel):
    _TEMPLATE_NAME = "forgot_password"
    reset_password_url: str


# 10. Cancelled Membership with Refund Information
class CancelledMembershipModel(BaseEmailModel):
    _TEMPLATE_NAME = "cancelled_membership"
    membership_name: str
    club_name: str


# 11. Newsletter
class NewsletterModel(BaseEmailModel):
    _TEMPLATE_NAME = "newsletter"
    club_name: str
    updates: List[str]


# 12. Password Change
class PasswordChangeModel(BaseEmailModel):
    _TEMPLATE_NAME = "password_change"
    pass


# 13. Username Change
class UsernameChangeModel(BaseEmailModel):
    _TEMPLATE_NAME = "username_change"
    new_username: str


# 14. Email Change
class EmailChangeModel(BaseEmailModel):
    _TEMPLATE_NAME = "email_change"
    new_email: EmailStr


TEmail = TypeVar("TEmail", bound="BaseEmailModel")
