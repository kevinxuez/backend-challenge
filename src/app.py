from flask import request, jsonify
from .database import create_app, db, DB_FILE
from .models import *
from .validation import ValidationError, validate_json_input, validate_club_code, validate_tags, sanitize_html, validate_string

# Create app and initialize database
app = create_app()
db.init_app(app)

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

# ===== REVIEW ENDPOINTS =====

@app.route("/api/reviews", methods=["GET"])
def getReviews():
    """Return all reviews with pagination."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        
        if per_page > 100:
            return errorResponse("per_page cannot exceed 100", 400)
        
        reviews = Review.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "reviews": [review.toJson() for review in reviews.items],
            "total": reviews.total,
            "pages": reviews.pages,
            "current_page": page
        })
    except Exception as e:
        return errorResponse(f"Error fetching reviews: {str(e)}", 500)

@app.route("/api/reviews", methods=["POST"])
def createReview():
    """Create a new review."""
    try:
        data = request.get_json()
        validate_json_input(data, ["user_id", "club_code", "rating", "title"])
        
        review = Review.createNewReview(
            user_id=data["user_id"],
            club_code=data["club_code"],
            rating=data["rating"],
            title=data["title"],
            text=data.get("text", "")
        )
        
        Review.addReviewToDb(review)
        return jsonify(review.toJson()), 201
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/reviews/<int:review_id>", methods=["GET"])
def getReview(review_id):
    """Get specific review by ID."""
    review = getOr404(Review, id=review_id)
    if not review:
        return errorResponse("Review not found", 404)
    return jsonify(review.toJson())

@app.route("/api/reviews/<int:review_id>", methods=["PUT"])
def updateReview(review_id):
    """Update existing review."""
    try:
        data = request.get_json()
        validate_json_input(data)
        
        review = getOr404(Review, id=review_id)
        if not review:
            return errorResponse("Review not found", 404)
        
        # Apply updates with validation
        if "rating" in data:
            review.updateRating(data["rating"])
        if "title" in data:
            review.updateTitle(data["title"])
        if "text" in data:
            review.updateText(data["text"])
        
        error = commitChanges()
        if error:
            return error
        return jsonify(review.toJson())
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/reviews/<int:review_id>", methods=["DELETE"])
def deleteReview(review_id):
    """Delete review."""
    try:
        review = getOr404(Review, id=review_id)
        if not review:
            return errorResponse("Review not found", 404)
        
        db.session.delete(review)
        error = commitChanges()
        if error:
            return error
        return jsonify({"message": f"Review {review_id} deleted"}), 200
        
    except Exception as e:
        db.session.rollback()
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/clubs/<club_code>/reviews", methods=["GET"])
def getClubReviews(club_code):
    """Get all reviews for a specific club."""
    try:
        validate_club_code(club_code)
        
        club = getOr404(Club, code=club_code)
        if not club:
            return errorResponse("Club not found", 404)
        
        # Optional sorting and filtering
        sort_by = request.args.get("sort_by", "created_at")
        order = request.args.get("order", "desc")
        min_rating = request.args.get("min_rating", type=int)
        
        query = Review.query.filter_by(club_code=club_code)
        
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        if sort_by == "rating":
            if order == "desc":
                query = query.order_by(Review.rating.desc())
            else:
                query = query.order_by(Review.rating.asc())
        else:  # default to created_at
            if order == "desc":
                query = query.order_by(Review.created_at.desc())
            else:
                query = query.order_by(Review.created_at.asc())
        
        reviews = query.all()
        return jsonify([review.toJson() for review in reviews])
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/clubs/<club_code>/reviews/stats", methods=["GET"])
def getClubReviewStats(club_code):
    """Return review statistics for club."""
    try:
        validate_club_code(club_code)
        
        club = getOr404(Club, code=club_code)
        if not club:
            return errorResponse("Club not found", 404)
        
        reviews = club.reviews
        total_reviews = len(reviews)
        average_rating = club.get_average_rating()
        
        # Calculate rating distribution
        rating_distribution = {str(i): 0 for i in range(1, 11)}
        for review in reviews:
            rating_distribution[str(review.rating)] += 1
        
        return jsonify({
            "club_code": club_code,
            "club_name": club.name,
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": rating_distribution
        })
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/users/<int:user_id>/reviews", methods=["GET"])
def getUserReviews(user_id):
    """Get all reviews written by a specific user."""
    try:
        user = getOr404(User, id=user_id)
        if not user:
            return errorResponse("User not found", 404)
        
        reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()
        return jsonify([review.toJson() for review in reviews])
        
    except Exception as e:
        return errorResponse(f"Server error: {str(e)}", 500)

@app.route("/api/users/<int:user_id>/reviews/<club_code>", methods=["GET"])
def getUserClubReview(user_id, club_code):
    """Get user's review for specific club."""
    try:
        validate_club_code(club_code)
        
        review = Review.query.filter_by(user_id=user_id, club_code=club_code).first()
        if not review:
            return errorResponse("Review not found", 404)
        
        return jsonify(review.toJson())
        
    except (ValidationError, ValueError, TypeError) as e:
        return errorResponse(str(e), 400)
    except Exception as e:
        return errorResponse(f"Server error: {str(e)}", 500)

if __name__ == "__main__":
    app.run()
