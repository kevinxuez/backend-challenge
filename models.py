from app import db
from sqlalchemy import String, Text, Integer, Boolean, CheckConstraint, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

club_tag_association = Table(
    'club_tag_association',
    db.metadata,
    Column('club_code', String, ForeignKey('club.code'), primary_key=True),
    Column('tag_name', String, ForeignKey('tag.name'), primary_key=True)  # Assuming you have a Tag model
)

user_club_association = Table(
    'user_club_association',
    db.metadata,  # Use your db's metadata
    Column('user_username', String, ForeignKey('user.username'), primary_key=True),
    Column('club_code', String, ForeignKey('club.code'), primary_key=True)
)

class Tag(db.Model):  # Define Tag Model
    __tablename__ = 'tag'
    name = mapped_column(String, primary_key=True)

    clubs = relationship("Club", secondary=club_tag_association, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"


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
        CheckConstraint('undergraduatesAllowed OR graduatesAllowed', name='check_at_least_one_student_type_allowed')
    )
    
    tags = relationship("Tag", secondary=club_tag_association, back_populates="clubs") # The relationship to tags

        
    @classmethod
    def fromLegacyDBjson(cls,  json_data: dict):
        tagsList=json_data.get("tags", [])
        ug_allowed = "Undergraduate" in tagsList
        g_allowed = "Graduate" in tagsList
        club = cls(
            code=json_data["code"],
            name=json_data["name"],
            description=json_data["description"],
            memberCount = json_data.get("memberCount", 0),
            undergraduatesAllowed=ug_allowed,
            graduatesAllowed=g_allowed
        )
        for tag_name in tagsList:
            tag = Tag.query.filter_by(name=tag_name).first()  
            if tag:
                club.tags.append(tag) 
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                club.tags.append(new_tag)
        return club

    
    @classmethod
    def fromCurrentDb(cls, json_data: dict):
        tagsList=json_data.get("tags", []),
        club = cls(
            code=json_data["code"],
            name=json_data["name"],
            description=json_data["description"],
            memberCount = json_data.get("memberCount", 0),
            undergraduatesAllowed = json_data.get["undergraduatesAllowed"],
            graduatesAllowed = json_data.get["graduatesAllowed"] 
        )
        
        for tag_name in tagsList:
            tag = Tag.query.filter_by(name=tag_name).first()  
            if tag:
                club.tags.append(tag) 
            else:
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                club.tags.append(new_tag)
        return club
    
    
        
    @classmethod
    def createNewClub(cls, 
                      code:str, 
                      name:str, 
                      description:str, 
                      tags:list[str], 
                      memberCount:int, 
                      undergraduatesAllowed:bool, 
                      graduatesAllowed:bool):
        club =   cls(
            code=code,
            name=name,
            description=description,
            memberCount=memberCount,
            undergraduatesAllowed=undergraduatesAllowed,
            graduatesAllowed=graduatesAllowed
        )
        for tag_name in tags:  # tags is now a set of tag *names*
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                club.tags.append(tag)
            else: # If the tag does not exist create it.
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                db.session.commit()
                club.tags.append(new_tag)

    
    @classmethod
    def addClubToDB(cls, addedClub):
        if isinstance(addedClub, Club):
            db.session.add(addedClub)
            db.session.commit()
            return addedClub
    
    def to_json(self) -> dict:
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
        self.name = newName
        db.session.commit()

    def updateDescription(self, newDescription: str):
        self.description = newDescription
        db.session.commit()

    def addTag(self, newTag: str):
        tag = Tag.query.filter_by(name=newTag).first()
        if tag:
            self.tags.append(tag)
            db.session.commit()
        else:
            new_tag = Tag(name=newTag)
            db.session.add(new_tag)
            db.session.commit()
            self.tags.append(new_tag)
        db.session.commit()
        
    def removeTag(self, removedTag:str) -> str:
        x = self.tags.remove(removedTag)
        db.session.commit()
        return x

    def updateMemberCount(self, newCount: int):
        x = self.memberCount = newCount
        db.session.commit()
        return x

    def updateUndergraduatesAllowed(self, newStatus: bool):
        self.undergraduatesAllowed = newStatus
        if (newStatus):
            self.addTag("Undergraduate")
        else:
            self.tags.remove("Undergraduate")
        db.session.commit()
                
    def updateGraduatesAllowed(self, newStatus: bool):
        self.graduatesAllowed = newStatus
        if (newStatus):
            self.addTag("Graduate")
        else:
            self.tags.remove("Graduate")
        db.session.commit()
        
    def __repr__(self):
        return f"<Tag {self.name}>"
    
    
    
        
        
        
class User(db.Model):
    __tablename__ = 'user' # Explicitly set tablename
    username: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    favorite_clubs = relationship("Club", secondary=user_club_association, back_populates="clubs_favorited")

    @classmethod
    def createNewUser(cls, 
                      username: str,
                      email: str,
                      favorites: set[str]
                      ):
        return cls(
            username=username,
            email=email,
            favorites=MutableSet(favorites)
        )

    @classmethod
    def addUserToDb(cls, newUser):
        if isinstance(newUser, User):
            newUser.favorites = list(newUser.favorites)  # Ensure it's serializable
            db.session.add(newUser)
            db.session.commit()
            return newUser

    def to_json(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "favorites": list(self.favorites),  # Convert set to list for JSON serialization
        }

    def updateEmail(self, newEmail: str):
        self.email = newEmail
        db.session.commit()

    def addFavorite(self, newFavorite: str):
        self.favorites.add(newFavorite)
        db.session.commit()

    def removeFavorite(self, removedFavorite: str) -> str:
        if removedFavorite in self.favorites:
            self.favorites.remove(removedFavorite)
            db.session.commit()
            return removedFavorite
        else:
            return "Favorite not found"

    def updateUsername(self, newUsername: str):
        self.username = newUsername
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"
    
        
    
    
    
  
  
    

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
