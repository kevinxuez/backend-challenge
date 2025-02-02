import os
import json
from app import app, db, DB_FILE
from models import Club, User

def createUser():
    """Create a new user with preset favorite clubs.
    (return) None
    """
    favSet = {"penn-memes"}
    josh = User.createNewUser("Josh", "josh@upenn.edu", favSet)
    User.addUserToDb(josh)

def loadData():
    """Load club data from 'clubs.json' and add to the database.
    (return) None
    """
    with open("clubs.json", "r") as file:
        clubData = json.load(file)
        for club in clubData:
            Club.addClubToDb(Club.fromLegacyDbJson(club))
    db.session.commit()

if __name__ == "__main__":
    localDbFile = f"instance/{DB_FILE}"
    if os.path.exists(localDbFile):
        os.remove(localDbFile)
    with app.app_context():
        db.create_all()
        createUser()
        loadData()
