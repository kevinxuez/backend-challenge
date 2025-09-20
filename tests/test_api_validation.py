import pytest
import json
import sys
import os

from src.app import app, db
from scripts.bootstrap import load_data

@pytest.fixture(scope="function")
def testClient():
    """Set up an in-memory test client and database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_create_club_validation(testClient):
    """Test club creation API with invalid data."""
    # Missing required fields
    response = testClient.post('/api/clubs', 
                              data=json.dumps({}),
                              content_type='application/json')
    assert response.status_code == 400
    assert "No input data provided" in response.get_json()["error"]
    
    # Invalid data types
    invalid_data = {
        "code": 123,  # Should be string
        "name": "Test Club",
        "description": "A test club description that is long enough",
        "undergraduatesAllowed": True,
        "graduatesAllowed": False
    }
    response = testClient.post('/api/clubs', 
                              data=json.dumps(invalid_data),
                              content_type='application/json')
    assert response.status_code == 400
    
    # Valid data should work
    valid_data = {
        "code": "test-club",
        "name": "Test Club",
        "description": "A test club description that is long enough",
        "tags": ["Undergraduate", "Academic"],
        "memberCount": 50,
        "undergraduatesAllowed": True,
        "graduatesAllowed": False
    }
    response = testClient.post('/api/clubs', 
                              data=json.dumps(valid_data),
                              content_type='application/json')
    assert response.status_code == 201

def test_create_user_validation(testClient):
    """Test user creation API with invalid data."""
    # Missing required fields
    response = testClient.post('/api/users', 
                              data=json.dumps({}),
                              content_type='application/json')
    assert response.status_code == 400
    
    # Invalid email
    invalid_data = {
        "username": "testuser",
        "email": "invalid-email"
    }
    response = testClient.post('/api/users', 
                              data=json.dumps(invalid_data),
                              content_type='application/json')
    assert response.status_code == 400
    
    # Valid data should work
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "favorites": []
    }
    response = testClient.post('/api/users', 
                              data=json.dumps(valid_data),
                              content_type='application/json')
    assert response.status_code == 201

def test_search_validation(testClient):
    """Test search API validation."""
    # Empty query
    response = testClient.get('/api/clubs/search?query=')
    assert response.status_code == 400
    
    # Missing query parameter
    response = testClient.get('/api/clubs/search')
    assert response.status_code == 400
    
    # Query too long
    long_query = "a" * 101
    response = testClient.get(f'/api/clubs/search?query={long_query}')
    assert response.status_code == 400

def test_update_club_validation(testClient):
    """Test club update API validation."""
    with app.app_context():
        # Create test data
        load_data()
        
        # Invalid club code format in URL
        response = testClient.put('/api/clubs/invalid@code', 
                                 data=json.dumps({"name": "New Name"}),
                                 content_type='application/json')
        assert response.status_code == 400
        
        # Valid update
        response = testClient.put('/api/clubs/pppjo', 
                                 data=json.dumps({"name": "Updated Club Name"}),
                                 content_type='application/json')
        assert response.status_code == 200

def test_validation_error_messages(testClient):
    """Test that validation errors return helpful messages."""
    # Test with short club name
    invalid_data = {
        "code": "test",
        "name": "ab",  # Too short
        "description": "A test club description that is long enough",
        "undergraduatesAllowed": True,
        "graduatesAllowed": False
    }
    response = testClient.post('/api/clubs', 
                              data=json.dumps(invalid_data),
                              content_type='application/json')
    assert response.status_code == 400
    assert "at least 3 characters" in response.get_json()["error"]