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

    class Config:
        from_attributes = True