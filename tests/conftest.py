"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
from code_graph.indexer.main import Indexer


@pytest.fixture
def indexed_repo(tmp_path):
    """Create and index a sample repository.

    This fixture creates a small Python repository with realistic code
    including user registration, validation utilities, and tests.
    It then indexes the repository and returns the GraphStore.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        GraphStore: Indexed graph containing the sample repository
    """
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Create user registration module
    (src_dir / "registration.py").write_text("""
\"\"\"User registration module.\"\"\"

from src.validation import validate_email
from src.models import User


def register_user(email: str, password: str):
    \"\"\"Register a new user.

    Args:
        email: User email address
        password: User password

    Returns:
        User: Created user instance

    Raises:
        ValueError: If email is invalid
    \"\"\"
    if not validate_email(email):
        raise ValueError("Invalid email address")

    user = User(email=email)
    user.set_password(password)
    return user
""")

    # Create validation utilities
    (src_dir / "validation.py").write_text("""
\"\"\"Validation utilities.\"\"\"

import re


def validate_email(email: str) -> bool:
    \"\"\"Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email is valid, False otherwise
    \"\"\"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    \"\"\"Validate password strength.

    Args:
        password: Password to validate

    Returns:
        bool: True if password is strong enough
    \"\"\"
    return len(password) >= 8
""")

    # Create user model
    (src_dir / "models.py").write_text("""
\"\"\"Data models.\"\"\"

import hashlib


class User:
    \"\"\"User model.\"\"\"

    def __init__(self, email: str):
        \"\"\"Initialize user.

        Args:
            email: User email address
        \"\"\"
        self.email = email
        self.password_hash = None

    def set_password(self, password: str):
        \"\"\"Set user password.

        Args:
            password: Plain text password
        \"\"\"
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        \"\"\"Verify password.

        Args:
            password: Plain text password to check

        Returns:
            bool: True if password matches
        \"\"\"
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
""")

    # Create authentication module
    (src_dir / "auth.py").write_text("""
\"\"\"Authentication module.\"\"\"

from src.models import User


class AuthenticationError(Exception):
    \"\"\"Raised when authentication fails.\"\"\"
    pass


def authenticate(email: str, password: str) -> User:
    \"\"\"Authenticate user.

    Args:
        email: User email
        password: User password

    Returns:
        User: Authenticated user

    Raises:
        AuthenticationError: If authentication fails
    \"\"\"
    # TODO: Implement actual authentication
    raise NotImplementedError("Authentication not implemented")
""")

    # Create test file
    (tests_dir / "test_registration.py").write_text("""
\"\"\"Tests for user registration.\"\"\"

import pytest
from src.registration import register_user
from src.validation import validate_email


def test_register_user_with_valid_email():
    \"\"\"Test user registration with valid email.\"\"\"
    user = register_user("test@example.com", "password123")
    assert user.email == "test@example.com"


def test_register_user_with_invalid_email():
    \"\"\"Test user registration with invalid email.\"\"\"
    with pytest.raises(ValueError, match="Invalid email"):
        register_user("invalid-email", "password123")


def test_validate_email_valid():
    \"\"\"Test email validation with valid email.\"\"\"
    assert validate_email("test@example.com") is True


def test_validate_email_invalid():
    \"\"\"Test email validation with invalid email.\"\"\"
    assert validate_email("invalid") is False
""")

    # Create __init__.py files
    (src_dir / "__init__.py").write_text("")
    (tests_dir / "__init__.py").write_text("")

    # Index the repository
    indexer = Indexer()
    result = indexer.index_repository(str(tmp_path))

    # Verify indexing succeeded
    assert result.success, f"Indexing failed with errors: {result.errors}"
    assert result.files_indexed >= 4, f"Expected at least 4 files, got {result.files_indexed}"

    # Return the graph store
    return indexer.store
