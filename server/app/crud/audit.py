from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from sqlalchemy.sql.expression import and_
import uuid
import datetime
from typing import Optional
import traceback
from rich.console import Console

from models.m_audit import AuthenticationLog, AuditLog, AuthMethods, ErrorLog, ErrorLevels, AuditLogCategories

from config.settings import DEFAULT_TIMEZONE, SYSTEM_USER_ID, DEBUG


###########################################################################
################################## Logger #################################
###########################################################################
class AuditLogger:
    def __init__(self, db: AsyncSession):
        self.db = db

    def log_to_audit(
        self,
        user_id: uuid.UUID,
        action: str,
        category: AuditLogCategories,
        details: Optional[str] = None,
        status: bool = True,
        is_system: bool = False,
    ) -> AuditLog:
        """Log to the audit log table.

        :param user_id: The user ID performing the action
        :param action: The action being performed
        :param category: The category of the action
        :param details: Additional details, defaults to None
        :param status: The status of the action, defaults to True
        :param is_system: Whether the action is performed by the system, defaults to False
        :return: The audit log entry
        """
        log_entry = AuditLog(
            user_id=user_id if not is_system else SYSTEM_USER_ID,
            action=action,
            category=category,
            status=status,
            details=details,
        )
        self.db.add(log_entry)
        return log_entry

    def log_to_authentication(
        self, user_id: uuid.UUID, method: AuthMethods, ip_address: str, status: bool, details: Optional[str] = None
    ) -> AuthenticationLog:
        """Log to the authentication log table.

        :param user_id: The user ID performing the authentication action
        :param method: The authentication method used
        :param ip_address: The IP address of the user
        :param status: The status of the authentication action
        :param details: Additional details about the authentication action, defaults to None
        :raises ValueError: If the authentication method is invalid
        :return: The created AuthenticationLog object
        """
        if type(method) is not AuthMethods:
            raise ValueError("Invalid authentication method")

        log_entry = AuthenticationLog(
            user_id=user_id,
            method=method,
            ip_address=ip_address,
            status=status,
            details=details,
        )
        self.db.add(log_entry)
        return log_entry

    def log_to_error(
        self,
        level: ErrorLevels,
        message: str,
        traceback: Optional[str] = None,
        correlation_id: Optional[uuid.UUID] = None,
    ) -> ErrorLog:
        """Log to the error log table.

        :param level: The error level
        :param message: The error message
        :param traceback: The traceback details, defaults to None
        :param correlation_id: The correlation ID for error tracking, defaults to None
        :raises ValueError: If the error level is invalid
        :return: The created ErrorLog object
        """
        if type(level) is not ErrorLevels:
            raise ValueError("Invalid error level")

        log_entry = ErrorLog(
            level=level,
            message=message,
            traceback=traceback,
            correlation_id=correlation_id,
        )
        self.db.add(log_entry)
        return log_entry

    # ======================================================== #
    # ======================== General ======================== #
    # ======================================================== #
    def sys_info(self, message: str, details: Optional[str] = None, status: bool = True):
        """Log a system information message.

        :param message: The information message
        :param details: Additional details about the information, defaults to None
        :param status: The status of the message, defaults to True
        """
        self.log_to_audit(SYSTEM_USER_ID, message, AuditLogCategories.SYSTEM, details, status, is_system=True)

    def sys_warning(self, message: str, details: Optional[str] = None, correlation_id: Optional[uuid.UUID] = None):
        """Log a system warning message.

        :param message: The warning message
        :param details: Additional details about the warning, defaults to None
        :param correlation_id: The correlation ID for tracking, defaults to None
        """
        self.log_to_error(ErrorLevels.WARNING, message, details, correlation_id)

    def sys_error(self, message: str, correlation_id: Optional[uuid.UUID] = None, traceback: Optional[str] = None):
        """Log a system error message.

        :param message: The error message
        :param correlation_id: The correlation ID for error tracking, defaults to None
        :param traceback: The traceback details, defaults to None
        """
        self.log_to_error(ErrorLevels.ERROR, message, traceback, correlation_id)

    def sys_critical(self, message: str, correlation_id: Optional[uuid.UUID] = None, traceback: Optional[str] = None):
        """Log a system critical message.

        :param message: The critical error message
        :param correlation_id: The correlation ID for error tracking, defaults to None
        :param traceback: The traceback details, defaults to None
        """
        self.log_to_error(ErrorLevels.CRITICAL, message, traceback, correlation_id)

    def sys_debug(self, message: str, description: Optional[str] = None):
        """Log a system debug message.

        :param message: The debug message
        :param description: Additional description about the debug message, defaults to None
        """
        if DEBUG:
            self.log_to_error(ErrorLevels.DEBUG, message, description)

    # ======================================================== #
    # ====================== JWT-Token ======================= #
    # ======================================================== #
    def token_creation(
        self, user_id: uuid.UUID, ip_address: str, application_id_hash: str, jti: uuid.UUID, log_creation: bool = False
    ):
        """Log a token creation or refresh action.

        :param user_id: The user ID for whom the token is created or refreshed
        :param ip_address: The IP address from which the request was made
        :param application_id_hash: The hashed application identifier
        :param jti: The unique token identifier
        :param log_creation: Determines if the action is token creation (True) or refresh (False), defaults to False
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.TOKEN_CREATE if log_creation else AuthMethods.TOKEN_REFRESH,
            ip_address=ip_address,
            status=True,
            details=f"Token created for application_id_hash: {application_id_hash}, jti: {jti}",
        )

    def token_refresh_failed(
        self, user_id: uuid.UUID, ip_address: str, application_id_hash: str, jti: uuid.UUID, reason: str
    ):
        """Log a token refresh failure action.

        :param user_id: The user ID whose token refresh failed
        :param ip_address: The IP address from which the refresh request was made
        :param application_id_hash: The hashed application identifier
        :param jti: The unique token identifier
        :param reason: The reason for the token refresh failure
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.TOKEN_REFRESH,
            ip_address=ip_address,
            status=False,
            details=f"Token refresh failed for application_id_hash: {application_id_hash}, jti: {jti}, reason: {reason}",
        )

    def token_revocation(self, user_id: uuid.UUID, jti: uuid.UUID, application_id_hash: str):
        """Log a token revocation action.

        :param user_id: The user ID whose token is being revoked
        :param jti: The unique token identifier
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="Token Revocation",
            category=AuditLogCategories.USER,
            details=f"Token revoked for application_id_hash: {application_id_hash}, jti: {jti}",
        )

    # ======================================================== #
    # ==================== Forgot Password =================== #
    # ======================================================== #
    def user_forgot_password(self, user_id: uuid.UUID, ip_address: str):
        """Log a forgot password action.

        :param user_id: The user ID initiating forgot password
        :param ip_address: The IP address from which the request was made
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.FORGOT_PASSWORD,
            ip_address=ip_address,
            status=True,
        )

    def user_reset_password_initiated(self, user_id: uuid.UUID):
        """Log a forgot password initiation action.

        :param user_id: The user ID initiating forgot password
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="Forgot Password Initiated",
            category=AuditLogCategories.USER,
            details="See authentication logs for more details",
        )

    def user_reset_password_failed(self, user_id: uuid.UUID, application_id_hash: str, reason: str):
        """Log a forgot password failure action.

        :param user_id: The user ID whose forgot password failed
        :param application_id_hash: The hashed application identifier
        :param reason: The reason for the forgot password failure
        """
        self.log_to_audit(
            user_id,
            action="Forgot Password Failed",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Reason: {reason}",
        )

    def user_reset_password_successful(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a forgot password success action.

        :param user_id: The user ID whose forgot password succeeded
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="Forgot Password Successful",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    # ======================================================== #
    # =================== User Login/Logout ================== #
    # ======================================================== #
    def user_login(self, user_id: uuid.UUID, ip_address: str):
        """Log a user login action.

        :param user_id: The user ID logging in
        :param ip_address: The IP address from which the login request was made
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.PASSWORD,
            ip_address=ip_address,
            status=True,
        )

    def user_login_failed(self, user_id: uuid.UUID, ip_address: str):
        """Log a user login failure action.

        :param user_id: The user ID attempting to log in
        :param ip_address: The IP address from which the failed login request was made
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.PASSWORD,
            ip_address=ip_address,
            status=False,
        )

    def user_2fa_failed(self, user_id: uuid.UUID, ip_address: str, method: AuthMethods, details: str = ""):
        """Log a user 2FA failure action.

        :param user_id: The user ID attempting 2FA
        :param ip_address: The IP address from which the failed 2FA request was made
        :param method: The 2FA method used
        """
        self.log_to_authentication(
            user_id,
            method=method,
            ip_address=ip_address,
            status=False,
            details=details if details else None,
        )

    def user_2fa_success(self, user_id: uuid.UUID, ip_address: str, method: AuthMethods):
        """Log a user 2FA success action.

        :param user_id: The user ID successfully completing 2FA
        :param ip_address: The IP address from which the successful 2FA request was made
        :param method: The 2FA method used
        """
        self.log_to_authentication(user_id, method=method, ip_address=ip_address, status=True, details="2FA")

    def user_logout(self, user_id: uuid.UUID, ip_address: str, application_id_hash: str):
        """Log a user logout action.

        :param user_id: The user ID logging out
        :param ip_address: The IP address from which the logout request was made
        """
        self.log_to_authentication(
            user_id,
            method=AuthMethods.LOGOUT,
            ip_address=ip_address,
            status=True,
            details=f"Logout for application_id_hash: {application_id_hash}",
        )

    # ======================================================== #
    # ========================== 2FA ========================= #
    # ======================================================== #
    def backup_codes_generated(self, user_id: uuid.UUID):
        """Log the generation of backup codes.

        :param user_id: The user ID for whom backup codes are generated
        """
        self.log_to_audit(
            user_id,
            action="Backup Codes Generated",
            category=AuditLogCategories.USER,
        )

    def totp_register_init(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a TOTP registration initiation action.

        :param user_id: The user ID initiating TOTP registration
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="TOTP Registration Initiated",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    def totp_register_failed(self, user_id: uuid.UUID, application_id_hash: str, reason: str):
        """Log a TOTP registration failure action.

        :param user_id: The user ID whose TOTP registration failed
        """
        self.log_to_audit(
            user_id,
            action="TOTP Registration Failed",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Reason: {reason}",
        )

    def totp_registered(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a TOTP registration completion action.

        :param user_id: The user ID completing TOTP registration
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="TOTP Registered",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    def totp_removal(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a TOTP removal action.

        :param user_id: The user ID removing TOTP
        :param application_id_hash: The hashed application identifier
        """
        self.log_to_audit(
            user_id,
            action="TOTP Removed",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    def totp_removal_failed(self, user_id: uuid.UUID, application_id_hash: str, reason: str):
        """Log a TOTP removal failure action.

        :param user_id: The user ID whose TOTP removal failed
        """
        self.log_to_audit(
            user_id,
            action="TOTP Removal Failed",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Reason: {reason}",
        )

    # ======================================================== #
    # ======================== Changes ======================= #
    # ======================================================== #
    def user_password_change(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a user password change action.

        :param user_id: The user ID changing the password
        """
        self.log_to_audit(
            user_id,
            action="Password Change",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )
    
    def user_email_change(self, user_id: uuid.UUID, application_id_hash: str, old_email_hash: str):
        """Log a user email change action.

        :param user_id: The user ID changing the email
        """
        self.log_to_audit(
            user_id,
            action="Email Change",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Old Email Hash: {old_email_hash}",
        )
    
    def user_username_change(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a user username change action.

        :param user_id: The user ID changing the username
        """
        self.log_to_audit(
            user_id,
            action="Username Change",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    def user_profile_update(self, user_id: uuid.UUID, application_id_hash: str, details: str):
        """Log a user profile update action.

        :param user_id: The user ID updating the profile
        """
        self.log_to_audit(
            user_id,
            action="Profile Update",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Details: {details}",
        )

    # ======================================================== #
    # ===================== User Deletion ==================== #
    # ======================================================== #
    def user_self_deletion_initiated(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a user self-deletion initiation action.

        :param user_id: The user ID initiating self-deletion
        :return: The created AuditLog entry
        """
        return self.log_to_audit(
            user_id,
            action="User Deletion Initiated",
            category=AuditLogCategories.USER,
            details=f"User deletion initiated by user (Application ID Hash: {application_id_hash})",
        )

    def user_self_deletion_cancelled_memberships(self, ref: uuid.UUID, user_id: uuid.UUID, count: int):
        """Log the cancellation of user memberships as part of user self-deletion.

        :param ref: A reference ID for the deletion process
        :param user_id: The user ID whose memberships are canceled
        :param count: The number of active memberships canceled
        """
        self.log_to_audit(
            user_id,
            action="User Memberships Cancellation",
            category=AuditLogCategories.USER,
            details=f"[USER] Cancelled {count} active membership subscriptions (REF: {ref})",
        )

    def user_self_deletion_anonymized(self, ref: uuid.UUID, user_id: uuid.UUID):
        """Log the anonymization of user data as part of user self-deletion.

        :param ref: A reference ID for the deletion process
        :param user_id: The user ID whose data is anonymized
        """
        self.log_to_audit(
            user_id,
            action="User Anonymized",
            category=AuditLogCategories.USER,
            details=f"[USER] User data anonymized (REF: {ref})",
        )

    def user_self_deletion_completed(self, ref: uuid.UUID, user_id: uuid.UUID):
        """Log the completion of user self-deletion.

        :param ref: A reference ID for the deletion process
        :param user_id: The user ID whose self-deletion is completed
        """
        self.log_to_audit(
            user_id,
            action="User Deletion Completed",
            category=AuditLogCategories.USER,
            details=f"[USER] User deletion completed (REF: {ref})",
        )

    def user_self_deletion_failed(self, user_id: uuid.UUID, application_id_hash: str, reason: str):
        """Log a user self-deletion failure action.

        :param user_id: The user ID whose self-deletion failed
        """
        self.log_to_audit(
            user_id,
            action="User Deletion Failed",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}, Reason: {reason}",
        )

    def user_self_deletion_successful(self, user_id: uuid.UUID, application_id_hash: str):
        """Log a user self-deletion success action.

        :param user_id: The user ID whose self-deletion succeeded
        """
        self.log_to_audit(
            user_id,
            action="User Deletion Successful",
            category=AuditLogCategories.USER,
            details=f"Application ID Hash: {application_id_hash}",
        )

    # ======================================================== #
    # ====================== User-Roles ====================== #
    # ======================================================== #
    def user_role_removed(self, issuer: uuid.UUID, user_id: uuid.UUID, role: str, reason: str = ""):
        """Log a user role removal action.

        :param issuer: The user ID or system ID that removes the role
        :param user_id: The user ID whose role is removed
        :param role: The role being removed
        :param reason: The reason for removing the role, defaults to an empty string
        """
        details = f"User {user_id} role {role} removed by {issuer}"
        if reason:
            details += f" for reason: {reason}"
        self.log_to_audit(issuer, action="User Role Removal", category=AuditLogCategories.USER, details=details)

    def user_role_assignment(self, issuer: uuid.UUID, user_id: uuid.UUID, role: str, reason: str = ""):
        """Log a user role assignment action.

        :param issuer: The user ID or system ID that assigns the role
        :param user_id: The user ID whose role is assigned
        :param role: The role being assigned
        :param reason: The reason for assigning the role, defaults to an empty string
        """
        details = f"User {user_id} role {role} assigned by {issuer}"
        if reason:
            details += f" for reason: {reason}"
        self.log_to_audit(issuer, action="User Role Assignment", category=AuditLogCategories.USER, details=details)

    # ======================================================== #
    # ====================== Club-Roles ====================== #
    # ======================================================== #
    def club_role_added(self, issuer: uuid.UUID, club_id: uuid.UUID, role_id: int):
        """Log a club role addition action.

        :param issuer: The user ID adding the role
        :param club_id: The club ID to which the role is added
        :param role_id: The ID of the role being added
        """
        self.log_to_audit(
            issuer,
            action="Club Role Added",
            category=AuditLogCategories.CLUB,
            details=f"Role {role_id} added to club {club_id}",
        )

    def club_role_updated(self, issuer: uuid.UUID, club_id: uuid.UUID, role_id: int, details: str):
        """Log a club role update action.

        :param issuer: The user ID updating the role
        :param club_id: The club ID for which the role is updated
        :param role_id: The ID of the role being updated
        :param details: The details of the role update
        """
        self.log_to_audit(
            issuer,
            action="Club Role Updated",
            category=AuditLogCategories.CLUB,
            details=f"Role {role_id} updated in club {club_id}: {details}",
        )

    def club_role_deleted(self, issuer: uuid.UUID, club_id: uuid.UUID, role_id: int):
        """Log a club role deletion action.

        :param issuer: The user ID removing the role
        :param club_id: The club ID from which the role is removed
        :param role_id: The ID of the role being removed
        """
        self.log_to_audit(
            issuer,
            action="Club Role Deleted",
            category=AuditLogCategories.CLUB,
            details=f"Role {role_id} deleted from club {club_id}",
        )


    # ======================================================== #
    # ======================= Employee ======================= #
    # ======================================================== #
    def club_employee_added(self, issuer: uuid.UUID, club_id: uuid.UUID, user_id: uuid.UUID, club_role_id: int, reason: str = ""):
        """Log a club employee addition action.

        :param issuer: The user ID assigning the role
        :param club_id: The club ID to which the role is assigned
        :param user_id: The user ID whose role is assigned
        :param club_role_id: The ID of the role being assigned
        """
        details = f"User {user_id} assigned role {club_role_id} in club {club_id}"
        if reason:
            details += f" for reason: {reason}"
        self.log_to_audit(
            issuer,
            action="Club Employee Added",
            category=AuditLogCategories.CLUB,
            details=details,
        )
       
    def club_employee_removed(self, issuer: uuid.UUID, club_id: uuid.UUID, user_id: uuid.UUID, club_role_id: int, reason: str = ""):
        """Log a club employee removal action.

        :param issuer: The user ID removing the role
        :param club_id: The club ID from which the role is removed
        :param user_id: The user ID whose role is removed
        :param club_role_id: The ID of the role being removed
        """
        details = f"User {user_id} removed role {club_role_id} in club {club_id}"
        if reason:
            details += f" for reason: {reason}"
        self.log_to_audit(
            issuer,
            action="Club Employee Removed",
            category=AuditLogCategories.CLUB,
            details=details,
        )
    
    def club_employee_updated(self, issuer: uuid.UUID, club_id: uuid.UUID, user_id: uuid.UUID, from_club_role_id: int, to_club_role_id: int, reason: str = ""):
        """Log a club employee role update action.

        :param issuer: The user ID updating the role
        :param club_id: The club ID for which the role is updated
        :param user_id: The user ID whose role is updated
        :param from_role: The role being updated from
        :param to_role: The role being updated to
        """
        details = f"User {user_id} role updated from {from_club_role_id} to {to_club_role_id} in club {club_id}"
        if reason:
            details += f" for reason: {reason}"
        self.log_to_audit(
            issuer,
            action="Club Employee Role Updated",
            category=AuditLogCategories.CLUB,
            details=details,
        )


    # ======================================================== #
    # ===================== Verification ===================== #
    # ======================================================== #
    def id_verification_submitted(self, user_id: uuid.UUID, verification_id: uuid.UUID):
        """Log an identity verification initiation action.

        :param user_id: The user ID initiating identity verification
        """
        self.log_to_audit(
            user_id,
            action="Identity Verification Submitted",
            category=AuditLogCategories.USER,
        )

    def id_verification_pending_retrieved(self, user_id: uuid.UUID):
        """Log a pending identity verification retrieval action.

        :param user_id: The user ID retrieving pending identity verifications
        """
        self.log_to_audit(
            user_id,
            action="Pending Identity Verification Retrieved",
            category=AuditLogCategories.USER,
        )

    def id_verification_retrieved(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID):
        """Log an identity verification retrieval action.

        :param from_user_id: The user ID retrieving the identity verification
        :param to_user_id: The user ID whose identity verification is retrieved
        """
        self.log_to_audit(
            from_user_id,
            action="Identity Verification Retrieved",
            category=AuditLogCategories.USER,
            details=f"Identity verification retrieved for user {to_user_id}",
        )

    def id_verification_image_retrieved(self, user_id: uuid.UUID, verification_id: uuid.UUID, image: str):
        """Log an identity verification image retrieval action.

        :param user_id: The user ID retrieving the identity verification image
        """
        self.log_to_audit(
            user_id,
            action="Identity Verification Image Retrieved",
            category=AuditLogCategories.USER,
            details=f"Identity verification image retrieved for verification {verification_id}: {image}",
        )

    def id_verification_approved(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID):
        """Log an identity verification approval action.

        :param from_user_id: The user ID approving the identity verification
        :param to_user_id: The user ID whose identity verification is approved
        """
        self.log_to_audit(
            from_user_id,
            action="Identity Verification Approved",
            category=AuditLogCategories.USER,
            details=f"Identity verification approved for user {to_user_id}",
        )

    def id_verification_rejected(self, from_user_id: uuid.UUID, to_user_id: uuid.UUID, reason: str):
        """Log an identity verification rejection action.

        :param from_user_id: The user ID rejecting the identity verification
        :param to_user_id: The user ID whose identity verification is rejected
        """
        self.log_to_audit(
            from_user_id,
            action="Identity Verification Rejected",
            category=AuditLogCategories.USER,
            details=f"Identity verification rejected for user {to_user_id}, reason: {reason}",
        )
    
    def id_verification_soft_deleted(self, user_id: uuid.UUID, verification_id: uuid.UUID):
        """Log the soft deletion of an identity verification.

        :param user_id: The user ID soft deleting the verification
        :param verification_id: The ID of the verification
        """
        self.log_to_audit(
            user_id,
            action="Identity Verification Soft Deleted",
            category=AuditLogCategories.USER,
            details=f"Soft deleted identity verification {verification_id}",
        )

    def id_verification_expired_deleted(self, since_days: int, count: int):
        """Log the deletion of expired identity verifications.

        :param since_days: The number of days since the verification expired
        :param count: The number of expired verifications deleted
        """
        self.log_to_audit(
            SYSTEM_USER_ID,
            action="Expired Identity Verifications Deleted",
            category=AuditLogCategories.SYSTEM,
            details=f"Deleted {count} expired identity verifications older than {since_days} days",
        )
    
    # ======================================================== #
    # ========================= Club ========================= #
    # ======================================================== #
    def club_created(self, user_id: uuid.UUID, club_id: uuid.UUID):
        """Log a club creation action.

        :param user_id: The user ID creating the club
        :param club_id: The ID of the created club
        """
        self.log_to_audit(
            user_id,
            action="Club Created",
            category=AuditLogCategories.CLUB,
            details=f"Created club {club_id}",
        )

    def club_updated(self, user_id: uuid.UUID, club_id: uuid.UUID, details: str):
        """Log a club update action.

        :param user_id: The user ID updating the club
        :param club_id: The ID of the updated club
        """
        self.log_to_audit(
            user_id,
            action="Club Updated",
            category=AuditLogCategories.CLUB,
            details=f"Updated club {club_id}: {details}",
        )


###########################################################################
################################## Verify #################################
###########################################################################
async def forgot_password_allowed(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Check if the user is allowed to reset their password

    :param db: The database session
    :param user: The user to check
    :return: True if the user is allowed to reset their password, False otherwise
    """
    res = await db.execute(select(AuthenticationLog).where(and_(AuthenticationLog.user_id == user_id, AuthenticationLog.method == AuthMethods.FORGOT_PASSWORD)).order_by(AuthenticationLog.timestamp.desc()).limit(1))
    last_log = res.scalars().first()
    if last_log and last_log.timestamp.replace(tzinfo=DEFAULT_TIMEZONE) > datetime.datetime.now(DEFAULT_TIMEZONE) - datetime.timedelta(minutes=5):
        return False
    return True

###########################################################################
############################## Recurring Task #############################
###########################################################################
async def anonymize_ip_addresses(db: AsyncSession, console: Console) -> bool:
    """Anonymize IP addresses older than four weeks.

    :param db: The database session
    :return: The number of rows updated, or None if an error occurs
    """
    audit_logger = AuditLogger(db)

    try:
        four_weeks_ago = datetime.datetime.now() - datetime.timedelta(weeks=4)

        audit_logger.sys_info("Anonymizing IP addresses older than four weeks")

        # Anonymize IP addresses older than four weeks
        res = await db.execute(
            update(AuthenticationLog)
            .values(ip_address="[ANONYMIZED]")
            .where(AuthenticationLog.timestamp < four_weeks_ago)
        )
        audit_logger.sys_info(f"Anonymized {res.rowcount} IP addresses")
        await db.commit()

        console.log(f"[blue][INFO][/blue]\t\tAnonymized {res.rowcount} IP addresses")

        return True
    except Exception as e:
        await db.rollback()
        audit_logger.sys_error(
            "An error occurred while anonymizing IP addresses",
            traceback=traceback.format_exc(),
        )
        await db.commit()
        console.log("[red][ERROR][/red]\t\tAn error occurred while anonymizing IP addresses")
        console.print_exception()
        return False
