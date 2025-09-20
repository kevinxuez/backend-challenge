import pytest
from src.app import app, db
from src.models import Club, User
from scripts.bootstrap import create_user, load_data
import json

@pytest.fixture(scope="function")
def testClient():
    """Set up an in-memory test client and database.
    (return) TestClient: A Flask test client with a fresh DB.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def testCreateClubAPI(testClient):
    """Test creating a club via API.
    (return) None
    """
    clubData = {
        "code": "test-club",
        "name": "Test Club",
        "description": "A test club",
        "tags": ["Undergraduate", "Academic"],
        "memberCount": 50,
        "undergraduatesAllowed": True,
        "graduatesAllowed": False
    }
    response = testClient.post('/api/clubs', 
                              data=json.dumps(clubData),
                              content_type='application/json')
    assert response.status_code == 201
    responseData = json.loads(response.data)
    assert responseData["code"] == "test-club"
    assert responseData["name"] == "Test Club"

def testGetClubsAPI(testClient):
    """Test getting all clubs via API.
    (return) None
    """
    # First create some test data
    load_data()
    
    response = testClient.get('/api/clubs')
    assert response.status_code == 200
    clubs = json.loads(response.data)
    assert len(clubs) > 0
    assert any(club["code"] == "pppjo" for club in clubs)

def testSearchClubsAPI(testClient):
    """Test searching clubs via API.
    (return) None
    """
    load_data()
    
    response = testClient.get('/api/clubs/search?query=Penn')
    assert response.status_code == 200
    clubs = json.loads(response.data)
    assert all("Penn" in club["name"] for club in clubs)