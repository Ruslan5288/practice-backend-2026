from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)

class ResourceOut(BaseModel):
    id: int
    name: str
    description: str
    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

class BookingOut(BaseModel):
    id: int
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    model_config = ConfigDict(from_attributes=True)