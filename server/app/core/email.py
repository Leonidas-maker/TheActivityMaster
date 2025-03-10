from typing import Optional
from contextlib import contextmanager

from utils.email_manager import EmailManager


class EmailManagerDependency:
    def __init__(self):
        self._km: Optional[EmailManager] = None

    def init(self, km_instance: EmailManager):
        self._km = km_instance

    @contextmanager
    def get(self):
        if not self._km:
            raise RuntimeError("KeyManager not initialized")
        yield self._km


email_manager_dependency = EmailManagerDependency()