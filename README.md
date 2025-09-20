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

## Developing

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




## API Decision Justification:

errorResponse, getOr404, listToJson, and commitChanges: These functions were just results of me looking through my API code and seeing a bunch of duplicate stuff so I decided to refactorize it to make it look better

API/Search: I ultimately decided on using "ilike" because I'm not familiar enough to find faster methods so I decided to go with the seemingly-most trusted option possible

## Model Decision Justification:

Tag Model fields:
Name (str): needed for identification

Clubs (relationship with Club): this makes it a lot easier to keep track of tags and allows for there to be mutability when it comes to tag-model relations, something I was struggling for a bit

Club Model fields:
Name (str): acts as the primary key and is an obvious 

Code(str): acts as the primary key and is useful for filtering. I made sure to never add a function that changes the code

Description(str): useful for displaying

MemberCount (int): allows for us to display the membersize for certain clubs, which comes in handy for filtering and ranking clubs

UndergraduatesAllowed (bool): just a cheap datapoint that will come in handy if I wanted to replicate something more advanced like signups

GraduatesAllowed(bool): just a cheap datapoint that will come in handy if I wanted to replicate something more advanced like signups

Tags (relationship with Tag): this makes it super convenient to keep track of which tags each club has

UsersFavorited (relationship with UsersFavorited): this makes it super convenient to keep track of which people are interested in each club 

User Model fields:
Username (str): acts as primary key, which is a flaw, and is not changeable

Email (str): this will come in useful for either user identification/session stuff I make in the future or just for sending alerts and stuff

FavoritedClubs(relationship with clubs): this ties a User to a bunch of clubs that way it can keep track of information like that


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
Added a fully functional review system