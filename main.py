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
  BANNED_USERS = set()

@app.post("/api/ban-user")
def ban_user(email: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action")
    BANNED_USERS.add(email)
    return {"message": f"User {email} has been banned successfully."}

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
@app.post("/api/admin-login")
def admin_login(email: str):
    if email == "mio257999@gmail.com":
        return {"success": True, "message": "Welcome back, Admin!"}
    raise HTTPException(status_code=403, detail="Access denied. Not an admin.")
# Persistent state variables
BANNED_USERS = set()
REPORTED_ITEMS = []
REPORT_COOLDOWNS = {}
REPORT_LOCKOUTS = {}

@app.post("/api/ban-user")
def ban_user(email: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action")
    BANNED_USERS.add(email)
    return {"message": f"User {email} has been banned successfully."}

@app.post("/api/reports")
def create_report(target_type: str, target_id: int, reason: str, reporter_email: str):
    if not reporter_email:
        raise HTTPException(status_code=401, detail="You must be logged in with an account to submit a report.")
    
    if reporter_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="Banned users cannot submit reports.")

    current_time = time.time()
    
    # Check if the user is locked out for sending an empty report
    if reporter_email in REPORT_LOCKOUTS:
        if current_time < REPORT_LOCKOUTS[reporter_email]:
            remaining = int((REPORT_LOCKOUTS[reporter_email] - current_time) / 60) + 1
            raise HTTPException(
                status_code=403, 
                detail=f"You are locked out for sending an empty report. Try again in {remaining} minutes."
            )
        else:
            del REPORT_LOCKOUTS[reporter_email]

    # The 10-minute penalty for empty, blank, or dot-only reports (600 seconds)
    if not reason or not reason.strip() or reason.strip() == ".":
        REPORT_LOCKOUTS[reporter_email] = current_time + 600
        raise HTTPException(
            status_code=403, 
            detail="Empty reports are not allowed! You have been locked out of the site for 10 minutes."
        )

    # Anti-spam cooldown (60 seconds)
    if reporter_email in REPORT_COOLDOWNS:
        if current_time - REPORT_COOLDOWNS[reporter_email] < 60:
            raise HTTPException(status_code=429, detail="Please wait a minute before submitting another report.")
            
    REPORT_COOLDOWNS[reporter_email] = current_time
    
    report = {
        "id": len(REPORTED_ITEMS) + 1,
        "target_type": target_type,
        "target_id": target_id,
        "reason": reason,
        "reporter_email": reporter_email
    }
    REPORTED_ITEMS.append(report)
    return {"message": "Report submitted successfully."}

@app.get("/api/admin/reports")
def get_reports(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action")
    return REPORTED_ITEMS
# Editor Applications, Permissions & Title Request State
APPROVED_EDITORS = set(["mio257999@gmail.com"])
EDITOR_APPLICATIONS = []
MANGA_REQUESTS = []

@app.post("/api/editor/apply")
def apply_to_be_editor(email: str, sample_work_link: str, note: str):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    
    # Check if they already have a pending application
    for app_item in EDITOR_APPLICATIONS:
        if app_item["email"] == email and app_item["status"] == "pending":
            raise HTTPException(status_code=400, detail="You already have a pending application.")
            
    application = {
        "id": len(EDITOR_APPLICATIONS) + 1,
        "email": email,
        "sample_work_link": sample_work_link,
        "note": note,
        "status": "pending"
    }
    EDITOR_APPLICATIONS.append(application)
    return {"message": "Application submitted successfully! You can track its status on your profile."}

@app.get("/api/editor/my-status")
def check_my_application_status(email: str):
    user_apps = [app for app in EDITOR_APPLICATIONS if app["email"] == email]
    if not user_apps:
        return {"status": "none"}
    return user_apps[-1]

@app.get("/api/admin/editor-applications")
def get_editor_applications(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action. Only the admin can view applications.")
    return EDITOR_APPLICATIONS

@app.post("/api/admin/review-editor")
def review_editor_application(app_id: int, status: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    
    for app_item in EDITOR_APPLICATIONS:
        if app_item["id"] == app_id:
            app_item["status"] = status
            if status == "approved":
                APPROVED_EDITORS.add(app_item["email"])
            return {"message": f"Application {status} successfully."}
            
    raise HTTPException(status_code=404, detail="Application not found.")

@app.post("/api/manga/request-title")
def request_new_title(title: str, author: str, original_language: str, submitter_email: str):
    if not submitter_email or submitter_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You cannot submit title requests.")
        
    request_entry = {
        "id": len(MANGA_REQUESTS) + 1,
        "title": title,
        "author": author,
        "original_language": original_language,
        "submitter_email": submitter_email,
        "status": "pending"
    }
    MANGA_REQUESTS.append(request_entry)
    return {"message": "Title request submitted to admin for review!"}

@app.get("/api/admin/manga-requests")
def get_manga_requests(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action")
    return MANGA_REQUESTS
# Track bad edits to automatically strip edit privileges: { email: bad_edit_count }
EDIT_ABUSE_TRACKER = {}
# Users who are allowed to edit metadata (starts empty, populated when you approve them)
EDIT_PRIVILEGES = set(["mio257999@gmail.com"])

@app.post("/api/manga/edit")
def edit_manga_metadata(manga_id: int, editor_email: str, is_bad_edit: bool = False):
    if editor_email not in EDIT_PRIVILEGES or editor_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You do not have permission to edit manga metadata.")
    
    # If the edit is flagged as bad (wrong tags/themes/covers)
    if is_bad_edit:
        EDIT_ABUSE_TRACKER[editor_email] = EDIT_ABUSE_TRACKER.get(editor_email, 0) + 1
        
        # If they hit 4 bad edits, automatically strip their edit rights and roll back!
        if EDIT_ABUSE_TRACKER[editor_email] >= 4:
            if editor_email in EDIT_PRIVILEGES:
                EDIT_PRIVILEGES.remove(editor_email)
            return {
                "message": "Warning: Too many incorrect edits! Your edit privileges have been automatically revoked, and the title has been rolled back."
            }
            
    return {"message": "Manga metadata updated successfully."}
# ==========================================
# MANGADEX-STYLE 4 SUBMISSION & HISTORY FEATURES
# ==========================================

APPROVED_EDITORS = set(["mio257999@gmail.com"])
EDITOR_APPLICATIONS = []

APPROVED_GROUPS = set()
GROUP_REQUESTS = []

MANGA_REQUESTS = []

REPORTS = []

# --- 1. EDITOR APPLICATIONS ---
@app.post("/api/editor/apply")
def apply_to_be_editor(email: str, sample_work_link: str, note: str):
    if not email or email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in.")
    for app_item in EDITOR_APPLICATIONS:
        if app_item["email"] == email and app_item["status"] == "pending":
            raise HTTPException(status_code=400, detail="You already have a pending application.")
    application = {
        "id": len(EDITOR_APPLICATIONS) + 1,
        "email": email,
        "sample_work_link": sample_work_link,
        "note": note,
        "status": "pending",
        "admin_note": ""
    }
    EDITOR_APPLICATIONS.append(application)
    return {"message": "Editor application submitted successfully!"}

@app.get("/api/user/editor-applications")
def get_my_editor_applications(email: str):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    return [app for app in EDITOR_APPLICATIONS if app["email"] == email]

@app.get("/api/admin/editor-applications")
def get_admin_editor_applications(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    return EDITOR_APPLICATIONS

@app.post("/api/admin/review-editor")
def review_editor_application(app_id: int, status: str, admin_note: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    for app_item in EDITOR_APPLICATIONS:
        if app_item["id"] == app_id:
            app_item["status"] = status
            app_item["admin_note"] = admin_note
            if status == "approved":
                APPROVED_EDITORS.add(app_item["email"])
                EDIT_PRIVILEGES.add(app_item["email"])
            return {"message": f"Application {status} successfully."}
    raise HTTPException(status_code=404, detail="Application not found.")


# --- 2. SCANLATION GROUPS ("My Groups" & public "Groups") ---
@app.post("/api/groups/request")
def request_scanlation_group(group_name: str, description: str, submitter_email: str):
    if not submitter_email or submitter_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in.")
    for req in GROUP_REQUESTS:
        if req["submitter_email"] == submitter_email and req["status"] == "pending":
            raise HTTPException(status_code=400, detail="You already have a pending group request.")
    group_request = {
        "id": len(GROUP_REQUESTS) + 1,
        "group_name": group_name,
        "description": description,
        "submitter_email": submitter_email,
        "status": "pending",
        "admin_note": ""
    }
    GROUP_REQUESTS.append(group_request)
    return {"message": "Group request submitted successfully!"}

@app.get("/api/user/my-groups")
def get_my_groups(email: str):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    return [req for req in GROUP_REQUESTS if req["submitter_email"] == email]

@app.get("/api/groups/public-list")
def get_public_groups():
    return [req for req in GROUP_REQUESTS if req["status"] == "approved"]

@app.get("/api/admin/group-requests")
def get_admin_group_requests(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    return GROUP_REQUESTS

@app.post("/api/admin/review-group")
def review_group_request(request_id: int, status: str, admin_note: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    for req in GROUP_REQUESTS:
        if req["id"] == request_id:
            req["status"] = status
            req["admin_note"] = admin_note
            if status == "approved":
                APPROVED_GROUPS.add(req["group_name"])
            return {"message": f"Group request {status} successfully."}
    raise HTTPException(status_code=404, detail="Group request not found.")


# --- 3. ENHANCED MANGA TITLE DRAFT & SUBMISSION HISTORY ---
@app.post("/api/manga/request-title-draft")
def request_title_draft(
    title: str,
    alternative_titles: str = "",
    synopsis: str = "",
    authors: str = "",
    original_language: str = "",
    content_rating: str = "",
    publication_status: str = "",
    genres: str = "",
    themes: str = "",
    submitter_email: str = ""
):
    if not submitter_email or submitter_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in to submit a title draft.")
    
    draft_entry = {
        "id": len(MANGA_REQUESTS) + 1,
        "title": title,
        "alternative_titles": alternative_titles,
        "synopsis": synopsis,
        "authors": authors,
        "original_language": original_language,
        "content_rating": content_rating,
        "publication_status": publication_status,
        "genres": genres,
        "themes": themes,
        "submitter_email": submitter_email,
        "status": "pending",
        "admin_note": ""
    }
    MANGA_REQUESTS.append(draft_entry)
    return {"message": "Title draft submitted successfully! You can track its status in your submission history."}

@app.get("/api/user/title-submissions")
def get_my_title_submissions(email: str):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    return [t for t in MANGA_REQUESTS if t["submitter_email"] == email]

@app.get("/api/admin/manga-requests")
def get_admin_manga_requests(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    return MANGA_REQUESTS

@app.post("/api/admin/review-manga-request")
def review_manga_request(request_id: int, status: str, admin_note: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    for t in MANGA_REQUESTS:
        if t["id"] == request_id:
            t["status"] = status
            t["admin_note"] = admin_note
            return {"message": f"Title request {status} successfully."}
    raise HTTPException(status_code=404, detail="Title request not found.")


# --- 4. REPORTS ("My Reports" Tracker) ---
@app.post("/api/reports/submit")
def submit_report(reporter_email: str, target_type: str, target_id: int, reason: str):
    if not reporter_email or reporter_email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in.")
    report = {
        "id": len(REPORTS) + 1,
        "reporter_email": reporter_email,
        "target_type": target_type,
        "target_id": target_id,
        "reason": reason,
        "status": "pending",
        "admin_note": ""
    }
    REPORTS.append(report)
    return {"message": "Report submitted successfully."}

@app.get("/api/user/my-reports")
def get_my_reports(email: str):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    return [r for r in REPORTS if r["reporter_email"] == email]

@app.get("/api/admin/reports")
def get_admin_reports(admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    return REPORTS

@app.post("/api/admin/review-report")
def review_report(report_id: int, status: str, admin_note: str, admin_email: str):
    if admin_email != "mio257999@gmail.com":
        raise HTTPException(status_code=403, detail="Unauthorized action.")
    for r in REPORTS:
        if r["id"] == report_id:
            r["status"] = status
            r["admin_note"] = admin_note
            return {"message": f"Report {status} successfully."}
    raise HTTPException(status_code=404, detail="Report not found.")
# ==========================================
# CHAPTER TRACKER & PROGRESS (Checkmarks, Continue Button, Mark All Read)
# ==========================================

# Stores read chapters as: { "email_mangaid": [1.0, 2.0, 3.0] }
CHAPTER_PROGRESS = {}

@app.get("/api/user/chapter-progress")
def get_chapter_progress(email: str, manga_id: int):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    key = f"{email}_{manga_id}"
    return {"read_chapters": CHAPTER_PROGRESS.get(key, [])}

@app.post("/api/user/toggle-chapter")
def toggle_chapter_read(email: str, manga_id: int, chapter_number: float, mark_read: bool):
    if not email or email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in.")
    key = f"{email}_{manga_id}"
    if key not in CHAPTER_PROGRESS:
        CHAPTER_PROGRESS[key] = []
        
    if mark_read and chapter_number not in CHAPTER_PROGRESS[key]:
        CHAPTER_PROGRESS[key].append(chapter_number)
    elif not mark_read and chapter_number in CHAPTER_PROGRESS[key]:
        CHAPTER_PROGRESS[key].remove(chapter_number)
        
    return {"message": "Chapter progress updated."}

@app.post("/api/user/mark-all-read")
def mark_all_read(email: str, manga_id: int, chapters: str):
    # Pass comma-separated chapter numbers e.g. "1,2,3,4"
    if not email or email in BANNED_USERS:
        raise HTTPException(status_code=403, detail="You must be logged in.")
    key = f"{email}_{manga_id}"
    chapter_list = [float(c.strip()) for c in chapters.split(",") if c.strip()]
    CHAPTER_PROGRESS[key] = chapter_list
    return {"message": "All chapters marked as read."}

@app.post("/api/user/clear-progress")
def clear_progress(email: str, manga_id: int):
    if not email:
        raise HTTPException(status_code=401, detail="You must be logged in.")
    key = f"{email}_{manga_id}"
    CHAPTER_PROGRESS[key] = []
    return {"message": "Reading progress cleared."}






  
