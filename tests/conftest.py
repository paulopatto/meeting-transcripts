"""Shared fixtures for tests."""

import pytest


@pytest.fixture
def mock_token():
    return "mock-access-token-12345"


@pytest.fixture
def mock_api_key():
    return "mock-api-key-abcde"
