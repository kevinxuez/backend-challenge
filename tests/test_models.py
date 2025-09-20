import pytest
import sys
import os

# Add the src and scripts directories to the Python path

from src.app import app, db
from src.models import Club, User
from scripts.bootstrap import create_user, load_data

@pytest.fixture(scope="function")
def testClient():
    """Set up an in-memory test client and database.
    (return) TestClient: A Flask test client with a fresh DB.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        # Load data once for all tests
        load_data()
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def testDataLoading(testClient):
    """Test that user data and club data load correctly.
    (return) None
    """
    with app.app_context():
        create_user()
        db.session.commit()
        josh = User.query.filter_by(username="Josh").first()
        assert josh is not None
        assert josh.email == "josh@upenn.edu"
        favoriteCodes = {club.code for club in josh.favoriteClubs}
        assert favoriteCodes == {"penn-memes"}


def testClubLoading(testClient):
    """Test that club details load correctly.
    (return) None
    """
    with app.app_context():
        pppjo = Club.query.filter_by(code="pppjo").first()
        assert pppjo is not None
        assert pppjo.name == (
            "Penn Pre-Professional Juggling Organization"
        )
        assert pppjo.description == (
            "The PPPJO is looking for intense jugglers seeking to juggle their "
            "way to the top. Come with your juggling equipment (and business "
            "formal attire) to hone your skills in time for recruiting season!"
        )
        pennMemesClub = Club.query.filter_by(code="penn-memes").first()
        assert pennMemesClub is not None
        assert pennMemesClub.name == "Penn Memes Club"
        tagNames = {tag.name for tag in pennMemesClub.tags}
        assert tagNames == {"Graduate", "Literary"}


def testLegacyDataLoading(testClient):
    """Test that legacy club data load with correct tag associations.
    (return) None
    """
    with app.app_context():
        pppjo = Club.query.filter_by(code="pppjo").first()
        assert pppjo is not None
        assert pppjo.name == (
            "Penn Pre-Professional Juggling Organization"
        )
        tagsPppjo = {tag.name for tag in pppjo.tags}
        assert tagsPppjo == {"Pre-Professional", "Athletics", "Undergraduate"}
        
        lorem = Club.query.filter_by(code="lorem-ipsum").first()
        assert lorem is not None
        tagsLorem = {tag.name for tag in lorem.tags}
        assert tagsLorem == {"Undergraduate", "Literary"}

        memes = Club.query.filter_by(code="penn-memes").first()
        assert memes is not None
        tagsMemes = {tag.name for tag in memes.tags}
        assert tagsMemes == {"Graduate", "Literary"}

        pppp = Club.query.filter_by(code="pppp").first()
        assert pppp is not None
        tagsPppp = {tag.name for tag in pppp.tags}
        assert tagsPppp == {"Undergraduate", "Academic"}

        locust = Club.query.filter_by(code="locustlabs").first()
        assert locust is not None
        tagsLocust = {tag.name for tag in locust.tags}
        assert tagsLocust == {"Undergraduate", "Graduate", "Technology"}


def testUserWithLegacyFavorites(testClient):
    """Test that a user created with legacy favorite clubs is set up 
    correctly.
    (return) None
    """
    with app.app_context():
        user = User.createNewUser(
            "legacyUser", "legacy@example.com", {"pppjo", "locustlabs"}
        )
        User.addUserToDb(user)
        
        retrievedUser = User.query.filter_by(
            username="legacyUser"
        ).first()
        assert retrievedUser is not None
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"pppjo", "locustlabs"}
        
        retrievedUser.addFavorite("penn-memes")
        db.session.commit()
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"pppjo", "locustlabs", "penn-memes"}
        
        retrievedUser.removeFavorite("pppjo")
        db.session.commit()
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"locustlabs", "penn-memes"}


def test_club_validation_errors(testClient):
    """Test that Club creation fails with invalid input."""
    with app.app_context():
        # Empty club code
        with pytest.raises(ValueError):
            Club.createNewClub("", "Valid Club Name", "Valid description that is long enough", set(), 0, True, False)
        
        # Short club name
        with pytest.raises(ValueError):
            Club.createNewClub("code", "ab", "Valid description that is long enough", set(), 0, True, False)
        
        # Short description
        with pytest.raises(ValueError):
            Club.createNewClub("code", "Valid Name", "short", set(), 0, True, False)
        
        # Negative member count
        with pytest.raises(ValueError):
            Club.createNewClub("code", "Valid Name", "Valid description that is long enough", set(), -1, True, False)
        
        # Neither undergrad nor grad allowed
        with pytest.raises(ValueError):
            Club.createNewClub("code", "Valid Name", "Valid description that is long enough", set(), 0, False, False)


def test_user_validation_errors(testClient):
    """Test that User creation fails with invalid input."""
    with app.app_context():
        # Short username
        with pytest.raises(ValueError):
            User.createNewUser("ab", "email@test.com", set())
        
        # Invalid email
        with pytest.raises(ValueError):
            User.createNewUser("username", "invalid-email", set())
        
        # Non-existent favorite club
        with pytest.raises(ValueError):
            User.createNewUser("username", "email@test.com", {"nonexistent-club"})


def test_club_update_validation(testClient):
    """Test club update methods with validation."""
    with app.app_context():
        club = Club.query.filter_by(code="pppjo").first()
        assert club is not None
        
        # Valid updates should work
        club.updateName("New Valid Club Name")
        assert club.name == "New Valid Club Name"
        
        club.updateMemberCount(100)
        assert club.memberCount == 100
        
        # Invalid updates should fail
        with pytest.raises(ValueError):
            club.updateName("ab")  # Too short
        
        with pytest.raises(ValueError):
            club.updateMemberCount(-1)  # Negative


def test_user_update_validation(testClient):
    """Test user update methods with validation."""
    with app.app_context():
        create_user()
        db.session.commit()
        
        user = User.query.filter_by(username="Josh").first()
        assert user is not None
        
        # Valid updates should work
        user.updateEmail("newemail@test.com")
        assert user.email == "newemail@test.com"
        
        user.updateUsername("NewUsername")
        assert user.username == "NewUsername"
        
        # Invalid updates should fail
        with pytest.raises(ValueError):
            user.updateEmail("invalid-email")
        
        with pytest.raises(ValueError):
            user.updateUsername("ab")  # Too short


def test_duplicate_prevention(testClient):
    """Test that duplicates are prevented."""
    with app.app_context():
        # Duplicate club code should fail
        with pytest.raises(ValueError):
            Club.createNewClub("pppjo", "New Club", "Valid description that is long enough", set(), 0, True, False)
        
        # Duplicate username should fail
        user1 = User.createNewUser("testuser", "test1@test.com", set())
        User.addUserToDb(user1)
        
        with pytest.raises(ValueError):
            User.createNewUser("testuser", "test2@test.com", set())
        
        # Duplicate email should fail
        with pytest.raises(ValueError):
            User.createNewUser("testuser2", "test1@test.com", set())
