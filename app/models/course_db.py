from app.settings import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime as dt

class User(db.Model):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(unique=True, index=True)
    mobile:Mapped[str] = mapped_column(unique=True, index=True)
    password:Mapped[str] = mapped_column(nullable=False)
    is_admin:Mapped[bool] = mapped_column(default=False, nullable=False)
    courses: Mapped[list["Course"]] = relationship(back_populates="author")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="user")
    
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "mobile": self.mobile
        }

class Course(db.Model):
    __tablename__ = "courses"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_name:Mapped[str] = mapped_column(nullable=False)
    course_details:Mapped[str] = mapped_column(nullable=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    price:Mapped[int] = mapped_column(default=0, nullable=True)
    thumbnail:Mapped[str] = mapped_column(default=None, nullable=True)
    course_type:Mapped[str] = mapped_column(nullable=False)
    course_duration:Mapped[int] = mapped_column(nullable=False)
    author:Mapped["User"] = relationship(back_populates="courses")
    
    def to_dict(self):
        return {
            "id" : self.id,
            "course_name": self.course_name,
            "course_details": self.course_details,
            "price": self.price,
            "thumbnail": self.thumbnail,
            "course_type": self.course_type,
            "course_duration": self.course_duration
        }

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id:Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    
    is_purchased:Mapped[bool] = mapped_column(default=False)
    is_accessed:Mapped[bool] = mapped_column(default=False)
    
    user: Mapped["User"] = relationship(back_populates="enrollments")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "is_purchased": self.is_purchased,
            "is_accessed": self.is_accessed,
            "user": self.user
        }

class Video(db.Model):
    __tablename__ = "videos"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id:Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    url:Mapped[str] = mapped_column(nullable=False)
    title:Mapped[str] = mapped_column(nullable=True)
    desc:Mapped[str] = mapped_column(nullable=True)
    
    def  to_dict(self):
        return {
            "id": self.id,
            "course_id" : self.course_id,
            "url": self.url,
            "title": self.title,
            "desc": self.desc
        }

class Contact(db.Model):
    __tablename__ = "contacts"
    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[str] = mapped_column(nullable=False)
    message:Mapped[str] = mapped_column(nullable=False)
    contact_at:Mapped[dt.datetime] = mapped_column(default=dt.datetime.now())
    
    def to_dict(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "email" : self.email,
            "message" : self.message
        }