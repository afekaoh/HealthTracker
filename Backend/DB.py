import os
from datetime import date
from typing import Callable, Union

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, Session

"""
The databases are very much look alike for simplicity of development.
There is no real reason for that so that's why I didn't build a more complex schema with a inheritance.
"""

# Global placeholders (will be initialized inside init_db)
engine = None
SessionLocal: Union[Callable, None] = None

Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Primary key
    # In order to not expose the id to the users we will use the user_name as the main identifier for the user
    user_name = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)


class PhysicalActivity(Base):
    __tablename__ = "physical_activity"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    steps = Column(Integer, nullable=False)
    cardio_time_session_minutes = Column(Integer, nullable=True)
    strength_time_session_minutes = Column(Integer, nullable=True)
    date = Column(Date, default=date.today, )
    __table_args__ = (
        # The app support one activity data unit per day. all other data will be added to the same day
        UniqueConstraint('id', 'date'),
    )


class SleepActivity(Base):
    __tablename__ = "sleep_activity"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sleep_hours = Column(Float, nullable=False)
    avg_heart_rate = Column(Float, nullable=False)
    avg_oxygen_level = Column(Float, nullable=False)
    date = Column(Date,
                  default=date.today,
                  nullable=False)
    __table_args__ = (
        # the app support one sleep per day, the date is the time that the sleep started
        UniqueConstraint('id', 'date'),
    )


class BloodTest(Base):
    __tablename__ = "blood_tests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    RBC = Column(Float, nullable=False)
    WBC = Column(Float, nullable=False)
    glucose_level = Column(Float, nullable=False)
    cholesterol_level = Column(Float, nullable=False)
    triglycerides_level = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
    __table_args__ = (
        # the app support one blood test per day, the date is the time that the test was taken
        UniqueConstraint('id', 'date'),
    )


def init_db():
    global engine, SessionLocal
    engine = create_engine(os.environ['DATABASE_URL'])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
