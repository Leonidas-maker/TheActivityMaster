import pytest
from .conftest import *
import time



def test_init_database(client):
    retries = 0
    while retries < 5:
        try:
            client.get(
                "/ping",
            )
            break
        except Exception as e:
            retries += 1
            time.sleep(1)