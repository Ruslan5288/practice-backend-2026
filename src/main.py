from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, auth, database

app = FastAPI(title="Booking API")

models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def root():
    return {"status": "active"}


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="email busy")
    h_pass = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=h_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/resources", response_model=List[schemas.ResourceOut])
def get_resources(db: Session = Depends(database.get_db)):
    return db.query(models.Resource).all()


@app.post("/bookings", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, user_id: int, db: Session = Depends(database.get_db)):
    res = db.query(models.Resource).filter(models.Resource.id == booking.resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="resource not found")

    check = db.query(models.Booking).filter(models.Booking.resource_id == booking.resource_id).first()
    if check:
        raise HTTPException(status_code=400, detail="already booked")

    new_booking = models.Booking(user_id=user_id, resource_id=booking.resource_id)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking