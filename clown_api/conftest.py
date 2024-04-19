"""This file contains fixtures for testing the API."""

import pytest

from app import app


@pytest.fixture
def fake_clown():
    """Returns an example clown as a dict."""
    return {"clown_id": 1,
            "clown_name": "Bernice",
            "speciality_id": 3}


@pytest.fixture
def test_app():
    """Returns a test version of the API."""
    return app.test_client()


@pytest.fixture
def new_fake_clown_with_ratings():
    """Returns an example clown as a dict."""
    return {'average_rating': '1', 
            'clown_id': 1, 
            'clown_name': 'It', 
            'review_count': 1, 
            'speciality_name': 'magic'}
