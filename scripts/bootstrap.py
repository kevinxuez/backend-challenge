import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app
from src.database import db, DB_FILE
from src.models import Club, User, Review

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

def create_sample_reviews():
    """Create sample reviews for existing clubs."""
    sample_reviews = [
        {
            "user_id": 1,  # Josh
            "club_code": "pppjo",
            "rating": 9,
            "title": "Amazing juggling experience!",
            "text": "The pre-professional atmosphere really helped me prepare for recruiting. Great community!"
        },
        {
            "user_id": 1,
            "club_code": "penn-memes",
            "rating": 8,
            "title": "Great meme community",
            "text": "Love the literary memes and graduate-level humor. Very welcoming environment."
        }
    ]
    
    for review_data in sample_reviews:
        try:
            review = Review.createNewReview(**review_data)
            Review.addReviewToDb(review)
        except ValueError as e:
            print(f"Skipping review creation: {e}")

if __name__ == "__main__":
    localDbFile = f"instance/{DB_FILE}"
    if os.path.exists(localDbFile):
        os.remove(localDbFile)
    with app.app_context():
        db.create_all()
        load_data()  
        create_user()  
        create_sample_reviews() 
