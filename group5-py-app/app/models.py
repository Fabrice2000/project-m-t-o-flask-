from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class IndoorOutdoor(enum.Enum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    MIX = "mix"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    role = Column(String, default="user")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    outdoor_pref = Column(Float, default=0.5)  # 0 = indoors only, 1 = outdoors preferred
    children_friendly = Column(Boolean, default=False)
    user = relationship("User", backref="profile")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    indoor_outdoor = Column(Enum(IndoorOutdoor), default=IndoorOutdoor.MIX)
    min_age = Column(Integer, default=0)
    meta = Column(JSON, default={})

class ActivityInstance(Base):
    __tablename__ = "activity_instances"
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    start_dt = Column(DateTime)
    end_dt = Column(DateTime)
    location = Column(String)
    activity = relationship("Activity", backref="instances")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ranking = Column(JSON)  # e.g. [activity_id1, activity_id3, activity_id2]
