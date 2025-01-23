from calendar import c
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
import uuid
import datetime
from typing import Optional
import traceback

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

    def user_role_removal(self, issuer: uuid.UUID, user_id: uuid.UUID, role: str, reason: str = ""):
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
    # ====================== User Login ====================== #
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
            details= details if details else None,
        )

    # ======================================================== #
    # ===================== User Deletion ==================== #
    # ======================================================== #
    def user_self_deletion_initiated(self, user_id: uuid.UUID) -> AuditLog:
        """Log a user self-deletion initiation action.

        :param user_id: The user ID initiating self-deletion
        :return: The created AuditLog entry
        """
        return self.log_to_audit(
            user_id,
            action="User Deletion Initiated",
            category=AuditLogCategories.USER,
            details=f"[USER] User deletion initiated by user",
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


###########################################################################
############################## Recurring Task #############################
###########################################################################
async def anonymize_ip_addresses(db: AsyncSession) -> Optional[int]:
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

        await db.flush()
        return res.rowcount
    except Exception as e:
        audit_logger.sys_error(
            "An error occurred while anonymizing IP addresses",
            traceback=traceback.format_exc(),
        )
