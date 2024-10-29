from sqlalchemy import Column, BigInteger, String, Time, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

# Initialize the base class for declarative models
Base = declarative_base()


# Users table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    gender = Column(String(50))
    favorite_genres = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationship with ListenHistory
    listen_history = relationship("ListenHistory", back_populates="user")

# Tracks table
class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    songwriters = Column(String(255))
    duration = Column(Time, nullable=False)
    genres = Column(String(255))
    album = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationship with ListenHistory
    listen_history = relationship("ListenHistory", back_populates="track")

# ListenHistory table
class ListenHistory(Base):
    __tablename__ = 'listen_history'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    track_id = Column(BigInteger, ForeignKey('tracks.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="listen_history")
    track = relationship("Track", back_populates="listen_history")

# Test table
class Test(Base):
    __tablename__ = 'test_table'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime)