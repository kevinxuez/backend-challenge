from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column



class Club(db.Model):
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column
    description: Mapped[str]
    tags: Mapped [set[str]] = mapped_column(JSON)
    memberCount: Mapped[str]
    undergraduatesAllowed: Mapped[bool]
    graduatesAllowed: Mapped[bool]
    
    def typeOfStudentAllowedAnalysis(self, club_data: dict) -> dict:
        ugAllowed = False
        gAllowed = False
        if "tags" in club_data and isinstance(club_data["tags"], set):
            if "Undergraduate" in club_data["tags"]:
                ugAllowed = True
            if "Graduate" in club_data["tags"]:
                gAllowed = True
        club_data["undergraduatesAllowed"] = ugAllowed
        club_data["graduatesAllowed"] = gAllowed
        return club_data
    
    @classmethod
    def fromLegacyDBjson(cls,  json_data: dict):
        initial_db = cls(
            code=json_data["code"],
            name=json_data["name"],
            description=json_data["description"],
            tags=json_data.get("tags", []),
            memberCount = json_data.get("memberCount", 0)
        )
        return [cls.typeOfStudentAllowedAnalysis(club) for club in initial_db]
    
    
    @classmethod
    def fromCurrentDb(cls, json_data: dict):
        return cls(
            code=json_data["code"],
            name=json_data["name"],
            description=json_data["description"],
            tags=json_data.get("tags", []),
            memberCount = json_data.get("memberCount", 0),
            undergraduatesAllowed = json_data.get["undergraduatesAllowed"],
            graduatesAllowed = json_data.get["graduatesAllowed"] 
        )
        
    @classmethod
    def createNewClub(cls, 
                      code:str, 
                      name:str, 
                      description:str, 
                      tags:set[str], 
                      memberCount:int, 
                      undergraduatesAllowed:bool, 
                      graduatesAllowed:bool):
        return  cls(
            code=code,
            name=name,
            description=description,
            tags=tags,
            memberCount=memberCount,
            undergraduatesAllowed=undergraduatesAllowed,
            graduatesAllowed=graduatesAllowed
        )

    
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
            "tags": self.tags,
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
        self.tags.add(newTag)
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
    
        
        
        
        
class User(db.Model):
    username: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str]
    favorites: Mapped [set[str]] = mapped_column(JSON)
    
    @classmethod
    def createNewUser(cls, 
                  username: str,
                  email: str,
                  favorites: set[str]
                  ):
        return cls(
        username = username,
        email = email,
        favorites = favorites)
    
    @classmethod
    def addUserToDb(cls, newUser):
        if isinstance(newUser, User):
            db.session.add(newUser)
            db.session.commit
            return newUser
    
    def to_json(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "favorites": self.favorites,
        }
        
    def updateEmail(self, newEmail: str):
        self.email = newEmail
        db.session.commit()

    def addFavorite(self, newFavorite: str):
        self.favorites.add(newFavorite)
        db.session.commit()

    def removeFavorite(self, removedFavorite: str) -> str:
        try:
            self.favorites.remove(removedFavorite)
            db.session.commit()
        except KeyError:  
            print(f"Error: {removedFavorite} not found in favorites.")
        return removedFavorite

    def updateUsername(self, newUsername: str):
        self.username = newUsername
        db.session.commit()
        
        
        
    
        
    
    
    
  
  
    

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
