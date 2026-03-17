from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
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
            models.Resource(name="Neon Zone", description="Small room")
        ])
        db.commit()
    db.close()
    yield

app = FastAPI(title="Booking API", lifespan=lifespan)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

@app.get("/resources", response_model=List[schemas.ResourceOut])
def get_resources(db: Session = Depends(database.get_db)):
    return db.query(models.Resource).all()

@app.post("/bookings", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    overlap = db.query(models.Booking).filter(
        models.Booking.resource_id == booking.resource_id,
        models.Booking.start_time < booking.end_time,
        models.Booking.end_time > booking.start_time
    ).first()
    if overlap:
        raise HTTPException(status_code=400, detail="Time occupied")
    new_booking = models.Booking(**booking.model_dump(), user_id=current_user.id)
    db.add(new_booking); db.commit(); db.refresh(new_booking)
    return new_booking