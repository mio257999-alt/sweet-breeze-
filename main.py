import enum  
from typing import List, Optional  
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, Query, HTTPException  
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text, Enum  
from sqlalchemy.orm import declarative_base, sessionmaker, Session  
  
DATABASE_URL = "sqlite:///./sweet_breeze.db"  
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
Base = declarative_base()  
  
class ContentRating(str, enum.Enum):  
    SAFE = "Safe"  
    SUGGESTIVE = "Suggestive"  
    EROTICA = "Erotica"  
  
class User(Base):  
    __tablename__ = "users"  
    id = Column(Integer, primary_key=True, index=True)  
    username = Column(String, unique=True, index=True, nullable=False)  
    avatar_url = Column(String, default="https://via.placeholder.com/150")  
    hide_wall = Column(Boolean, default=False)  
    hide_comments = Column(Boolean, default=False)  
    hide_reads = Column(Boolean, default=False)  
    hide_stats = Column(Boolean, default=False)  
    show_following_rails = Column(Boolean, default=True)  
    show_history_rails = Column(Boolean, default=True)  
  
class Manga(Base):  
    __tablename__ = "manga"  
    id = Column(Integer, primary_key=True, index=True)  
    title = Column(String, index=True)  
    author = Column(String, index=True)  
    cover_image = Column(String)  
    rating = Column(Enum(ContentRating), default=ContentRating.SAFE)  
    genres = Column(String)  
    themes = Column(String)  
    warnings = Column(String)  
  
class Comment(Base):  
    __tablename__ = "comments"  
    id = Column(Integer, primary_key=True, index=True)  
    manga_id = Column(Integer, ForeignKey("manga.id"))  
    chapter_num = Column(Integer)  
    user_id = Column(Integer, ForeignKey("users.id"))  
    text = Column(Text)  
    likes = Column(Integer, default=0)  
    dislikes = Column(Integer, default=0)  
  
Base.metadata.create_all(bind=engine)  
  
app = FastAPI(title="Sweet Breeze API")  
  
def get_db():  
    db = SessionLocal()  
    try:  
        yield db  
    finally:  
        db.close()  
  
@app.get("/api/manga/search")  
def search_manga(  
    q: Optional[str] = None,  
    ratings: Optional[List[str]] = Query(None),  
    genres: Optional[List[str]] = Query(None),  
    themes: Optional[List[str]] = Query(None),  
    db: Session = Depends(get_db)  
):  
    query = db.query(Manga)  
    if q:  
        query = query.filter((Manga.title.ilike(f"%{q}%")) | (Manga.author.ilike(f"%{q}%")))  
    if ratings:  
        query = query.filter(Manga.rating.in_(ratings))  
    if genres:  
        for genre in genres:  
            query = query.filter(Manga.genres.contains(genre))  
    if themes:  
        for theme in themes:  
            query = query.filter(Manga.themes.contains(theme))  
    return query.all()  
  
@app.post("/api/comments/report")  
def report_comment(comment_id: int, reason: str, agree_rules: bool):  
    if not agree_rules:  
        raise HTTPException(status_code=400, detail="Must agree to community rules before reporting.")  
    return {"status": "success", "message": "Report logged for moderation review."}  
  from pydantic import BaseModel

class MangaCreate(BaseModel):
    title: str
    author: Optional[str] = None
    cover_image: Optional[str] = None
    rating: Optional[ContentRating] = ContentRating.SAFE
    genres: Optional[str] = None
    themes: Optional[str] = None
    warnings: Optional[str] = None

@app.post("/api/manga")
def create_manga(manga: MangaCreate, db: Session = Depends(get_db)):
    db_manga = Manga(
        title=manga.title,
        author=manga.author,
        cover_image=manga.cover_image,
        rating=manga.rating,
        genres=manga.genres,
        themes=manga.themes,
        warnings=manga.warnings
    )
    db.add(db_manga)
    db.commit()
    db.refresh(db_manga)
    return db_manga
  @app.get("/api/manga")
def get_all_manga(db: Session = Depends(get_db)):
    return db.query(Manga).all()




  
