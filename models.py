from database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Float
from datetime import datetime
class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    emailname=Column(String,unique=True)
    username=Column(String,unique=True)
    fristname=Column(String)
    lestname=Column(String)
    hashpassword=Column(String)
    is_active=Column(Boolean,default=True)
    role=Column(String)#librarian or user
    
    
class Books(Base):
    __tablename__='books'
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String)
    author=Column(String)
    category=Column(String)
    dectiption=Column(String)
    price=Column(Float,default=0.0)
    total_copies=Column(Integer,default=3)
    available_copies=Column(Integer,nullable=True)
    cover_image=Column(String,nullable=True)
    created_at=Column(DateTime,default=datetime.now)

   
class Reservation(Base):
    __tablename__='reservation'
    
    id=Column(Integer,primary_key=True,index=True)
    book_id=Column(Integer,ForeignKey('books.id'))
    user_id=Column(Integer,ForeignKey('users.id'))
    reservation_date=Column(DateTime,default=datetime.now)
    status=Column(String,default='panding')


  
class IssueRecods(Base):
    __tablename__='issue_recods'
    
    id=Column(Integer,primary_key=True,index=True)
    book_id=Column(Integer,ForeignKey('books.id'))
    user_id=Column(Integer,ForeignKey('users.id'))
    issue_date=Column(DateTime,default=datetime.now)
    due_date=Column(DateTime)
    return_date=Column(DateTime,nullable=True)
    status=Column(String,default='issued')#issued returned
    fine_amount=Column(Float,default=0.0)
    fine_paid=Column(Boolean,default=False)
    
    