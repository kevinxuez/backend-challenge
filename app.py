from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *
from validation import ValidationError, validate_json_input, validate_club_code, validate_tags, sanitize_html

def errorResponse(message, status=400):
    """Return a JSON error response.
    (arg) message-str: The error message.
    (arg) status-int: The HTTP status code.
    (return) tuple: (JSON response, status code).
    """
    return jsonify({"error": message}), status

def getOr404(model, **kwargs):
    """Return the first object matching kwargs or None.
    (arg) model-Class: The SQLAlchemy model to query.
    (arg) kwargs-dict: Filter criteria.
    (return) Model instance or None.
    """
    obj = model.query.filter_by(**kwargs).first()
    return None if not obj else obj

def listToJson(objects):
    """Return a JSON response for a list of objects.
    (arg) objects-list: A list of model instances with toJson method.
    (return) Response: A JSON response.
    """
    return jsonify([obj.toJson() for obj in objects])

def commitChanges():
    """Commit changes to the DB and handle exceptions.
    (return) None if successful, else a JSON error response.
    """
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return errorResponse(str(e), 400)
    return None

@app.route("/")
def main():
    """Return the welcome message.
    (return) str: Welcome text.
    """
    return "Welcome to Penn Club Review!"

@app.route("/api")
def api():
    """Return a simple API greeting.
    (return) Response: JSON greeting.
    """
    return jsonify("hi")

@app.route("/api/clubs", methods=["GET"])
def getClubs():
    """Return a list of all clubs as JSON.
    (return) Response: JSON list of clubs.
    """
    clubs = Club.query.all()
    clubsJson = [club.toJson() for club in clubs]
    return jsonify(clubsJson)

@app.route("/api/clubs", methods=["POST"])
def createClub():
    """Create a new club with full validation.
    (return) Response: JSON error response if input is missing.
    """
    try:
        data = request.get_json()
        validate_json_input(data, ["code", "name", "description", "undergraduatesAllowed", "graduatesAllowed"])
        
        tags = set(data.get("tags", []))
        club = Club.createNewClub(
            code=data["code"],
            name=data["name"],
            description=data["description"],
            tags=tags,
            memberCount=data.get("memberCount", 0),
            undergraduatesAllowed=data["undergraduatesAllowed"],
            graduatesAllowed=data["graduatesAllowed"]
        )
        Club.addClubToDb(club)
        error = commitChanges()
        if error:
            return error
        return jsonify(club.toJson()), 201
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/clubs/<clubCode>", methods=["PUT"])
def updateClub(clubCode):
    """Update a club with validation.
    (arg) clubCode-str: The club code.
    (return) Response: JSON representation of the updated club.
    """
    try:
        # Validate club code format
        validate_club_code(clubCode)
        
        data = request.get_json()
        validate_json_input(data)
        
        club = getOr404(Club, code=clubCode)
        if not club:
            return errorResponse("Club not found", 404)
        
        # Apply updates with validation
        if "name" in data:
            club.updateName(data["name"])
        if "description" in data:
            club.updateDescription(data["description"])
        if "memberCount" in data:
            club.updateMemberCount(data["memberCount"])
        if "undergraduatesAllowed" in data:
            club.updateUndergraduatesAllowed(data["undergraduatesAllowed"])
        if "graduatesAllowed" in data:
            club.updateGraduatesAllowed(data["graduatesAllowed"])
        if "tags" in data:
            validate_tags(data["tags"])
            club.tags.clear()
            club.handleTags(set(data["tags"]))
        
        error = commitChanges()
        if error:
            return error
        return jsonify(club.toJson())
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/clubs/<clubCode>", methods=["DELETE"])
def deleteClub(clubCode):
    """Delete a club by its code.
    (arg) clubCode-str: The club code.
    (return) Response: JSON confirmation message.
    """
    try:
        validate_club_code(clubCode)
        club = getOr404(Club, code=clubCode)
        if not club:
            return errorResponse("Club not found", 404)
        db.session.delete(club)
        error = commitChanges()
        if error:
            return error
        return jsonify({"message": f"Club {clubCode} deleted"}), 200
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/clubs/search", methods=["GET"])
def searchClubs():
    """Search clubs with query validation.
    (return) Response: JSON list of clubs matching the query.
    """
    try:
        query = request.args.get("query", "")
        if not query or not query.strip():
            return errorResponse("Query parameter is required and cannot be empty", 400)
        
        # Sanitize query
        query = sanitize_html(query.strip())
        
        # Limit query length
        if len(query) > 100:
            return errorResponse("Query cannot exceed 100 characters", 400)
        
        clubs = Club.query.filter(Club.name.ilike(f"%{query}%")).all()
        clubsJson = [club.toJson() for club in clubs]
        return jsonify(clubsJson)
        
    except Exception as e:
        return errorResponse(f"Search error: {str(e)}", 500)

@app.route("/api/users", methods=["GET"])
def getUsers():
    """Return a list of all users as JSON.
    (return) Response: JSON list of users.
    """
    users = User.query.all()
    usersJson = [user.toJson() for user in users]
    return jsonify(usersJson)

@app.route("/api/users", methods=["POST"])
def createUserRoute():
    """Create a user with validation.
    (return) Response: JSON representation of the new user.
    """
    try:
        data = request.get_json()
        validate_json_input(data, ["username", "email"])
        
        user = User.createNewUser(
            username=data["username"],
            email=data["email"],
            favorites=set(data.get("favorites", []))
        )
        User.addUserToDb(user)
        error = commitChanges()
        if error:
            return error
        return jsonify(user.toJson()), 201
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/users/<int:user_id>", methods=["GET"])
def getUser(user_id):
    """Get a user by their ID.
    (arg) user_id-int: The user's ID.
    (return) Response: JSON representation of the user.
    """
    user = getOr404(User, id=user_id)
    if not user:
        return errorResponse("User not found", 404)
    return jsonify(user.toJson())

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def updateUser(user_id):
    """Update an existing user.
    (arg) user_id-int: The user's ID.
    (return) Response: JSON representation of the updated user.
    """
    try:
        data = request.get_json()
        validate_json_input(data)
        
        user = getOr404(User, id=user_id)
        if not user:
            return errorResponse("User not found", 404)
        
        if "email" in data:
            user.updateEmail(data["email"])
        if "username" in data:
            user.updateUsername(data["username"])
        if "favorites" in data:
            user.favoriteClubs = []
            user.handleFavorite(set(data["favorites"]))
        
        error = commitChanges()
        if error:
            return error
        return jsonify(user.toJson())
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def deleteUser(user_id):
    """Delete a user by their ID.
    (arg) user_id-int: The user's ID.
    (return) Response: JSON confirmation message.
    """
    try:
        user = getOr404(User, id=user_id)
        if not user:
            return errorResponse("User not found", 404)
        db.session.delete(user)
        error = commitChanges()
        if error:
            return error
        return jsonify({"message": f"User {user.username} deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/tags/<tagName>", methods=["GET"])
def getTagClubs(tagName):
    """Return clubs associated with a tag.
    (arg) tagName-str: The tag name.
    (return) Response: JSON with tag and list of clubs.
    """
    try:
        validate_string(tagName, "Tag name", min_length=2, max_length=50)
        tag = Tag.query.filter_by(name=tagName).first()
        if not tag:
            return errorResponse("Tag not found", 404)
        clubList = [club.toJson() for club in tag.clubs]
        return jsonify({"tag": tagName, "clubs": clubList})
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)

@app.route("/api/clubs/<clubCode>/favoritedBy", methods=["GET"])
def getClubFavoritedBy(clubCode):
    """Return users who have favorited a club.
    (arg) clubCode-str: The club code.
    (return) Response: JSON with club and list of usernames.
    """
    try:
        validate_club_code(clubCode)
        club = getOr404(Club, code=clubCode)
        if not club:
            return errorResponse("Club not found", 404)
        users = [user.username for user in club.usersFavorited]
        return jsonify({"club": clubCode, "favorited_by": users})
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)

if __name__ == "__main__":
    app.run()
