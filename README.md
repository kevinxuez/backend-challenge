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
2. Run `python3 bootstrap.py` to create the database and populate it.
3. Use `flask run` to run the project.
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




Decision Justification:

Club Model fields + justification:
Name (STR): Given, useful for filtering
Code(STR): Given, useful for filtering
Description(STR): Given, useful for filtering
Tags(STRING ARRAY): Given, useful for fitering
Main Focus (STR): could be used to identify the main type of a club, though would conflict with tags because both are generally used for the same purpose
MemberCount (INT): Allows for us to display the membersize for certain clubs. Given that our old data starsts
UndergraduatesAllowed (BOOL): Useful for future registration
GraduatesAllowed(BOOL): Useful for future registration

User Model fields + justifications:
Name (STR): Useful for recognition
Email (STR): Useful for future features (such as club application openings or updates)
Favorites (CLUB OR STRING ARRAY): Needed to implement the favorite feature



current thoughts:
11:12 PM
0. wait i forgot to push any of these git changes

11:37 PM
0. let's polish up steps 1-3 before i even do any api work
1. ran throgh all my models.py and changed them back to python types that are mapped to a SQL types, misread the documentation and didn't map them to SQL types
2. added some basic CheckConstraints to practice with them and get some more data, will add some more when I add the functions
3. lemme go refresh on pytest and find how to test this program without postman, I'll do the postman testing later
4. forgot to install pytest as a module
5. why is running "poetry shell" giving me this bs "The command "shell" does not exist."

11:51
0. wait ok so I have poetry installed and i'm in the powershell state but not in the poetry shell state
1. I had to visit chatgpt for this one LOL its telling my environmental variable changing is the answer which is not GOOD
2. wait i had the pyproject.toml in my directory the entire time and I actually was in poetry, the issue was just that running poetry shell inside a poetry shell doesn't tell you you're in one but instead just breaks
3. ok back to testing
4. BRO I HAVE MATH 3140 HW DUE AT MIDNIGHT TODAY !!!!!!! TURN TS IN
5. turned in, back to testing
6. oh wait, pytest in vscode is ran using test CheckConstraints

12:17
0. got sucked back into the poetry shell just to search ts up on reddit and find that they updated it like a month ago to be a plugin
1. wait literally all of my issues were because the poetry devs completely changed how poetry shell works to some random plugin holy 
2. tests done i love life
3. adding more tests because cis 1210 trauma

12:46
0. let's finish up testing my add/minus/update/modify features and then we can safely use them with APIs
1. my add's for favorites+lists were both cooked
2. bro there was a mutableList that I could have used the whole time no wonder this makes a lot more sense now
3. have to account for keyerrors if the thing isn't there
4. why df did I write JSON().with_variant(with_variant) for my list[str]
5. yo i hate mutablelist bs lemme just switch to mutableSet because there's also faster search runtime 

1:30
0. took a small break and then fixed everything to be mutableSet
1. ok might FINALLY be time to work on the APIS holy 
2. wait no this mutable stuff still doesn't wrok LOL

2:00
0. stuck on mutability LOL
1. no more mutableSet let's try the relationship route
2. relationships seem to work a lot better then mutableSet so that's a good STRING
3. my sleeps gonna get cooked when i have to actually implement these APIS


