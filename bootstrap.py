import os

from app import app, db, DB_FILE, jsonify

from models import Club, User

import json


def create_user():
    favSet = {"penn-memes"}
    Josh = User.createNewUser("Josh", "josh@upenn.edu", favSet)
    User.addUserToDb(Josh)
    

def load_data():
    with open('clubs.json', 'r') as file:
        club_data = json.load(file)
        for club in club_data:
            Club.addClubToDB(Club.fromLegacyDBjson(club))
        
def display_clubs():
    """Fetch all clubs and return them as a JSON response."""
    with app.app_context():
        clubs = Club.query.all()
        club_list = [club.to_json() for club in clubs]  # Convert each club to JSON
        return jsonify(club_list)  # Return the list as a JSON response

# No need to modify the below code.
if __name__ == "__main__":
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = f"instance/{DB_FILE}"
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
        create_user()
        load_data()
        display_clubs()

