from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
from . import models, schemas, auth, database

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    if db.query(models.Resource).count() == 0:
        db.add_all([
            models.Resource(name="Main Hall", description="Big room"),
            models.Resource(name="Small Room", description="For calls")
        ])
        db.commit()
    db.close()
    yield

app = FastAPI(title="Booking API", lifespan=lifespan)

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="busy")
    new_user = models.User(email=user.email, hashed_password=auth.get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/resources", response_model=List[schemas.ResourceOut])
def get_resources(db: Session = Depends(database.get_db)):
    return db.query(models.Resource).all()

@app.post("/bookings", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, user_id: int, db: Session = Depends(database.get_db)):
    check = db.query(models.Booking).filter(models.Booking.resource_id == booking.resource_id).first()
    if check:
        raise HTTPException(status_code=400, detail="booked")
    new_booking = models.Booking(user_id=user_id, resource_id=booking.resource_id)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, user_id: int, db: Session = Depends(database.get_db)):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == user_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(db_booking)
    db.commit()
    return {"ok": True}