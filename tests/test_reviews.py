import pytest

from src.app import app, db
from src.models import Club, User, Review
from scripts.bootstrap import load_data, create_user

@pytest.fixture(scope="function")
def testClient():
    """Set up an in-memory test client and database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        load_data()  # Load clubs
        create_user()  # Create test user
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_review_creation(testClient):
    """Test creating a new review."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        club = Club.query.filter_by(code="pppjo").first()
        
        assert user is not None
        assert club is not None
        
        review = Review.createNewReview(
            user_id=user.id,
            club_code=club.code,
            rating=8,
            title="Great club!",
            text="Really enjoyed my time here."
        )
        
        assert review.user_id == user.id
        assert review.club_code == club.code
        assert review.rating == 8
        assert review.title == "Great club!"
        assert review.text == "Really enjoyed my time here."

def test_review_validation_errors(testClient):
    """Test that Review creation fails with invalid input."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Invalid rating (too high)
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=user.id,
                club_code="pppjo",
                rating=11,
                title="Great club!",
                text="Test"
            )
        
        # Invalid rating (too low)
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=user.id,
                club_code="pppjo",
                rating=0,
                title="Great club!",
                text="Test"
            )
        
        # Title too short
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=user.id,
                club_code="pppjo",
                rating=8,
                title="Bad",
                text="Test"
            )
        
        # Non-existent user
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=999,
                club_code="pppjo",
                rating=8,
                title="Great club!",
                text="Test"
            )
        
        # Non-existent club
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=user.id,
                club_code="nonexistent",
                rating=8,
                title="Great club!",
                text="Test"
            )

def test_duplicate_review_prevention(testClient):
    """Test that duplicate reviews are prevented."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        # Create first review
        review1 = Review.createNewReview(
            user_id=user.id,
            club_code="pppjo",
            rating=8,
            title="Great club!",
            text="Test"
        )
        Review.addReviewToDb(review1)
        
        # Try to create duplicate review
        with pytest.raises(ValueError):
            Review.createNewReview(
                user_id=user.id,
                club_code="pppjo",
                rating=9,
                title="Even better!",
                text="Test"
            )

def test_club_average_rating(testClient):
    """Test club average rating calculation."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        club = Club.query.filter_by(code="pppjo").first()
        
        # Initially no reviews
        assert club.get_average_rating() == 0.0
        
        # Add one review
        review1 = Review.createNewReview(
            user_id=user.id,
            club_code=club.code,
            rating=8,
            title="Good club",
            text="Test"
        )
        Review.addReviewToDb(review1)
        
        # Create another user for second review
        user2 = User.createNewUser("testuser2", "test2@example.com", set())
        User.addUserToDb(user2)
        
        review2 = Review.createNewReview(
            user_id=user2.id,
            club_code=club.code,
            rating=6,
            title="Okay club",
            text="Test"
        )
        Review.addReviewToDb(review2)
        
        # Average should be (8 + 6) / 2 = 7.0
        assert club.get_average_rating() == 7.0

def test_review_updates(testClient):
    """Test updating review fields."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        review = Review.createNewReview(
            user_id=user.id,
            club_code="pppjo",
            rating=8,
            title="Good club",
            text="Initial review"
        )
        Review.addReviewToDb(review)
        
        original_updated_at = review.updated_at
        
        # Update rating
        review.updateRating(9)
        assert review.rating == 9
        assert review.updated_at > original_updated_at
        
        # Update title
        review.updateTitle("Great club!")
        assert review.title == "Great club!"
        
        # Update text
        review.updateText("Updated review text")
        assert review.text == "Updated review text"

def test_review_to_json(testClient):
    """Test review JSON serialization."""
    with app.app_context():
        user = User.query.filter_by(username="Josh").first()
        
        review = Review.createNewReview(
            user_id=user.id,
            club_code="pppjo",
            rating=8,
            title="Great club!",
            text="Really enjoyed it."
        )
        Review.addReviewToDb(review)
        
        json_data = review.toJson()
        assert json_data["user_id"] == user.id
        assert json_data["club_code"] == "pppjo"
        assert json_data["rating"] == 8
        assert json_data["title"] == "Great club!"
        assert json_data["text"] == "Really enjoyed it."
        assert json_data["user_username"] == "Josh"
        assert "created_at" in json_data
        assert "updated_at" in json_data
