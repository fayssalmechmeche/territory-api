from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from database import Base

class PointOfInterest(Base):
    __tablename__ = "points_of_interest"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326), index=True)
    