import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app
from src.database import db, DB_FILE
from src.models import Club, User

def create_user():
    """Create a new user with preset favorite clubs.
    (return) None
    """
    favSet = {"penn-memes"}
    josh = User.createNewUser("Josh", "josh@upenn.edu", favSet)
    User.addUserToDb(josh)

def load_data():
    """Load club data from 'clubs.json' and add to the database.
    (return) None
    """
    # Path from scripts directory to data directory
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "clubs.json")
    with open(data_path, "r") as file:
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
        load_data()  # Load clubs first
        create_user()  # Then create user with favorites
