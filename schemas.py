from pydantic import BaseModel

class PointOfInterestBase(BaseModel):

    name: str
    category: str
    latitude: float
    longitude: float

class PointOfInterestCreate(PointOfInterestBase):
    pass

class PointOfInterestOut(PointOfInterestBase):
    id: int

    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str