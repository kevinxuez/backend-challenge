import pytest
import json
from src.app import app, db
from src.models import User
from scripts.bootstrap import load_data, create_user

@pytest.fixture(scope="function")
def testClient():
    """Set up an in-memory test client and database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        load_data()
        create_user()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_create_review_api(testClient):
    """Test creating a review via API."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great juggling club!",
            "text": "Really enjoyed the pre-professional atmosphere."
        }
        
        response = testClient.post('/api/reviews',
                                  data=json.dumps(review_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["rating"] == 8
        assert response_data["title"] == "Great juggling club!"

def test_get_club_reviews_api(testClient):
    """Test getting reviews for a club."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create a review first
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great club!",
            "text": "Test review"
        }
        
        testClient.post('/api/reviews',
                       data=json.dumps(review_data),
                       content_type='application/json')
        
        # Get reviews for the club
        response = testClient.get('/api/clubs/pppjo/reviews')
        assert response.status_code == 200
        
        reviews = json.loads(response.data)
        assert len(reviews) == 1
        assert reviews[0]["rating"] == 8

def test_get_club_review_stats_api(testClient):
    """Test getting review statistics for a club."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create a review first
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great club!",
            "text": "Test review"
        }
        
        testClient.post('/api/reviews',
                       data=json.dumps(review_data),
                       content_type='application/json')
        
        # Get stats
        response = testClient.get('/api/clubs/pppjo/reviews/stats')
        assert response.status_code == 200
        
        stats = json.loads(response.data)
        assert stats["total_reviews"] == 1
        assert stats["average_rating"] == 8.0
        assert stats["rating_distribution"]["8"] == 1

def test_update_review_api(testClient):
    """Test updating a review via API."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create review
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 7,
            "title": "Good club",
            "text": "Initial review"
        }
        
        create_response = testClient.post('/api/reviews',
                                         data=json.dumps(review_data),
                                         content_type='application/json')
        
        review_id = json.loads(create_response.data)["id"]
        
        # Update review
        update_data = {
            "rating": 9,
            "title": "Amazing club!",
            "text": "Updated review - much better than I thought!"
        }
        
        response = testClient.put(f'/api/reviews/{review_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        updated_review = json.loads(response.data)
        assert updated_review["rating"] == 9
        assert updated_review["title"] == "Amazing club!"

def test_delete_review_api(testClient):
    """Test deleting a review via API."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create review
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great club!",
            "text": "Test review"
        }
        
        create_response = testClient.post('/api/reviews',
                                         data=json.dumps(review_data),
                                         content_type='application/json')
        
        review_id = json.loads(create_response.data)["id"]
        
        # Delete review
        response = testClient.delete(f'/api/reviews/{review_id}')
        assert response.status_code == 200
        
        # Verify deletion
        get_response = testClient.get(f'/api/reviews/{review_id}')
        assert get_response.status_code == 404

def test_review_validation_api(testClient):
    """Test API validation for reviews."""
    # Missing required fields
    response = testClient.post('/api/reviews',
                              data=json.dumps({}),
                              content_type='application/json')
    assert response.status_code == 400
    
    # Invalid rating
    invalid_data = {
        "user_id": 1,
        "club_code": "pppjo",
        "rating": 15,  # Too high
        "title": "Test title"
    }
    response = testClient.post('/api/reviews',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
    assert response.status_code == 400

def test_get_user_reviews_api(testClient):
    """Test getting all reviews by a user."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create multiple reviews
        review1_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great juggling!",
            "text": "Love it"
        }
        
        review2_data = {
            "user_id": user.id,
            "club_code": "penn-memes",
            "rating": 9,
            "title": "Hilarious memes",
            "text": "So funny"
        }
        
        testClient.post('/api/reviews',
                       data=json.dumps(review1_data),
                       content_type='application/json')
        testClient.post('/api/reviews',
                       data=json.dumps(review2_data),
                       content_type='application/json')
        
        # Get user's reviews
        response = testClient.get(f'/api/users/{user.id}/reviews')
        assert response.status_code == 200
        
        reviews = json.loads(response.data)
        assert len(reviews) == 2

def test_get_user_club_review_api(testClient):
    """Test getting a user's specific club review."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create review
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Great club!",
            "text": "Test review"
        }
        
        testClient.post('/api/reviews',
                       data=json.dumps(review_data),
                       content_type='application/json')
        
        # Get user's review for specific club
        response = testClient.get(f'/api/users/{user.id}/reviews/pppjo')
        assert response.status_code == 200
        
        review = json.loads(response.data)
        assert review["rating"] == 8
        assert review["club_code"] == "pppjo"

def test_get_reviews_pagination_api(testClient):
    """Test review pagination."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create a review first
        review_data = {
            "user_id": user.id,
            "club_code": "pppjo",
            "rating": 8,
            "title": "Test review",
            "text": "Test"
        }
        
        testClient.post('/api/reviews',
                       data=json.dumps(review_data),
                       content_type='application/json')
        
        # Test pagination endpoint
        response = testClient.get('/api/reviews?page=1&per_page=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "reviews" in data
        assert "total" in data
        assert "pages" in data
        assert "current_page" in data
