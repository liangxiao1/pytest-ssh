
import pytest
from .ssh import SSH


@pytest.fixture
def ssh_get():
    return SSH
