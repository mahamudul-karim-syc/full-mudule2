from fastapi import FastAPI, APIRouter, Depends,Query,HTTPException
from sqlalchemy.orm import Session
import models
from datetime import datetime,timedelta
from pydantic import BaseModel,Field
from typing import Annotated,Optional
from models import Books,User,Reservation,IssueRecods
from database import engine,Sessionlocal
from fastapi.responses import JSONResponse
from router import admin,auth
from router.auth import get_current_user

router=APIRouter()

class BookCreate(BaseModel):
    title:str
    author:str
    category:str
    dectiption:str
    price : float=Field(default=0.0,ge=0)
    total_copies:int=Field(default=1,ge=1)

class UpdateBook(BaseModel):
    title:Optional[str]=Field(default=None)
    author:Optional[str]=Field(default=None)
    category:Optional[str]=Field(default=None)
    dectiption:Optional[str]=Field(default=None)
    price:Optional[float]=Field(default=None)
    total_copies:Optional[int]=Field(default=None)
    available_copies:Optional[int]=Field(default=None)
    
class IssueBook(BaseModel):
    book_id:int
    user_id:int


def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()
db_dapandancy=Annotated[Session,Depends(get_db)]
user_dapandancy=Annotated[dict,Depends(get_current_user)]
FINE_PER_DAY=20

def calulate_fine(due_date:datetime,return_date:datetime):
    over_due_days=(return_date.date()-due_date.date()).days
    if over_due_days >0:
        return round(over_due_days * FINE_PER_DAY,2) 
    else:
        return 0.0
    

@router.post("/admin/create_book")
def create_book(user:user_dapandancy,db:db_dapandancy,New_Book:BookCreate):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    book_model=Books(
        **New_Book.model_dump(),
        available_copies=New_Book.total_copies
    )
    db.add(book_model)
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"Book added successfully"})



@router.put("/admin/update_book/{book_id}")
def update_book(user:user_dapandancy,db:db_dapandancy,update_Book:UpdateBook,book_id:int):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    
    book = db.query(Books).filter(Books.id==book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail="Book not found")
    
    updatedata=update_Book.model_dump(exclude_unset=True)
    for key,value in updatedata.items():
        setattr(book,key,value)
    
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"Book update successfully"})
    
    

@router.delete("/admin/delete_book/{book_id}")
def delete_book(user:user_dapandancy,db:db_dapandancy,book_id:int):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    
    book = db.query(Books).filter(Books.id==book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail="Book not found")
    db.query(Books).filter(Books.id==book_id).delete()
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"Book deleted successfully"})
    
    

@router.post("/admin/create_issue")
def issue_book(user:user_dapandancy,db:db_dapandancy,issu_equest:IssueBook):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    book=db.query(Books).filter(Books.id==issu_equest.book_id).first()
    
    if book is None:
        raise HTTPException(status_code=404,detail="Book not found!")
    
    member=db.query(User).filter(User.id==issu_equest.user_id).first()
        
    if member is None:
        raise HTTPException(status_code=404,detail="member not found!")
    if book.available_copies is None or int(book.available_copies) <= 0:
    # if book.available_copies <=0:
        raise HTTPException(status_code=400,detail="Not copies available")
    
    loan_days=14
    issue_date=datetime.now()
    issue_model=IssueRecods(
        book_id=issu_equest.book_id,
        user_id=issu_equest.user_id,
        issue_date=issue_date,
        due_date=issue_date + timedelta(days=loan_days),
        status="issued"
    )
    # book.available_copies-=1
    book.available_copies = int(book.available_copies) - 1
    reservation=db.query(Reservation).filter(
        Reservation.book_id==issu_equest.book_id,
        Reservation.user_id==issu_equest.user_id,
        Reservation.status=="panding"
        
        ).first()
    if reservation is not None:
        reservation.status="aproved"
    db.add(issue_model)
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"Book issue successfully"})



@router.put("/admin/return_book/{issue_id}")
def return_book(user:user_dapandancy,db:db_dapandancy,issue_id:int):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    issue=db.query(IssueRecods).filter(IssueRecods.id==issue_id).first()
    
    if issue is None:
        raise HTTPException(status_code=404,detail="issue recode not found!")
    
    return_date=datetime.now()
    fine=calulate_fine(issue.due_date,return_date)
    issue.return_date=return_date
    issue.status='returned'
    issue.fine_amount=fine
    
    book=db.query(Books).filter(Books.id==issue.book_id).first()
    if book is not None:
        book.available_copies = int(book.available_copies) + 1
    
    # book.available_copies-=1
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"Book returned successfully","fine amount":fine})


@router.put("/admin/fine/paid/{issue_id}")
def fine_paid(user:user_dapandancy,db:db_dapandancy,issue_id:int):
    if user is None or user.get('role')!='librarian':
        raise HTTPException(status_code=401,detail="Faild authentication")
    issue=db.query(IssueRecods).filter(IssueRecods.id==issue_id).first()
    
    if issue is None:
        raise HTTPException(status_code=404,detail="issue recode not found!")
    
    issue.fine_paid=True
    db.commit()
    return JSONResponse(status_code=201,content={'massage':"fine paid successfully"})

