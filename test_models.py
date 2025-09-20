import pytest
from app import app, db
from models import Club, User
from bootstrap import create_user, load_data

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


def testDataLoading(testClient):
    """Test that user data and club data load correctly.
    (return) None
    """
    with app.app_context():
        load_data()
        create_user()
        db.session.commit()  # Explicitly commit after loading data
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
        load_data()
        db.session.commit()  # Commit after loading
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
        load_data()
        db.session.commit()  # Commit after loading
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
        load_data()
        db.session.commit()  # Commit loaded data first
        
        user = User.createNewUser(
            "legacyUser", "legacy@example.com", {"pppjo", "locustlabs"}
        )
        User.addUserToDb(user)  # This method still commits internally
        
        retrievedUser = User.query.filter_by(
            username="legacyUser"
        ).first()
        assert retrievedUser is not None
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"pppjo", "locustlabs"}
        
        retrievedUser.addFavorite("penn-memes")
        db.session.commit()  # Manually commit changes
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"pppjo", "locustlabs", "penn-memes"}
        
        retrievedUser.removeFavorite("pppjo")
        db.session.commit()  # Manually commit changes
        favoriteCodes = {club.code for club in retrievedUser.favoriteClubs}
        assert favoriteCodes == {"locustlabs", "penn-memes"}
