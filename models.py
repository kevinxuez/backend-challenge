from app import db
from sqlalchemy import String, Text, Integer, Boolean, CheckConstraint, Table, Column, \
    ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

clubTagAssociation = Table(
    'club_tag_association', db.metadata,
    Column('club_code', String, ForeignKey('club.code'), primary_key=True),
    Column('tag_name', String, ForeignKey('tag.name'), primary_key=True)
)

userClubAssociation = Table(
    'user_club_association', db.metadata,
    Column('user_username', String, ForeignKey('user.username'),
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
        return cls(name=name)

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
        for tagName in tagNames:
            tag = Tag.query.filter_by(name=tagName).first()
            if not tag:
                tag = Tag.createTag(tagName)
                Tag.addTagToDb(tag)
            if not db.session.query(clubTagAssociation).filter_by(
                club_code=self.code, tag_name=tag.name).first():
                db.session.execute(
                    clubTagAssociation.insert().values(
                        club_code=self.code, tag_name=tag.name)
                )
        db.session.commit()

    @classmethod
    def fromLegacyDbJson(cls, jsonData: dict):
        """Instantiate a Club from legacy JSON data.
        (arg) jsonData-dict: Dictionary containing legacy club data.
        (bad input) jsonData-missing keys: May raise KeyError.
        (return) Club: A new Club instance.
        """
        tagsList = jsonData.get("tags", [])
        ugAllowed = "Undergraduate" in tagsList
        gAllowed = "Graduate" in tagsList
        clubInstance = cls(
            code=jsonData["code"],
            name=jsonData["name"],
            description=jsonData["description"],
            memberCount=jsonData.get("memberCount", 0),
            undergraduatesAllowed=ugAllowed,
            graduatesAllowed=gAllowed
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
        tagsList = jsonData.get("tags", [])
        clubInstance = cls(
            code=jsonData["code"],
            name=jsonData["name"],
            description=jsonData["description"],
            memberCount=jsonData.get("memberCount", 0),
            undergraduatesAllowed=jsonData.get("undergraduatesAllowed"),
            graduatesAllowed=jsonData.get("graduatesAllowed")
        )
        clubInstance.handleTags(set(tagsList))
        return clubInstance

    @classmethod
    def createNewClub(cls, code: str, name: str, description: str,
                      tags: set[str], memberCount: int,
                      undergraduatesAllowed: bool,
                      graduatesAllowed: bool):
        """Create a new Club instance with the provided details.
        (arg) code-str: Unique code for the club.
        (arg) name-str: Name of the club.
        (arg) description-str: Description of the club.
        (arg) tags-set[str]: Set of associated tag names.
        (bad input) tags-non set: Undefined if not a set.
        (arg) memberCount-int: Initial member count.
        (bad input) memberCount-negative int: Negative values may be invalid.
        (arg) undergraduatesAllowed-bool: Whether undergraduates are allowed.
        (arg) graduatesAllowed-bool: Whether graduates are allowed.
        (return) Club: A new Club instance.
        """
        clubInstance = cls(
            code=code,
            name=name,
            description=description,
            memberCount=memberCount,
            undergraduatesAllowed=undergraduatesAllowed,
            graduatesAllowed=graduatesAllowed
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
        "tags", "memberCount", "undergraduatesAllowed", and "graduatesAllowed".
        """
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "tags": [tag.name for tag in self.tags],
            "memberCount": self.memberCount,
            "undergraduatesAllowed": self.undergraduatesAllowed,
            "graduatesAllowed": self.graduatesAllowed
        }

    def updateName(self, newName: str):
        """Update the club's name.
        (arg) newName-str: The new club name.
        (bad input) newName-non str: Undefined if not a string.
        (return) None
        """
        self.name = newName
        db.session.commit()

    def updateDescription(self, newDescription: str):
        """Update the club's description.
        (arg) newDescription-str: The new description.
        (bad input) newDescription-non str: Undefined if not a string.
        (return) None
        """
        self.description = newDescription
        db.session.commit()

    def addTag(self, newTag: str):
        """Add a new tag to the club.
        (arg) newTag-str: The tag name to add.
        (bad input) newTag-non str: Undefined if not a string.
        (return) None
        """
        self.handleTags({newTag})
        db.session.commit()

    def removeTag(self, removedTag: str) -> str:
        """Remove the specified tag from the club.
        (arg) removedTag-str: The tag name to remove.
        (bad input) removedTag-non str: Undefined if not a string.
        (return) str: The removed tag name; None if not found.
        """
        tag = Tag.query.filter_by(name=removedTag).first()
        if tag and tag in self.tags:
            self.tags.remove(tag)
        db.session.commit()

    def updateMemberCount(self, newCount: int):
        """Update the club's member count.
        (arg) newCount-int: The new member count.
        (bad input) newCount-non int: Undefined if not an integer.
        (return) int: The updated member count.
        """
        self.memberCount = newCount
        db.session.commit()
        return self.memberCount

    def updateUndergraduatesAllowed(self, newStatus: bool):
        """Update the undergraduates allowed flag.
        (arg) newStatus-bool: The new status.
        (bad input) newStatus-non bool: Undefined if not a bool.
        (return) None
        """
        self.undergraduatesAllowed = newStatus
        if newStatus:
            self.addTag("Undergraduate")
        else:
            self.removeTag("Undergraduate")
        db.session.commit()

    def updateGraduatesAllowed(self, newStatus: bool):
        """Update the graduates allowed flag.
        (arg) newStatus-bool: The new status.
        (bad input) newStatus-non bool: Undefined if not a bool.
        (return) None
        """
        self.graduatesAllowed = newStatus
        if newStatus:
            self.addTag("Graduate")
        else:
            self.removeTag("Graduate")
        db.session.commit()

    def __repr__(self):
        """Return a string representation of the Club.
        (return) str: String in the format "<Club name>".
        """
        return f"<Club {self.name}>"


class User(db.Model):
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    favoriteClubs = relationship("Club", secondary=userClubAssociation,
                                 back_populates="usersFavorited")

    def handleFavorite(self, favoriteNames: set):
        """Associate provided club codes as user's favorites.
        (arg) favoriteNames-set[str]: Set of club codes.
        (bad input) favoriteNames-non set: Undefined if not a set.
        (return) None
        """
        for clubCode in favoriteNames:
            club = Club.query.filter_by(code=clubCode).first()
            if not club:
                continue
            if not db.session.query(userClubAssociation).filter_by(
                club_code=club.code, user_username=self.username).first():
                db.session.execute(
                    userClubAssociation.insert().values(
                        club_code=club.code, user_username=self.username)
                )
        db.session.commit()

    @classmethod
    def createNewUser(cls, username: str, email: str, favorites: set[str]):
        """Create a new User instance.
        (arg) username-str: The user's username.
        (arg) email-str: The user's email.
        (arg) favorites-set[str]: Set of favorite club codes.
        (bad input) favorites-non set: Undefined if not a set.
        (return) User: A new User instance.
        """
        userInstance = cls(username=username, email=email)
        userInstance.handleFavorite(favorites)
        return userInstance

    @classmethod
    def addUserToDb(cls, newUser):
        """Add a User instance to the database if valid.
        (arg) newUser-User: The User instance to add.
        (bad input) newUser-non User: No action if invalid.
        (return) User: The added User instance.
        """
        if isinstance(newUser, User):
            db.session.add(newUser)
            db.session.commit()
            return newUser

    def toJson(self) -> dict:
        """Return a JSON-serializable dict of the User.
        (return) dict: Dictionary with "username", "email", and "favorites".
        """
        return {
            "username": self.username,
            "email": self.email,
            "favorites": [club.code for club in self.favoriteClubs]
        }

    def updateEmail(self, newEmail: str):
        """Update the user's email.
        (arg) newEmail-str: The new email address.
        (bad input) newEmail-non str: Undefined if not a string.
        (return) None
        """
        self.email = newEmail
        db.session.commit()

    def addFavorite(self, newFavorite: str):
        """Add a club to the user's favorites.
        (arg) newFavorite-str: Club code to add.
        (bad input) newFavorite-non str: Undefined if not a string.
        (return) None
        """
        self.handleFavorite({newFavorite})
        db.session.commit()

    def removeFavorite(self, removedFavoriteCode: str) -> str:
        """Remove the specified club from favorites.
        (arg) removedFavoriteCode-str: Club code to remove.
        (bad input) removedFavoriteCode-non str: Undefined if not a string.
        (return) str: The removed club code; None if not found.
        """
        club = Club.query.filter_by(code=removedFavoriteCode).first()
        if club in self.favoriteClubs:
            self.favoriteClubs.remove(club)
        db.session.commit()

    def updateUsername(self, newUsername: str):
        """Update the user's username.
        (arg) newUsername-str: The new username.
        (bad input) newUsername-non str: Undefined if not a string.
        (return) None
        """
        self.username = newUsername
        db.session.commit()

    def __repr__(self):
        """Return a string representation of the User.
        (return) str: String in the format "<User username>".
        """
        return f"<User {self.username}>"
