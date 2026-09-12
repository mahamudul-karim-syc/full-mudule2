from fastapi import FastAPI, Depends,Query,HTTPException
from sqlalchemy.orm import Session
import models
from typing import Annotated,Optional
from models import Books,User,Reservation,IssueRecods
from database import engine,Sessionlocal
from fastapi.responses import JSONResponse
from router import admin,auth
from router.auth import get_current_user

app=FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()
db_dapandancy=Annotated[Session,Depends(get_db)]
user_dapandancy=Annotated[dict,Depends(get_current_user)]

@app.get("/books/all")
def get_all_book(user:user_dapandancy,db:db_dapandancy):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    books=db.query(Books).all()
    return books

@app.get("/book/{book_id}")
def get_specific_book(user:user_dapandancy,db:db_dapandancy,book_id:int):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    book=db.query(Books).filter(Books.id==book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail='Book Not found !')
    return book

@app.post("/reserved/{book_id}")
def get_reserved_book(user:user_dapandancy,db:db_dapandancy,book_id:int):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    book=db.query(Books).filter(Books.id==book_id).first()
    if book is None:
        raise HTTPException(status_code=404,detail='Book Not found !')
    reservation_model=Reservation(
        book_id=book_id,
        user_id=user.get("id"),
        status="panding"
        
    )
    db.add(reservation_model)
    db.commit()
    return JSONResponse(status_code=201,content={'message':'Reservation Booked successfully'})


@app.delete("/reservation/cancelled/{reservation_id}")
def cancelled_reservation(user:user_dapandancy,db:db_dapandancy,reservation_id:int):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    reservation=db.query(Reservation).filter(Reservation.id==reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404,detail='Reservation Not found !')
    
    reservation.status="cancelled"
    db.commit()
    return JSONResponse(status_code=201,content={'message':'cancelled Reservation successfully'})

@app.get("/reservation/my")
def cancelled_reservation(user:user_dapandancy,db:db_dapandancy):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    reservations=db.query(Reservation).filter(Reservation.user_id==user.get("id")).all()
    return reservations

@app.get("/issue/my")
def my_issue_books(user:user_dapandancy,db:db_dapandancy):
    if user is None:
        raise HTTPException(status_code=401,detail="Faild authentication")
    issue=db.query(IssueRecods).filter(
        IssueRecods.id==user.get("id"),
        IssueRecods.status=="issued").all()
    return issue
