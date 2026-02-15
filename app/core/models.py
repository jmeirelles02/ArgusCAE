from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    chat_id = Column(BigInteger, primary_key=True, index=True)
    profile = Column(String, default="Indefinido")
    language = Column(String, default="pt")
    
    assets = relationship("Asset", back_populates="owner", lazy="selectin")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    user_chat_id = Column(BigInteger, ForeignKey("users.chat_id"))

    owner = relationship("User", back_populates="assets")