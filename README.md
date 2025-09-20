# Penn Labs Backend Challenge

## Documentation

Fill out this section as you complete the challenge!

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipx`
   - `brew install pipx` (macOS)
   - See instructions here https://github.com/pypa/pipx for other operating systems
4. Install `poetry`
   - `pipx install poetry`
5. Install packages using `poetry install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

(NEW)

- `validation.py`: Standard validation error class and input validation functions 

## Developing

(I edited the file structure so running the app is a little different)

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Activate the Poetry shell with `poetry shell`.
2. Run `python3 -m scripts.bootstrap.py` to create the database and populate it.
3. Use `cd src`, then `flask run` after going inside src to run the project.
4. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-862656cb8b7048db95aaa4e2935b77e5).
5. Document your work in this `README.md` file.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `poetry add <package_name>` within the directory. Make sure to document your additions.


Installed Modules
flask
flask_sqlalchemy
sqlalchemy
pytest

## Reflection:

Honestly, this project was fun to edit and improve upon. I enjoyed refining the code and adding new features, especially the review system. The most challenging part was actually migrating all the files to the new structured file system, as it was a tedious effort to change all the imports manually. One thing I made sure to do was implement all my "future improvements" from the previous writeup, which included input validation, reducing commits, and adding user_id and datetime fields.

When it comes to new features, the main thing I added was a review system that allows users to leave reviews for clubs. This involved creating a new Review model, adding API endpoints for creating and retrieving reviews, and updating the Club model to include a relationship with reviews. I also made sure to add tests for the new functionality.

## Future Improvements (1):

1 - Commenting System: Implement an actual commenting system to my reviews, now that I've already made a review system
2 - History/Versioning: Implement a history/versioning system for clubs and reviews so that users can see how things have changed over time
3 - Likes/Upvotes: Implement a like/upvote system for reviews and comments to allow users to show appreciation for helpful content

## API Decision Justification:

**Helper Functions Design:**
- `errorResponse()`: Standardized error handling makes respond to errors consistent
- `getOr404()`: Allows for a cleaner way to handle errors when qurying the database
- `listToJson()`: Centralizes JSON serialization for collections
- `commitChanges()`: Wraps database commits with proper exception handling and rollback functionality, allowing everybody to view changes

**Search Implementation:**
- Used SQLAlchemy's `ilike()` for case-insensitive search club names and descriptions
- Chose database-level filtering over application-level filtering for better performance with larger datasets

**RESTful Endpoint Design:**
- Followed REST conventions: GET for retrieval, POST for creation, PUT for updates, DELETE for removal
- Used descriptive URL patterns (`/api/clubs/<code>`, `/api/users/<id>/reviews`) for intuitive navigation

**Review System Architecture:**
- Designed nested endpoints (`/api/clubs/<code>/reviews`, `/api/users/<id>/reviews`) to reflect data relationships
- Added statistics endpoints (`/api/clubs/<code>/reviews/stats`) for analytical capabilities

## Model Decision Justification:

**Tag Model:**
- `Name (str)`: Serves as the primary identifier for tag categorization and searching
- `Clubs (relationship with Club)`: Implements a many-to-many relationship that provides flexibility for tag management and enables dynamic association between tags and clubs without data duplication

**Club Model:**
- `Name (str)`: Provides human-readable club identification for display purposes
- `Code (str)`: Acts as the primary key and immutable identifier, ensuring consistent referencing across the application while remaining URL-friendly
- `Description (str)`: Stores detailed club information for user discovery and decision-making
- `MemberCount (int)`: Enables sorting, filtering, and ranking functionality based on club popularity and size
- `UndergraduatesAllowed (bool)`: Provides eligibility filtering capability, designed for future enrollment system integration
- `GraduatesAllowed (bool)`: Complements undergraduate eligibility, supporting comprehensive access control for different student populations
- `Tags (relationship with Tag)`: Establishes many-to-many relationship for flexible categorization and advanced search functionality
- `UsersFavorited (relationship with UsersFavorited)`: Tracks user preferences through a many-to-many relationship, enabling personalized recommendations and user engagement metrics

**User Model:**
- `Username (str)`: Originally designed as primary key for simplicity, though this creates limitations for username changes (noted for future refactoring)
- `Email (str)`: Provides unique user identification alternative and enables future features like notifications, password recovery, and session management
- `FavoritedClubs (relationship with clubs)`: Implements user preference tracking through many-to-many relationship, supporting personalized user experiences and club recommendation algorithms

**Review Model:**
- `ID (int)`: Auto-incrementing primary key ensuring unique identification for each review
- `User_ID (int)`: Foreign key establishing relationship with User model, enabling user-specific review tracking and management
- `Club_Code (str)`: Foreign key linking to Club model, creating the core association between reviews and clubs
- `Rating (int)`: Numerical rating (1-10) with database constraints for data integrity and analytical capabilities
- `Title (str)`: Required review title (5-100 characters) providing quick review identification and searchability
- `Text (str)`: Optional detailed review content (up to 2000 characters) allowing comprehensive user feedback
- `Created_At (datetime)`: Timestamp tracking review creation for chronological ordering and audit trails
- `Updated_At (datetime)`: Automatic timestamp updates for tracking review modifications and version control
- `User (relationship)`: Back-reference to User model enabling efficient query navigation and user review aggregation
- `Club (relationship)`: Back-reference to Club model supporting club review collections and rating calculations



## Development Process:

OLD:

1. Started with SQLAlchemy model design, initially struggled with Poetry shell configuration and spent significant time debugging mutableSet/mutableList approaches before settling on SQLAlchemy relationships for better data handling.

2. Implemented comprehensive pytest testing suite, then built Flask API endpoints with proper error handling and JSON serialization. Had to refactor several model methods to work seamlessly with the relationship-based approach.

3. Added docstrings to all functions, refactored duplicate code into helper methods (errorResponse, getOr404, listToJson, commitChanges), and performed extensive API testing via Postman to ensure all endpoints work correctly.

NEW: 

1.
 Removed duplicate code into helper methods (errorResponse, getOr404, listToJson, commitChanges), and performed extensive API testing via Postman to ensure all endpoints work correctly.
 Added a user_id primary key to the User() model for better database practices and enable username changes and duplicate usernames
 Added a datetimeCreated field to Club() model to enable sorting by creation time.

2. 
Added I/O validation to API endpoints to catch bad input data and return appropriate error messages.
Added I/O validation to model methods to ensure data integrity at the model level.
Wrote additional pytest tests to cover new validation logic and edge cases.

3. 
Refactored file structure and improved encapsulation by adding getter methods to models.
Reviewed and cleaned up code for readability and maintainability.

4. 
Added a fully functional review system with a Review() model, API endpoints for creating and retrieving reviews, and integration with the Club() and User() models.