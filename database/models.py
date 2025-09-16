from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config.settings import DB_URL

engine = create_engine(DB_URL, echo=True)

Base = declarative_base()

class Article(Base):
    __tablename__ = "Articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, nullable=False, unique=True)
    timestamp = Column(DateTime)
    
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)