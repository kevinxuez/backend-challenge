import pytest
from app import app, db
from models import Club, User
from bootstrap import create_user, load_data


@pytest.fixture(scope="function")
def test_client():  
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory SQLite for testing
    
    with app.app_context():
        db.create_all()  
        yield app.test_client()  
        db.session.remove()  
        db.drop_all() 
        

def test_data_loading(test_client): 
    create_user()
    load_data()

    josh = User.query.filter_by(username="Josh").first()
    assert josh is not None
    assert josh.email == "josh@upenn.edu"
    assert josh.favorites == {"penn-memes"}  

def test_club_loading(test_client):
    with app.app_context():
        load_data()
        
        pppjo = Club.query.filter_by(code="pppjo").first()
        assert pppjo is not None
        assert pppjo.name == "Penn Pre-Professional Juggling Organization"
        assert pppjo.description == "The PPPJO is looking for intense jugglers seeking to juggle their way to the top. Come with your juggling equipment (and business formal attire) to hone your skills in time for recruiting season!"
        
        penn_memes_club = Club.query.filter_by(code="penn-memes").first()
        assert penn_memes_club is not None
        assert penn_memes_club.name == "Penn Memes Club"
        assert penn_memes_club.tags == {"Graduate", "Undergraduate"}  # Set equality check
        
def test_club_update_methods(test_client):
    with app.app_context():
        club = Club.createNewClub(
            code="TESTCLUB",
            name="Test Club",
            description="A club for testing.",
            tags={"Undergraduate", "Test", "Club"},  
            memberCount=0,
            undergraduatesAllowed=True,
            graduatesAllowed=False
        )
        Club.addClubToDB(club)

        # Test updateName
        club.updateName("Updated Test Club")
        assert club.name == "Updated Test Club"

        # Test updateDescription
        club.updateDescription("An updated description.")
        assert club.description == "An updated description."

        # Test addTag and removeTag
        club.addTag("New Tag")
        assert "New Tag" in club.tags
        club.removeTag("New Tag")
        assert "New Tag" not in club.tags

        # Test updateMemberCount
        club.updateMemberCount(10)
        assert club.memberCount == 10

        # Test updateGraduatesAllowed
        club.updateGraduatesAllowed(True)
        assert club.graduatesAllowed is True
        assert "Graduate" in club.tags  # Check if "Graduate" is added to the tags.

        # Test updateUndergraduatesAllowed
        club.updateUndergraduatesAllowed(False)
        assert club.undergraduatesAllowed is False
        assert "Undergraduate" not in club.tags  # Check if "Undergraduate" is removed from the tags.
        
        # Retrieve the club from the database to ensure changes are persisted
        retrieved_club = Club.query.filter_by(code="TESTCLUB").first()
        assert retrieved_club.name == "Updated Test Club"
        assert retrieved_club.description == "An updated description."
        assert retrieved_club.memberCount == 10
        assert retrieved_club.undergraduatesAllowed is False
        assert retrieved_club.graduatesAllowed is True
        assert "Graduate" in retrieved_club.tags
        assert "Undergraduate" not in retrieved_club.tags

def test_user_update_methods(test_client):
    with app.app_context():
        user = User.createNewUser(
            username="testuser",
            email="test@example.com",
            favorites={"club1", "club2"}  # Using a set
        )
        User.addUserToDb(user)

        # Test updateEmail
        user.updateEmail("new_email@example.com")
        assert user.email == "new_email@example.com"

        # Test addFavorite and removeFavorite
        user.addFavorite("club3")
        assert "club3" in user.favorites
        user.removeFavorite("club3")
        assert "club3" not in user.favorites

        # Test updateUsername
        user.updateUsername("new_testuser")
        assert user.username == "new_testuser"

        retrieved_user = User.query.filter_by(username="new_testuser").first()
        assert retrieved_user.email == "new_email@example.com"
        assert retrieved_user.favorites == {"club1", "club2"}  # Set equality check
        assert retrieved_user.username == "new_testuser"


