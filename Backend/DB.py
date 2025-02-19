from datetime import date

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./health_tracker.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)


class PhysicalActivity(Base):
    __tablename__ = "physical_activity"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    steps = Column(Integer, nullable=False)
    cardio_time_session_minutes = Column(Integer, nullable=True)
    strength_time_session_minutes = Column(Integer, nullable=True)
    date = Column(Date,
                  default=date.today)  # The app support one activity data unit per day. all other data will be added to the same day


class SleepActivity(Base):
    __tablename__ = "sleep_activity"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sleep_hours = Column(Float, nullable=False)
    avg_heart_rate = Column(Float, nullable=False)
    avg_oxygen_level = Column(Float, nullable=False)
    date = Column(Date,
                  default=date.today,
                  nullable=False)  # the app support one sleep per day, the date is the time that the sleep started


class BloodTest(Base):
    __tablename__ = "blood_tests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    RBC = Column(Float, nullable=False)
    WBC = Column(Float, nullable=False)
    glucose_level = Column(Float, nullable=False)
    cholesterol_level = Column(Float, nullable=False)
    triglycerides_level = Column(Float, nullable=False)
    date = Column(Date, default=date.today)


Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def delete_all_data(session: Session, user_id: int) -> None:
    session.query(PhysicalActivity).filter(PhysicalActivity.user_id == user_id).delete()
    session.query(SleepActivity).filter(SleepActivity.user_id == user_id).delete()
    session.query(BloodTest).filter(BloodTest.user_id == user_id).delete()
    session.query(User).filter(User.id == user_id).delete()
