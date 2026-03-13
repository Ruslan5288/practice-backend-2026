from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, auth, database

app = FastAPI(title="Booking API")

models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def root():
    return {"mess": "vse rabotaet"}


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="email is busy")

    h_pass = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=h_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user