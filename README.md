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
Name (STR): Useful for recognition
Email (STR): Useful for future features (such as club application openings or updates)


## coding thoughts:

11:12 PM

0. wait i forgot to push any of these git changes
1. i've been generally working for like 40 minutes before this

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
4. currently reworking everything to fit the relationship, so adding tag stuff migth get miserable
5. oh my god i have to rework the tests too LOL

3:00

0. monster caffeine is actually so clutch
1. OK FINISHED OUT ALL THE KINKS AND BUGS IN THE RELATIONSHIP Model
2. I'm going to now develop the APIs then go back to adding features and bad-input catchers to the model functions
3. Cleaning up a lot of slop 
4. ok it's time to run through most of the code
5. i fell asleep that was really annoying

4:00

0. i need to remove all the db.session.commits in my model for better performance
1. let me look for the most efficient wway to do the search method
2. graduatses are actually trolling my code holy moly
3. ok everything seems good time to go to sleep for a bit then wake up and polish
4. ok time to docstring everything and then ill go to sleep, wake up in like 3-4 hours
5. i can do all my pure justification after i've started docStringing

5:00

0. bro imma go to sleep 
1. lemme use chatgpt to quickly format my stuff such that i have docstrings and a set charcter limit
2. "Hello Chatgpt
first, I prefer camelCase to any snake_case, so replace all of those
second, give every function a formatted docstring where 
   it's short (gives arg, any bad inputs, and returns) 
   and all the docstring text is one indent right of the funciton definition
third, reformat it such that the character limit is 80 characters" yo wait this is actually really nice
3. sleep!!!!
4. in total took me like 6 hours but i might do more tmr

post-nap goals:

1. actually writeup some stuff to justify my decision making 
2. add some more info to some of the docstrings that have additional info
3. deal with some of the bad input cases if i have time
4. writeup the 3 writeup answers
5. see if there are faster search methods out there

10:00 AM (little 4 hour nap)

1. I need to first make sure every function actually works like its supposed to, so postman time!
2. testing-wise, everything except createClub has worked. i think to fix createClub route I just need change with model method it uses
3. i fixed all my routes now it's time to do some i/o checking
4. my db.session.commits() are super messy but getting rid of them breaks some stuff so whatever
5. ok my test_models class now doesn't work but that's fine since I was relying on it to test when I didn't have postman

10:56 AM

1. might finally be time to start doing the writeup and justify a bunch of decisions
2. there's lwk a lot of stuff I'll put that somewhere else in my document
3. writeup long but interesting

woke up



