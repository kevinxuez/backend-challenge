from app import db
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, CheckConstraint, Table, Column, \
    ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from validation import (validate_string, validate_integer, validate_boolean, 
                       validate_club_code, validate_tags, validate_email, sanitize_html)

clubTagAssociation = Table(
    'club_tag_association', db.metadata,
    Column('club_code', String, ForeignKey('club.code'), primary_key=True),
    Column('tag_name', String, ForeignKey('tag.name'), primary_key=True)
)

userClubAssociation = Table(
    'user_club_association', db.metadata,
    Column('user_id', Integer, ForeignKey('user.id'),
           primary_key=True),
    Column('club_code', String, ForeignKey('club.code'), primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tag'
    name = mapped_column(String, primary_key=True)
    clubs = relationship("Club", secondary=clubTagAssociation,
                         back_populates="tags")

    def __repr__(self):
        """Return a string representation of the Tag instance.
        (return) str: String in the format "<Tag name>".
        """
        return f"<Tag {self.name}>"

    @classmethod
    def createTag(cls, name):
        """Create and return a new Tag instance with the given name.
        (arg) name-str: The name of the tag.
        (bad input) name-non str: Undefined behavior if not a string.
        (return) Tag: A new Tag object.
        """
        validate_string(name, "Tag name", min_length=2, max_length=50)
        return cls(name=sanitize_html(name.strip()))

    @classmethod
    def addTagToDb(cls, newTag):
        """Add a Tag instance to the database if it is valid.
        (arg) newTag-Tag: The Tag instance to add.
        (bad input) newTag-non Tag: No action if not a Tag instance.
        (return) None
        """
        if isinstance(newTag, Tag):
            db.session.add(newTag)
            db.session.flush()


class Club(db.Model):
    __tablename__ = 'club'
    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    memberCount: Mapped[int] = mapped_column(Integer)
    undergraduatesAllowed: Mapped[bool] = mapped_column(Boolean)
    graduatesAllowed: Mapped[bool] = mapped_column(Boolean)
    dateCreated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        CheckConstraint('memberCount >= 0', name="Positive member count"),
        CheckConstraint('LENGTH(name) >= 3', name="No short name length"),
        CheckConstraint('undergraduatesAllowed OR graduatesAllowed',
                        name='check_at_least_one_student_type_allowed')
    )
    tags = relationship("Tag", secondary=clubTagAssociation,
                        back_populates="clubs")
    usersFavorited = relationship("User", secondary=userClubAssociation,
                                  back_populates="favoriteClubs")

    def handleTags(self, tagNames: set):
        """Associate the provided tag names with this Club instance.
        (arg) tagNames-set[str]: A set of tag names to associate.
        (bad input) tagNames-non set: Undefined behavior if not a set.
        (return) None
        """
        validate_tags(tagNames)
        for tagName in tagNames:
            sanitized_name = sanitize_html(tagName.strip())
            tag = Tag.query.filter_by(name=sanitized_name).first()
            if not tag:
                tag = Tag.createTag(sanitized_name)
                Tag.addTagToDb(tag)
            if not db.session.query(clubTagAssociation).filter_by(
                club_code=self.code, tag_name=tag.name).first():
                db.session.execute(
                    clubTagAssociation.insert().values(
                        club_code=self.code, tag_name=tag.name)
                )

    @classmethod
    def fromLegacyDbJson(cls, jsonData: dict):
        """Instantiate a Club from legacy JSON data.
        (arg) jsonData-dict: Dictionary containing legacy club data.
        (bad input) jsonData-missing keys: May raise KeyError.
        (return) Club: A new Club instance.
        """
        # Basic validation for legacy data
        if not isinstance(jsonData, dict):
            raise TypeError("jsonData must be a dictionary")
        
        required_fields = ["code", "name", "description"]
        for field in required_fields:
            if field not in jsonData:
                raise ValueError(f"Missing required field: {field}")
        
        tagsList = jsonData.get("tags", [])
        ugAllowed = "Undergraduate" in tagsList
        gAllowed = "Graduate" in tagsList
        
        # Validate basic fields
        validate_club_code(jsonData["code"])
        validate_string(jsonData["name"], "Club name", min_length=3, max_length=255)
        validate_string(jsonData["description"], "Description", min_length=10, max_length=2000)
        
        clubInstance = cls(
            code=jsonData["code"].strip().lower(),
            name=sanitize_html(jsonData["name"].strip()),
            description=sanitize_html(jsonData["description"].strip()),
            memberCount=jsonData.get("memberCount", 0),
            undergraduatesAllowed=ugAllowed,
            graduatesAllowed=gAllowed,
            dateCreated=datetime.utcnow()
        )
        clubInstance.handleTags(set(tagsList))
        return clubInstance

    @classmethod
    def fromCurrentDb(cls, jsonData: dict):
        """Instantiate a Club from current DB JSON data.
        (arg) jsonData-dict: Dictionary containing club data.
        (bad input) jsonData-missing keys: May raise errors.
        (return) Club: A new Club instance.
        """
        if not isinstance(jsonData, dict):
            raise TypeError("jsonData must be a dictionary")
        
        tagsList = jsonData.get("tags", [])
        # Parse dateCreated if it exists, otherwise use current time
        date_created = jsonData.get("dateCreated")
        if date_created:
            if isinstance(date_created, str):
                date_created = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
            elif not isinstance(date_created, datetime):
                date_created = datetime.utcnow()
        else:
            date_created = datetime.utcnow()
        
        # Validate all inputs
        validate_club_code(jsonData["code"])
        validate_string(jsonData["name"], "Club name", min_length=3, max_length=255)
        validate_string(jsonData["description"], "Description", min_length=10, max_length=2000)
        validate_integer(jsonData.get("memberCount", 0), "Member count", min_val=0, max_val=100000)
        validate_boolean(jsonData.get("undergraduatesAllowed"), "Undergraduates allowed")
        validate_boolean(jsonData.get("graduatesAllowed"), "Graduates allowed")
            
        clubInstance = cls(
            code=jsonData["code"].strip().lower(),
            name=sanitize_html(jsonData["name"].strip()),
            description=sanitize_html(jsonData["description"].strip()),
            memberCount=jsonData.get("memberCount", 0),
            undergraduatesAllowed=jsonData.get("undergraduatesAllowed"),
            graduatesAllowed=jsonData.get("graduatesAllowed"),
            dateCreated=date_created
        )
        clubInstance.handleTags(set(tagsList))
        return clubInstance

    @classmethod
    def createNewClub(cls, code: str, name: str, description: str,
                      tags: set[str], memberCount: int,
                      undergraduatesAllowed: bool,
                      graduatesAllowed: bool):
        """Create a new Club with comprehensive validation.
        (arg) code-str: Unique code for the club.
        (arg) name-str: Name of the club.
        (arg) description-str: Description of the club.
        (arg) tags-set[str]: Set of associated tag names.
        (arg) memberCount-int: Initial member count.
        (arg) undergraduatesAllowed-bool: Whether undergraduates are allowed.
        (arg) graduatesAllowed-bool: Whether graduates are allowed.
        (return) Club: A new Club instance.
        """
        # Validate all inputs
        validate_club_code(code)
        validate_string(name, "Club name", min_length=3, max_length=255)
        validate_string(description, "Description", min_length=10, max_length=2000)
        validate_tags(tags)
        validate_integer(memberCount, "Member count", min_val=0, max_val=100000)
        validate_boolean(undergraduatesAllowed, "Undergraduates allowed")
        validate_boolean(graduatesAllowed, "Graduates allowed")
        
        # Business logic validation
        if not (undergraduatesAllowed or graduatesAllowed):
            raise ValueError("At least one student type must be allowed")
        
        # Check for duplicate club code
        existing_club = cls.query.filter_by(code=code.strip().lower()).first()
        if existing_club:
            raise ValueError(f"Club with code '{code}' already exists")
        
        # Sanitize inputs
        name = sanitize_html(name.strip())
        description = sanitize_html(description.strip())
        code = code.strip().lower()
        
        clubInstance = cls(
            code=code,
            name=name,
            description=description,
            memberCount=memberCount,
            undergraduatesAllowed=undergraduatesAllowed,
            graduatesAllowed=graduatesAllowed,
            dateCreated=datetime.utcnow()
        )
        clubInstance.handleTags(tags)
        return clubInstance

    @classmethod
    def addClubToDb(cls, addedClub):
        """Add a Club instance to the database if valid.
        (arg) addedClub-Club: The Club instance to add.
        (bad input) addedClub-non Club: No action if invalid.
        (return) Club: The added Club instance.
        """
        if isinstance(addedClub, Club):
            db.session.add(addedClub)
            db.session.commit()
            return addedClub

    def toJson(self) -> dict:
        """Return a JSON-serializable dictionary of the Club.
        (return) dict: Dictionary with keys "code", "name", "description",
        "tags", "memberCount", "undergraduatesAllowed", "graduatesAllowed", and "dateCreated".
        """
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "tags": [tag.name for tag in self.tags],
            "memberCount": self.memberCount,
            "undergraduatesAllowed": self.undergraduatesAllowed,
            "graduatesAllowed": self.graduatesAllowed,
            "dateCreated": self.dateCreated.isoformat() if self.dateCreated else None
        }

    def updateName(self, newName: str):
        """Update club name with validation.
        (arg) newName-str: The new club name.
        (return) None
        """
        validate_string(newName, "Club name", min_length=3, max_length=255)
        self.name = sanitize_html(newName.strip())

    def updateDescription(self, newDescription: str):
        """Update description with validation.
        (arg) newDescription-str: The new description.
        (return) None
        """
        validate_string(newDescription, "Description", min_length=10, max_length=2000)
        self.description = sanitize_html(newDescription.strip())

    def addTag(self, newTag: str):
        """Add a new tag to the club.
        (arg) newTag-str: The tag name to add.
        (return) None
        """
        validate_string(newTag, "Tag", min_length=2, max_length=50)
        self.handleTags({newTag})

    def removeTag(self, removedTag: str) -> str:
        """Remove the specified tag from the club.
        (arg) removedTag-str: The tag name to remove.
        (return) str: The removed tag name; None if not found.
        """
        validate_string(removedTag, "Tag", min_length=2, max_length=50)
        tag = Tag.query.filter_by(name=removedTag).first()
        if tag and tag in self.tags:
            self.tags.remove(tag)

    def updateMemberCount(self, newCount: int):
        """Update member count with validation.
        (arg) newCount-int: The new member count.
        (return) int: The updated member count.
        """
        validate_integer(newCount, "Member count", min_val=0, max_val=100000)
        self.memberCount = newCount
        return self.memberCount

    def updateUndergraduatesAllowed(self, newStatus: bool):
        """Update undergraduates allowed with validation.
        (arg) newStatus-bool: The new status.
        (return) None
        """
        validate_boolean(newStatus, "Undergraduates allowed")
        
        # Business logic validation
        if not newStatus and not self.graduatesAllowed:
            raise ValueError("Cannot disable undergraduates if graduates are also disabled")
        
        self.undergraduatesAllowed = newStatus
        if newStatus:
            self.addTag("Undergraduate")
        else:
            self.removeTag("Undergraduate")

    def updateGraduatesAllowed(self, newStatus: bool):
        """Update graduates allowed with validation.
        (arg) newStatus-bool: The new status.
        (return) None
        """
        validate_boolean(newStatus, "Graduates allowed")
        
        # Business logic validation
        if not newStatus and not self.undergraduatesAllowed:
            raise ValueError("Cannot disable graduates if undergraduates are also disabled")
        
        self.graduatesAllowed = newStatus
        if newStatus:
            self.addTag("Graduate")
        else:
            self.removeTag("Graduate")

    def __repr__(self):
        """Return a string representation of the Club.
        (return) str: String in the format "<Club name>".
        """
        return f"<Club {self.name}>"


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    favoriteClubs = relationship("Club", secondary=userClubAssociation,
                                 back_populates="usersFavorited")

    def handleFavorite(self, favoriteNames: set):
        """Associate provided club codes as user's favorites.
        (arg) favoriteNames-set[str]: Set of club codes.
        (return) None
        """
        if not isinstance(favoriteNames, set):
            raise TypeError("Favorites must be a set")
        
        for clubCode in favoriteNames:
            validate_club_code(clubCode)
            club = Club.query.filter_by(code=clubCode).first()
            if not club:
                continue
            if not db.session.query(userClubAssociation).filter_by(
                club_code=club.code, user_id=self.id).first():
                db.session.execute(
                    userClubAssociation.insert().values(
                        club_code=club.code, user_id=self.id)
                )

    @classmethod
    def createNewUser(cls, username: str, email: str, favorites: set[str]):
        """Create a new User with comprehensive validation.
        (arg) username-str: The user's username.
        (arg) email-str: The user's email.
        (arg) favorites-set[str]: Set of favorite club codes.
        (return) User: A new User instance.
        """
        # Validate inputs
        validate_string(username, "Username", min_length=3, max_length=50)
        validate_string(email, "Email", min_length=5, max_length=255)
        validate_email(email)
        
        if not isinstance(favorites, set):
            raise TypeError("Favorites must be a set")
        
        # Check for duplicates
        if cls.query.filter_by(username=username.strip()).first():
            raise ValueError(f"Username '{username}' already exists")
        if cls.query.filter_by(email=email.strip().lower()).first():
            raise ValueError(f"Email '{email}' already exists")
        
        # Validate favorite club codes exist
        for club_code in favorites:
            validate_club_code(club_code)
            if not Club.query.filter_by(code=club_code).first():
                raise ValueError(f"Club with code '{club_code}' does not exist")
        
        # Sanitize inputs
        username = sanitize_html(username.strip())
        email = email.strip().lower()
        
        userInstance = cls(username=username, email=email)
        userInstance._pending_favorites = favorites
        return userInstance

    @classmethod
    def addUserToDb(cls, newUser):
        """Add a User instance to the database if valid.
        (arg) newUser-User: The User instance to add.
        (return) User: The added User instance.
        """
        if isinstance(newUser, User):
            db.session.add(newUser)
            db.session.flush()
            
            if hasattr(newUser, '_pending_favorites'):
                newUser.handleFavorite(newUser._pending_favorites)
                delattr(newUser, '_pending_favorites')
            
            db.session.commit()
            return newUser

    def toJson(self) -> dict:
        """Return a JSON-serializable dict of the User.
        (return) dict: Dictionary with "id", "username", "email", and "favorites".
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": [club.code for club in self.favoriteClubs]
        }

    def updateEmail(self, newEmail: str):
        """Update email with validation.
        (arg) newEmail-str: The new email address.
        (return) None
        """
        validate_string(newEmail, "Email", min_length=5, max_length=255)
        validate_email(newEmail)
        
        # Check for duplicate
        existing_user = User.query.filter_by(email=newEmail.strip().lower()).first()
        if existing_user and existing_user.id != self.id:
            raise ValueError(f"Email '{newEmail}' already exists")
        
        self.email = newEmail.strip().lower()

    def addFavorite(self, newFavorite: str):
        """Add favorite with validation.
        (arg) newFavorite-str: Club code to add.
        (return) None
        """
        validate_club_code(newFavorite)
        
        # Check if club exists
        club = Club.query.filter_by(code=newFavorite).first()
        if not club:
            raise ValueError(f"Club with code '{newFavorite}' does not exist")
        
        # Check if already favorited
        if club in self.favoriteClubs:
            raise ValueError(f"Club '{newFavorite}' is already in favorites")
        
        self.handleFavorite({newFavorite})

    def removeFavorite(self, removedFavoriteCode: str) -> str:
        """Remove the specified club from favorites.
        (arg) removedFavoriteCode-str: Club code to remove.
        (return) str: The removed club code; None if not found.
        """
        validate_club_code(removedFavoriteCode)
        club = Club.query.filter_by(code=removedFavoriteCode).first()
        if club in self.favoriteClubs:
            self.favoriteClubs.remove(club)

    def updateUsername(self, newUsername: str):
        """Update username with validation.
        (arg) newUsername-str: The new username.
        (return) None
        """
        validate_string(newUsername, "Username", min_length=3, max_length=50)
        
        # Check for duplicate
        existing_user = User.query.filter_by(username=newUsername.strip()).first()
        if existing_user and existing_user.id != self.id:
            raise ValueError(f"Username '{newUsername}' already exists")
        
        self.username = sanitize_html(newUsername.strip())

    def __repr__(self):
        """Return a string representation of the User.
        (return) str: String in the format "<User username>".
        """
        return f"<User {self.username}>"
