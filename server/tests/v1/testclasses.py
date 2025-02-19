import datetime
import uuid
import re
from urllib.parse import urlencode
from fastapi import status
from fastapi.testclient import TestClient
from pathlib import Path
import pyotp
import time
from typing import Optional
import os


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
