import datetime
import uuid
import re
from urllib.parse import urlencode
from fastapi import status
from fastapi.testclient import TestClient
from pathlib import Path
import pyotp
import time
from typing import Optional, List, Tuple
import os
import random
import warnings
from abc import abstractmethod

from config.permissions import DEFAULT_CLUB_ROLES, ClubPermissions  # type: ignore
from .enums import PriceType, SessionType, ProgramStatusPublic, Weekday, OccurrenceStatus


###########################################################################
################################### User ##################################
###########################################################################
class TestUser:
    __test__ = False

    def __init__(self, client: TestClient):
        self.client = client
        self.capsys = None

        # User
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + os.urandom(4).hex()
        self.username = f"testuser_{timestamp}"
        self.email = f"test.user+{timestamp}@example.com"
        self.password = f"password_{timestamp}"
        self.first_name = "Test"
        self.last_name = "User"

        self.user_id = None
        self.tokens = None

        # Security
        self.application_id = uuid.uuid4().hex

        # TOTP
        self.totp_secret = None
        self.last_totp_code = None

    # ======================================================== #
    # =================== GET Terminal AUTH ================== #
    # ======================================================== #
    @staticmethod
    def __get_email_code(capsys):
        captured = capsys.readouterr()

        match = re.search(r"Email code:\s*(\d+)", captured.out)
        assert match, "Email code not found in captured output"

        code = match.group(1)
        return code

    @staticmethod
    def __get_verify_token(capsys):
        # Capture standard output
        captured = capsys.readouterr()

        # Define the regex pattern to extract user_uuid, expires, and signature
        pattern = r"user_id=([\w-]+)&expires=(\d+)&signature=([\w-]+)"

        # Search for the pattern in captured output
        match = re.search(pattern, captured.out)
        assert match, "Authentication token not found!"

        # Extracted components
        user_id, expires, signature = match.groups()

        return urlencode({"user_id": user_id, "expires": expires, "signature": signature})

    # ======================================================== #
    # ========================= Basic ======================== #
    # ======================================================== #
    def set_capsys(self, capsys):
        self.capsys = capsys

    def verify_email(self):
        querry = TestUser.__get_verify_token(self.capsys)

        response = self.client.post(
            f"/api/v1/verification/verify_email?{querry}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

    def register_user(self):
        test_user_data = {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

        response = self.client.post("/api/v1/user/register", json={**test_user_data, "address": None})
        if response.status_code == 400 and "already exists" in response.json()["detail"]:
            return

        assert response.status_code == status.HTTP_200_OK, response.json()
        self.user_id = response.json()["message"]
        self.verify_email()

    def login_email(self):
        if self.tokens:
            return

        retries = 0
        login_response = None
        while retries < 30:
            login_response = self.client.post(
                "/api/v1/auth/login",
                headers={"application-id": self.application_id},
                json={"ident": self.email, "password": self.password},
            )

            if login_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                retries += 1
                time.sleep(1)
                continue
            break

        assert login_response is not None, "Login failed"
        assert login_response.status_code == status.HTTP_200_OK, login_response.json()
        security_token = login_response.json()["security_token"]

        code = TestUser.__get_email_code(self.capsys)

        # Verify 2FA- Email
        verify_response = self.client.post(
            "/api/v1/auth/verify-code-2fa",
            headers={"Authorization": f"Bearer {security_token}", "application-id": self.application_id},
            json={"code": code, "is_totp": False},
        )
        assert verify_response.status_code == status.HTTP_200_OK, login_response.json()
        tokens = verify_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        self.tokens = tokens

    def login_totp(self):
        if not self.totp_secret:
            raise Exception("TOTP secret not set")

        login_response = self.client.post(
            "/api/v1/auth/login",
            headers={"application-id": self.application_id},
            json={"ident": self.email, "password": self.password},
        )
        assert login_response.status_code == status.HTTP_200_OK, login_response.json()
        security_token = login_response.json()["security_token"]

        totp = pyotp.TOTP(self.totp_secret)
        code = totp.now()
        print("\nCode already used, generating new code...", end="")
        while code == self.last_totp_code:
            code = totp.now()
            time.sleep(5)
            print(".", end="")
        print()

        self.last_totp_code = code

        # Verify 2FA- TOTP
        verify_response = self.client.post(
            "/api/v1/auth/verify-code-2fa",
            headers={"Authorization": f"Bearer {security_token}", "application-id": self.application_id},
            json={"code": code, "is_totp": True},
        )
        assert verify_response.status_code == status.HTTP_200_OK, verify_response.json()
        tokens = verify_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

        self.tokens = tokens

    def logout(self):
        if not self.tokens:
            return
        self.client.delete(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {self.tokens['access_token']}", "application-id": self.application_id},
        )
        self.tokens = None

    def __request(
        self, method: str, path: str, params: Optional[dict] = None, json: Optional[dict] = None, check_status=True
    ):
        if not self.tokens:
            self.login_email()

        response = self.client.request(
            method,
            path,
            headers={
                "Authorization": f"Bearer {self.tokens['access_token']}",  # type: ignore
                "application-id": self.application_id,
            },
            params=params,
            json=json,
        )

        if check_status:
            assert response.status_code == status.HTTP_200_OK, response.json()

        return response

    def get(self, path: str, params: Optional[dict] = None, check_status=True):
        return self.__request("GET", path, params, check_status=check_status)

    def post(self, path: str, params: Optional[dict] = None, json: Optional[dict] = None, check_status=True):
        return self.__request("POST", path, params, json, check_status)

    def put(self, path: str, params: Optional[dict] = None, json: Optional[dict] = None, check_status=True):
        return self.__request("PUT", path, params, json, check_status)

    def delete(self, path: str, params: Optional[dict] = None, json: Optional[dict] = None, check_status=True):
        return self.__request("DELETE", path, params, json, check_status)

    def patch(self, path: str, params: Optional[dict] = None, json: Optional[dict] = None, check_status=True):
        return self.__request("PATCH", path, params, json, check_status)

    # ======================================================== #
    # ===================== Verification ===================== #
    # ======================================================== #

    def submit_identity_verification(self, check_status=True):
        image_files_path = Path(__file__).parent / "test_files" / "img" / "identity"

        if not self.tokens:
            self.login_email()

        images = []
        file_handlers = []
        for file in image_files_path.iterdir():
            f = open(file, "rb")
            file_handlers.append(f)
            images.append(("image_files", (file.name, f, "image/png")))

        response = self.client.post(
            "/api/v1/verification/identity/submit_identity_verification",
            headers={
                "application-id": self.application_id,
                "Authorization": f"Bearer {self.tokens['access_token']}",  # type: ignore
            },
            data={
                "id_card_mrz": "dadhbwahdbahb",
                "first_name": "Test",
                "last_name": "User",
                "date_of_birth": "01.01.2025",
            },
            files=images,  # Pass files using the files parameter
        )

        if check_status:
            assert response.status_code == status.HTTP_200_OK, response.json()

        # Close all file handles after the request
        for f in file_handlers:
            f.close()

    def check_identity_verification_status(self):
        if not self.tokens:
            self.login_email()

        response = self.client.get(
            "/api/v1/verification/identity/self",
            headers={
                "Authorization": f"Bearer {self.tokens['access_token']}",  # type: ignore
                "application-id": self.application_id,
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["status"] == "approved"

    # ======================================================== #
    # ======================= Other ========================== #
    # ======================================================== #
    def get_details(self) -> dict:
        response = self.get(
            "/api/v1/user/me",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return response.json()


class AdminUser(TestUser):
    __test__ = False

    def __init__(self, client: TestClient):
        super().__init__(client)  # Call the parent class constructor
        self.email = "admin@localhost.de"
        self.name = "Admin"
        self.password = "ADMIN_ADMIN"

    def register(self):
        raise Exception("Admin user cannot be registered")

    def verify_identity(self, user_id: str, approve: bool = True):
        if not self.tokens:
            self.login_email()

        response = self.get("/api/v1/verification/identity/pending")
        assert len(response.json()) > 0

        identity_verification_id = ""
        for identity_verification in response.json():
            if identity_verification["user_id"] == user_id:
                identity_verification_id = identity_verification["id"]
                break

        assert identity_verification_id, "Identity verification ID not found for user."

        if approve:
            response = self.post(
                f"/api/v1/verification/identity/approve",
                params={"verification_id": identity_verification_id},
            )
            assert response.status_code == status.HTTP_200_OK, response.json()
        else:
            response = self.post(
                f"/api/v1/verification/identity/reject",
                json={"identity_verification_id": identity_verification_id, "reason": "YourMomStinks"},
            )
            assert response.status_code == status.HTTP_200_OK, response.json()


###########################################################################
################################### Club ##################################
###########################################################################
class Club:
    def __init__(self, user: TestUser):
        self.user = user

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + os.urandom(4).hex()

        self.name = f"Test Club {timestamp} {os.urandom(4).hex()}"
        self.description = f"Test Club {timestamp} Description"
        self.address = {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "postal_code": "12345",
            "country": "Germany",
        }

        self.club_id = None
        self.employees: List[Employee] = []
        self.roles: List[ClubRole] = []
        self.programs: List[Program] = []

    def create(self, check_default_roles=False, check: bool = True):
        response = self.user.post(
            "/api/v1/clubs",
            json={"name": self.name, "description": self.description, "address": self.address},
        )
        if check:
            assert response.json()["name"] == self.name
            assert response.json()["description"] == self.description
            assert response.json()["address"] == self.address

        self.club_id = response.json()["id"]

        assert response.status_code == status.HTTP_200_OK, response.json()
        if check_default_roles:
            self.check_default_roles()

    def get(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club_id}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["id"] == self.club_id, "Club ID mismatch"
        return response.json()

    def update(self, name: Optional[str] = None, description: Optional[str] = None):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + os.urandom(4).hex()
        if not name:
            name = f"Updated Club {timestamp}"
        if not description:
            description = f"Updated Club {timestamp} Description"

        response = self.user.put(
            f"/api/v1/clubs/{self.club_id}",
            json={"name": name, "description": description},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["id"] == self.club_id
        assert response.json()["name"] == name
        assert response.json()["description"] == description

        self.name = name
        self.description = description

    def delete(self):
        response = self.user.delete(
            f"/api/v1/clubs/{self.club_id}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        self.club_id = None

    # ======================================================== #
    # ========================= Roles ======================== #
    # ======================================================== #
    def check_default_roles(self):
        self.refresh_roles()
        role_dict = {role.name: role for role in self.roles}
        for role_name, role_data in DEFAULT_CLUB_ROLES.items():
            role = role_dict.get(role_name)
            assert role, f"Default Role {role_name} not found"
            assert role_data["level"] == role.level, f"Default Role {role_name} level mismatch"
            assert role_data["description"] == role.description, f"Default Role {role_name} description mismatch"
            for permission in role_data["permissions"]:
                if "*" in permission:
                    permission_start = permission.split("*")[0]
                    needed_permissions = [p.value for p in ClubPermissions if p.value.startswith(permission_start)]
                    for needed_permission in needed_permissions:
                        assert (
                            needed_permission in role.permissions
                        ), f"Default Role {role_name} permissions mismatch {needed_permission}"
                else:
                    assert permission in role.permissions, f"Default Role {role_name} permissions mismatch {permission}"

            # assert all(
            # permission in role.permissions for permission in role_data["permissions"]
            # ), f"Default Role {role_name} permissions mismatch"

    def refresh_roles(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club_id}/roles/all",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        self.roles.clear()
        for role in response.json():
            permission_names = [permission["name"] for permission in role["permissions"]]
            role_obj = ClubRole(self, role["name"], permission_names, role["level"], role["description"])
            role_obj.role_id = role["id"]
            self.roles.append(role_obj)

    # ======================================================== #
    # ======================= Employees ====================== #
    # ======================================================== #
    def refresh_employees(self, users: Optional[List[TestUser]] = None):
        self.refresh_roles()
        role_dict = {role.name: role for role in self.roles}
        user_dict = {user.email: user for user in users} if users else {}

        response = self.user.get(
            f"/api/v1/clubs/{self.club_id}/employees/all",
        )
        self.employees.clear()
        for role_name, employees in response.json().items():
            role = role_dict.get(role_name)
            assert role, f"Role with name {role_name} not found"
            for employee in employees:
                employee_obj = Employee(employee["email"], self, role, user_dict.get(employee["email"]))
                self.employees.append(employee_obj)

    # ======================================================== #
    # =================== Program Offerings ================== #
    # ======================================================== #
    def refresh_programs(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club_id}/programs",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        self.programs.clear()
        for program in response.json():
            program_obj = Program(
                self,
                program["name"],
                program["description"],
                PriceType(program["pricing_model"]),
                program.get("price"),
                program.get("capacity"),
                session_count=0,
                currency=program["currency"],
            )
            program_obj.program_id = program["id"]
            self.programs.append(program_obj)

    def refresh_programs_details(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club_id}/programs/details",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        self.programs.clear()
        for program in response.json():
            program_obj = Program(
                self,
                program["name"],
                program["description"],
                PriceType(program["pricing_model"]),
                program.get("price"),
                program.get("capacity"),
                session_count=0,
                currency=program["currency"],
                membership_required=program["membership_required"],
            )
            program_obj.program_id = program["id"]
            program_obj.refresh_sessions(program["sessions"])
            self.programs.append(program_obj)


class ClubRole:
    def __init__(self, club: Club, name: str, permissions: List[str], level: int, description: Optional[str] = None):
        self.user = club.user
        self.club = club

        self.name = name
        self.description = description if description else f"{name} Description"
        self.permissions = permissions
        self.level = level
        self.role_id = None

    def create(self, check_status=True):
        response = self.user.post(
            f"/api/v1/clubs/{self.club.club_id}/roles",
            json={
                "name": self.name,
                "description": self.description,
                "permissions": self.permissions,
                "level": self.level,
            },
        )
        if check_status:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["name"] == self.name
            assert response.json()["description"] == self.description
            assert all(
                permission["name"] in self.permissions for permission in response.json()["permissions"]
            ), "Permissions not found"
            assert response.json()["level"] == self.level
            self.role_id = response.json()["id"]

        return response

    def get(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club.club_id}/roles/{self.role_id}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["id"] == self.role_id

        return response

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        level: Optional[int] = None,
        check=True,
    ):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + os.urandom(4).hex()
        if not any([name, description, permissions, level]):
            if not name:
                name = f"Updated Role {timestamp}"
            if not description:
                description = f"Updated Role {timestamp} Description"
            if not permissions:
                permissions = random.sample(self.permissions, 2)

        response = self.user.put(
            f"/api/v1/clubs/{self.club.club_id}/roles/{self.role_id}",
            json={"name": name, "description": description, "permissions": permissions},
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["id"] == self.role_id
            assert response.json()["name"] == name
            assert response.json()["description"] == description
            assert all(
                permission["name"] in permissions for permission in response.json()["permissions"]
            ), "Permissions not found"
            self.name = response.json()["name"]
            self.description = response.json()["description"]
            self.permissions = [permission["name"] for permission in response.json()["permissions"]]
            self.level = response.json()["level"]
        return response

    def delete(self, check_deletion=True):
        response = self.user.delete(
            f"/api/v1/clubs/{self.club.club_id}/roles/{self.role_id}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        if check_deletion:
            response = self.user.get(
                f"/api/v1/roles/{self.role_id}",
                check_status=False,
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
        self.role_id = None

    def override_user(self, user: TestUser):
        self.user = user

    def assign_role(self, user_ident: str, user: Optional[TestUser] = None):
        if not user:
            user = self.user

        response = user.post(
            f"/api/v1/clubs/{self.club.club_id}/employees",
            json={"user_ident": user_ident, "level": self.level},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

    def unassign_role(self, user_ident: str, user: Optional[TestUser] = None):
        if not user:
            user = self.user

        response = user.delete(
            f"/api/v1/clubs/{self.club.club_id}/employees/{user_ident}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()


class Employee:
    def __init__(self, employee_ident: str, club: Club, role: ClubRole, employee: Optional[TestUser] = None):
        self.issuer = club.user
        self.employee = employee
        self.club = club
        self.role = role

        self.ident = employee_ident
        if employee:
            self.employee_id = employee.user_id
        else:
            self.employee_id = None

    def create(self, check: bool = True):
        response = self.issuer.post(
            f"/api/v1/clubs/{self.club.club_id}/employees",
            json={"user_ident": self.ident, "level": self.role.level},
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
        self.club.employees.append(self)

    def get(self, check: bool = True):
        if not self.employee_id:
            raise Exception("Employee ID not set")

        response = self.issuer.get(
            f"/api/v1/clubs/{self.club.club_id}/employees",
            params={"user_id": self.employee_id},
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["id"] == self.employee_id
        return response

    def update(self, role: ClubRole, check: bool = True):
        if not self.employee_id:
            raise Exception("Employee ID not set")

        response = self.issuer.put(
            f"/api/v1/clubs/{self.club.club_id}/employees",
            json={"user_id": self.employee_id, "level": role.level},
            check_status=False,
        )
        if check:
            response = self.get(check=False)
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["role_level"] == role.level

            self.role = role
        return response

    def delete(self, check_deletion: bool = True):
        if not self.employee_id:
            raise Exception("Employee ID not set")

        response = self.issuer.delete(
            f"/api/v1/clubs/{self.club.club_id}/employees",
            params={"user_id": self.employee_id},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        if check_deletion:
            response = self.get(check=False)
            assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

        self.employee_id = None


class Program:
    def __init__(
        self,
        club: Club,
        name: str,
        description: str,
        price_model: PriceType,
        price: Optional[int] = None,
        capacity: Optional[int] = None,
        session_count: Optional[int] = None,
        currency: str = "EUR",
        membership_required: bool = True,
    ):
        self.user = club.user
        self.club = club

        self.name = name
        self.description = description
        self.price_model = price_model

        if price_model == PriceType.PACKAGE and (not price or not capacity):
            warnings.warn("Price and capacity required for package programm")
        elif price_model == PriceType.PER_SESSION and (price or capacity):
            warnings.warn("Setting price or capacity should be None for per session programm")

        self.price = price
        self.currency = currency
        self.capacity = capacity
        self.membership_required = membership_required

        self.session_events: List[SessionEvent] = []
        self.session_courses: List[SessionCourse] = []
        self.trainers = []

        if session_count:
            self.session_events = get_random_session_events(self, session_count // 2)
            self.session_courses = get_random_session_courses(self, session_count // 2 + session_count % 2)

        self.program_id = None

    def create(self, check=True):
        if not self.club.club_id:
            raise Exception("Club ID not set")
        sessions = [events.to_dict() for events in self.session_events] + [
            courses.to_dict() for courses in self.session_courses
        ]

        response = self.user.post(
            f"/api/v1/clubs/{self.club.club_id}/programs",
            json={
                "name": self.name,
                "description": self.description,
                "pricing_model": self.price_model.value,
                "price": self.price,
                "currency": self.currency,
                "capacity": self.capacity,
                "sessions": sessions,
                "membership_required": self.membership_required,
            },
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["name"] == self.name
            assert response.json()["description"] == self.description
            assert response.json()["pricing_model"] == self.price_model.value
            assert response.json().get("price") == self.price
            assert response.json()["currency"] == self.currency
            assert response.json().get("capacity") == self.capacity
            assert response.json()["membership_required"] == self.membership_required
            self.program_id = response.json()["id"]
            self.check_sessions()

        self.club.programs.append(self)

    def get(self, check=True):
        if not self.get_id():
            raise Exception("Program ID not set")

        response = self.user.get(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}",
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["id"] == self.get_id()
            assert response.json()["name"] == self.name
            assert response.json()["description"] == self.description
            assert response.json()["pricing_model"] == self.price_model.value
            assert response.json().get("price") == self.price
            assert response.json()["currency"] == self.currency
            assert response.json().get("capacity") == self.capacity
            assert response.json()["membership_required"] == self.membership_required
            self.check_sessions(response.json()["sessions"])
        return response

    def refresh_id(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club.club_id}/programs",
        )
        for program in response.json():
            if program["name"] == self.name:
                self.program_id = program["id"]
                break

    def get_id(self):
        if not self.program_id:
            self.refresh_id()
        return self.program_id

    def update(self, check=True):
        new_name = f"Updated {self.name}"
        new_description = f"Updated {self.description}"
        session_data = {}

        if self.price_model == PriceType.PACKAGE:

            for session in self.session_events + self.session_courses:
                if not session.session_id:
                    raise Exception("Session ID not set")

                new_price = random.randint(0, 100)
                new_capacity = random.randint(1, 100)
                session_data[session.session_id] = (new_price, new_capacity)
                session.price = new_price
                session.capacity = new_capacity

            new_pricing_model = PriceType.PER_SESSION

            new_price = None
            new_capacity = None
            new_currency = "USD"
            new_membership_required = False
        else:
            for session in self.session_events + self.session_courses:
                session.price = None
                session.capacity = None

            new_pricing_model = PriceType.PACKAGE
            new_price = random.randint(0, 100)
            new_capacity = random.randint(1, 100)
            new_currency = "EUR"
            new_membership_required = True

        response = self.user.put(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}",
            json={
                "name": new_name,
                "description": new_description,
                "pricing_model": new_pricing_model.value,
                "price": new_price,
                "currency": new_currency,
                "capacity": new_capacity,
                "session_data": session_data if self.price_model == PriceType.PACKAGE else None,
                "membership_required": new_membership_required,
            },
            check_status=False,
        )

        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["id"] == self.get_id()
            assert response.json()["name"] == new_name
            assert response.json()["description"] == new_description
            assert response.json()["pricing_model"] == new_pricing_model.value
            assert response.json().get("price") == new_price
            assert response.json()["currency"] == new_currency
            assert response.json().get("capacity") == new_capacity
            assert response.json()["membership_required"] == new_membership_required
            self.check_sessions()

        self.name = new_name
        self.description = new_description
        self.price_model = new_pricing_model
        self.price = new_price
        self.currency = new_currency
        self.capacity = new_capacity
        self.membership_required = new_membership_required

    def update_status(self, program_status: ProgramStatusPublic, check=True):
        response = self.user.put(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}",
            json={"status": program_status.value},
            check_status=False,
        )

        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["status"] == program_status.value
        return response

    def delete(self, force_delete=False, check_deletion=True):
        response = self.user.delete(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}",
            params={"force": force_delete},
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        if check_deletion:
            response = self.user.get(
                f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}",
                check_status=False,
            )
            assert response.status_code == status.HTTP_200_OK, response.json()
            assert response.json()["status"] == "deleted"
        self.program_id = None

    # ======================================================== #
    # ======================= Sessions ======================= #
    # ======================================================== #
    def get_sessions(self) -> List[dict]:
        response = self.user.get(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}/sessions",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        return response.json()

    def check_sessions(self, sessions_to_check: Optional[List[dict]] = None):
        if not sessions_to_check:
            sessions_to_check = self.get_sessions()
        assert len(sessions_to_check) == len(self.session_events) + len(self.session_courses)

        for res_session in sessions_to_check:
            session = None
            if res_session["session_type"] == SessionType.EVENT.value:
                for event in self.session_events:
                    if event.start_datetime == datetime.datetime.strptime(
                        res_session["start_datetime"], "%Y-%m-%dT%H:%M:%S"
                    ) and event.end_datetime == datetime.datetime.strptime(
                        res_session["end_datetime"], "%Y-%m-%dT%H:%M:%S"
                    ):
                        session = event
                        break
            else:
                for course in self.session_courses:
                    if (
                        course.start_date == datetime.datetime.strptime(res_session["start_date"], "%Y-%m-%d").date()
                        and course.end_date == datetime.datetime.strptime(res_session["end_date"], "%Y-%m-%d").date()
                        and course.start_time
                        == datetime.datetime.strptime(res_session["start_time"], "%H:%M:%S").time()
                        and course.end_time == datetime.datetime.strptime(res_session["end_time"], "%H:%M:%S").time()
                        and course.day_of_week.value == res_session["day_of_week"]
                    ):
                        session = course
                        break

            assert session, "Session not found"

            assert res_session.get("price") == session.price
            assert res_session.get("capacity") == session.capacity
            assert res_session.get("address") == session.address
            session.session_id = res_session["id"]

    def refresh_sessions(self, sessions_refresh: list = []):
        if not sessions_refresh:
            response = self.user.get(
                f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}/sessions",
            )
            assert response.status_code == status.HTTP_200_OK, response.json()
            self.session_events.clear()
            self.session_courses.clear()
            sessions_refresh = response.json()
        for session in sessions_refresh:
            if session["session_type"] == SessionType.EVENT.value:
                session_obj = SessionEvent(
                    self,
                    datetime.datetime.strptime(session["start_datetime"], "%Y-%m-%dT%H:%M:%S"),
                    datetime.datetime.strptime(session["end_datetime"], "%Y-%m-%dT%H:%M:%S"),
                    address=session.get("address"),
                    price=session.get("price"),
                    capacity=session.get("capacity"),
                )
                session_obj.session_id = session["id"]
                self.session_events.append(session_obj)
            else:
                session_obj = SessionCourse(
                    self,
                    Weekday(session["day_of_week"]),
                    datetime.datetime.strptime(session["start_time"], "%H:%M:%S").time(),
                    datetime.datetime.strptime(session["end_time"], "%H:%M:%S").time(),
                    datetime.datetime.strptime(session["start_date"], "%Y-%m-%d").date(),
                    datetime.datetime.strptime(session["end_date"], "%Y-%m-%d").date(),
                    address=session.get("address"),
                    price=session.get("price"),
                    capacity=session.get("capacity"),
                )
                session_obj.session_id = session["id"]
                self.session_courses.append(session_obj)

    # ======================================================== #
    # ======================== Trainer ======================= #
    # ======================================================== #
    def assign_trainer(self, user_id: str, check=True):
        self.user.post(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}/trainers",
            params={"user_id": user_id},
        )
        self.trainers.append(user_id)

        if check:
            trainers = self.get_trainers()
            assert user_id in {trainer["id"] for trainer in trainers}

    def unassign_trainer(self, user_id: str, check=True):
        self.user.delete(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}/trainers/{user_id}",
        )
        self.trainers.remove(user_id)

        if check:
            trainers = self.get_trainers()
            assert user_id not in {trainer["id"] for trainer in trainers}

    def get_trainers(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.club.club_id}/programs/{self.get_id()}/trainers",
        )
        return response.json()


class Session:
    def __init__(self, program: Program):
        self.user = program.club.user
        self.program = program
        self.session_id = None
        self.price = None
        self.capacity = None
        self.address = None

    @abstractmethod
    def randomize(self):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def create(self, check=True):
        response = self.user.post(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions",
            json=self.to_dict(),
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
        self.session_id = response.json()["id"]



    def get(self, check=True) -> bool:
        response = self.user.get(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions",
            check_status=False,
        )
        assert response.status_code == status.HTTP_200_OK, response.json()
        session_found = False
        for session in response.json():
            if session["id"] == self.get_id():
                assert session.get("price") == self.price
                assert session.get("capacity") == self.capacity
                assert session.get("address") == self.address
                session_found = True
                break
        if check:
            assert session_found, "Session not found"
        return session_found

    @abstractmethod
    def is_same(self, session: dict) -> bool:
        pass

    def refresh_id(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions",
        )
        for session in response.json():
            if self.is_same(session):
                self.session_id = session["id"]
                break

    def get_id(self):
        if not self.session_id:
            self.refresh_id()
        return self.session_id

    def update(self, check=True):
        response = self.user.put(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/{self.get_id()}",
            json=self.to_dict(),
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
        return response

    def delete(self, check_deletion=True):
        response = self.user.delete(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/{self.get_id()}",
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        if check_deletion:
            session_found = self.get(check=False)
            assert session_found is False, "Session not deleted"
        self.session_id = None


def random_times() -> Tuple[datetime.time, datetime.time]:
    start_time = datetime.time(random.randint(0, 22), random.randint(0, 59))
    end_time = datetime.time(random.randint(start_time.hour + 1, 23), random.randint(0, 59))
    return start_time, end_time


def random_dates() -> Tuple[datetime.date, datetime.date]:
    start_date = datetime.date.today() + datetime.timedelta(days=random.randint(1, 30))
    end_date = start_date + datetime.timedelta(days=random.randint(10, 30))
    return start_date, end_date


class SessionEvent(Session):
    def __init__(
        self,
        program: Program,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        address: Optional[dict] = None,
        price: Optional[int] = None,
        capacity: Optional[int] = None,
    ):
        super().__init__(program)

        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.address = address

        if program.price_model == PriceType.PACKAGE and (price or capacity):
            warnings.warn("Setting price or capacity should be None for package programm")
        elif program.price_model == PriceType.PER_SESSION and (not price or not capacity):
            warnings.warn("Price and capacity required for per session programm")

        self.price = price
        self.capacity = capacity

        self.session_id = None

    def to_dict(self) -> dict:
        return {
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": self.end_datetime.isoformat(),
            "session_type": SessionType.EVENT.value,
            "address": self.address,
            "price": self.price,
            "capacity": self.capacity,
        }

    def randomize(self):
        start_time, end_time = random_times()
        start_date, end_date = random_dates()
        self.start_datetime = datetime.datetime.combine(start_date, start_time)
        self.end_datetime = datetime.datetime.combine(end_date, end_time)

        if self.program.price_model == PriceType.PER_SESSION:
            self.price = random.randint(100, 1000)
            self.capacity = random.randint(1, 100)

    def to_course(self) -> "SessionCourse":
        start_date = self.start_datetime.date()
        end_date = self.end_datetime.date()
        start_time = self.start_datetime.time()
        end_time = self.end_datetime.time()
        weekday = random.choice(list(Weekday.__members__.values()))
        return SessionCourse(
            self.program,
            day_of_week=weekday,
            start_time=start_time,
            end_time=end_time,
            start_date=start_date,
            end_date=end_date,
            address=self.address,
            price=self.price,
            capacity=self.capacity,
        )

    def create(self, check=True):
        super().create(check)
        self.program.session_events.append(self)

    def is_same(self, session: dict) -> bool:
        return (
            session["session_type"] == SessionType.EVENT.value
            and session["start_datetime"] == self.start_datetime.isoformat()
            and session["end_datetime"] == self.end_datetime.isoformat()
        )


class SessionCourse(Session):
    def __init__(
        self,
        program: Program,
        day_of_week: Weekday,
        start_time: datetime.time,
        end_time: datetime.time,
        start_date: datetime.date,
        end_date: datetime.date,
        address: Optional[dict] = None,
        price: Optional[int] = None,
        capacity: Optional[int] = None,
    ):
        super().__init__(program)

        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.address = address

        if program.price_model == PriceType.PACKAGE and (price or capacity):
            warnings.warn("Setting price or capacity should be None for package programm")
        elif program.price_model == PriceType.PER_SESSION and (not price or not capacity):
            warnings.warn("Price and capacity required for per session programm")

        self.price = price
        self.capacity = capacity

        self.session_id = None

        self.occurences = {}

    def to_dict(self) -> dict:
        return {
            "day_of_week": self.day_of_week.value,
            "session_type": SessionType.COURSE.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "address": self.address,
            "price": self.price,
            "capacity": self.capacity,
        }

    def randomize(self):
        start_time, end_time = random_times()
        start_date, end_date = random_dates()
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.day_of_week = random.choice(list(Weekday))

        if self.program.price_model == PriceType.PER_SESSION:
            self.price = random.randint(100, 1000)
            self.capacity = random.randint(1, 100)

    def to_event(self) -> SessionEvent:
        start_datetime = datetime.datetime.combine(self.start_date, self.start_time)
        end_datetime = datetime.datetime.combine(self.end_date, self.end_time)
        return SessionEvent(self.program, start_datetime, end_datetime, self.address, self.price, self.capacity)

    def create(self, check=True):
        super().create(check)
        self.refresh_occurrences()
        self.program.session_courses.append(self)

    def is_same(self, session: dict) -> bool:
        return (
            session["session_type"] == SessionType.COURSE.value
            and session["day_of_week"] == self.day_of_week.value
            and session["start_time"] == self.start_time.isoformat()
            and session["end_time"] == self.end_time.isoformat()
            and session["start_date"] == self.start_date.isoformat()
            and session["end_date"] == self.end_date.isoformat()
        )

    def refresh_occurrences(self):
        response = self.user.get(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/",
            check_status=False,
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        for session in response.json():
            if session["id"] == self.get_id():
                if not session.get("occurrences"):
                    time.sleep(1)
                    self.refresh_occurrences()
                    return
                self.occurences = {occ["id"]: occ for occ in session.get("occurrences", [])}
                return

    def reschedule_occurrence(self, occurence_id: Optional[str] = None) -> str:
        if not occurence_id:
            if not self.occurences:
                self.refresh_occurrences()
            occurence_id = random.choice(list(self.occurences.keys()))

        new_day = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 5))
        new_start_time, new_end_time = random_times()
        new_start_date = datetime.datetime.combine(new_day.date(), new_start_time)
        new_end_date = datetime.datetime.combine(new_day.date(), new_end_time)

        response = self.user.put(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/{self.get_id()}/occurrences/reschedule",
            json=[
                {
                    "occurrence_id": occurence_id,
                    "note": "Rescheduled",
                    "start_datetime": new_start_date.isoformat(),
                    "end_datetime": new_end_date.isoformat(),
                }
            ],  # type: ignore
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        self.refresh_occurrences()
        occurence = self.occurences[occurence_id]
        assert occurence["start_datetime"] == new_start_date.isoformat()
        assert occurence["end_datetime"] == new_end_date.isoformat()
        assert occurence["note"] == "Rescheduled", f"Note mismatch {occurence['note']}"
        assert occurence["status"] == "rescheduled", f"Status mismatch {occurence['status']}"
        return occurence_id

    def cancel_occurrence(self, occurence_id: Optional[str] = None, check: bool = True) -> str:
        if not occurence_id:
            if not self.occurences:
                self.refresh_occurrences()
            active_occurences = []

            for occ in self.occurences.values():
                if occ["status"] == "scheduled":
                    active_occurences.append(occ["id"])

            if not active_occurences:
                raise Exception("No active occurences to cancel")
            occurence_id = random.choice(active_occurences)

        response = self.user.delete(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/{self.get_id()}/occurrences/{occurence_id}",
            check_status=False,
        )
        if check:
            assert response.status_code == status.HTTP_200_OK, response.json()
            self.refresh_occurrences()
            occurence = self.occurences[occurence_id]
            assert occurence["status"] == "cancelled", f"Status mismatch {occurence['status']}"
        return occurence_id # type: ignore

    def reinstate_occurrence(self, occurence_id: str) -> str:
        if not occurence_id:
            raise Exception("Occurence ID required for reinstating")
            

        response = self.user.put(
            f"/api/v1/clubs/{self.program.club.club_id}/programs/{self.program.get_id()}/sessions/{self.get_id()}/occurrences/reinstate",
            json=[
                {
                    "occurrence_id": occurence_id,
                    "note": "Reinstated",
                }
            ],  # type: ignore
        )
        assert response.status_code == status.HTTP_200_OK, response.json()

        self.refresh_occurrences()
        occurence = self.occurences[occurence_id]
        assert occurence["note"] == "Reinstated", f"Note mismatch {occurence['note']}"
        assert occurence["status"] == "scheduled", f"Status mismatch {occurence['status']}"
        return occurence_id


def get_random_session_events(program: Program, count: int = 1) -> List[SessionEvent]:
    sessions = []
    for _ in range(count):
        start_time, end_time = random_times()
        date, _ = random_dates()

        price = None
        capacity = None

        if program.price_model == PriceType.PER_SESSION:
            price = random.randint(100, 1000)
            capacity = random.randint(1, 100)

        session = SessionEvent(
            program,
            start_datetime=datetime.datetime.combine(date, start_time),
            end_datetime=datetime.datetime.combine(date, end_time),
            price=price,
            capacity=capacity,
        )
        sessions.append(session)
    return sessions


def get_random_session_courses(program: Program, count: int = 1) -> List[SessionCourse]:
    sessions = []
    for _ in range(count):
        start_time, end_time = random_times()
        start_date, end_date = random_dates()
        price = None
        capacity = None

        if program.price_model == PriceType.PER_SESSION:
            price = random.randint(100, 1000)
            capacity = random.randint(1, 100)

        session = SessionCourse(
            program,
            day_of_week=random.choice(list(Weekday)),
            start_time=start_time,
            end_time=end_time,
            start_date=start_date,
            end_date=end_date,
            price=price,
            capacity=capacity,
        )
        sessions.append(session)
    return sessions


def get_random_programs(club: Club, count: int = 2, max_sessions: Optional[int] = None) -> List[Program]:
    programs = []
    count_package = random.randint(1, count - 1) if count > 1 else 1
    count_per_session = count - count_package

    for _ in range(count):
        name = f"Test Program {datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')} {os.urandom(4).hex()}"
        description = f"Test Program {datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')} Description"

        if count_package > 0:
            price_model = PriceType.PACKAGE
            count_package -= 1
        else:
            price_model = PriceType.PER_SESSION
            count_per_session -= 1
        price = None
        capacity = None

        if price_model == PriceType.PACKAGE:
            price = random.randint(100, 1000)
            capacity = random.randint(1, 100)

        program = Program(
            club,
            name,
            description,
            price_model,
            price,
            capacity,
            random.randint(4, max_sessions) if max_sessions else None,
        )
        programs.append(program)
    return programs
