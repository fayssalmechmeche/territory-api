from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from database import Base, engine
from dependencies import get_db
import models
import schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)


def _point_to_out(db_point: models.PointOfInterest) -> schemas.PointOfInterestOut:
    shape = to_shape(db_point.geom)
    return schemas.PointOfInterestOut(
        id=db_point.id,
        name=db_point.name,
        category=db_point.category,
        latitude=shape.y,
        longitude=shape.x,
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/db-check")
async def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {"db": "connected", "result": result.scalar()}


@app.post("/points", response_model=schemas.PointOfInterestOut)
async def create_point(point: schemas.PointOfInterestCreate, db: Session = Depends(get_db)):
    wkt_point = WKTElement(f"POINT({point.longitude} {point.latitude})", srid=4326)
    db_point = models.PointOfInterest(
        name=point.name,
        category=point.category,
        geom=wkt_point
    )
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return _point_to_out(db_point)


@app.get("/points", response_model=list[schemas.PointOfInterestOut])
async def list_points(db: Session = Depends(get_db)):
    points = db.query(models.PointOfInterest).all()
    return [_point_to_out(p) for p in points]

@app.get("/points/nearby", response_model=list[schemas.PointOfInterestOut])
async def points_nearby(latitude: float, longitude: float, radius_meters: float = 1000, db: Session = Depends(get_db)):
    origin = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
    points = db.query(models.PointOfInterest).filter(
        func.ST_DWithin(
            func.cast(models.PointOfInterest.geom, Geography),
            func.cast(origin, Geography),
            radius_meters
        )
    ).all()
    return [_point_to_out(p) for p in points]

@app.get("/points/{point_id}", response_model=schemas.PointOfInterestOut)
async def get_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(models.PointOfInterest).filter(models.PointOfInterest.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    return _point_to_out(point)


@app.delete("/points/{point_id}")
async def delete_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(models.PointOfInterest).filter(models.PointOfInterest.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    db.delete(point)
    db.commit()
    return {"deleted": True}

@app.get("/zones/buffer")
async def zone_buffer(latitude: float, longitude: float, radius_meters: float = 1000, db: Session = Depends(get_db)):
    origin = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
    result = db.query(
        func.ST_AsGeoJSON(
            func.ST_Transform(
                func.ST_Buffer(
                    func.ST_Transform(origin, 3857),
                    radius_meters
                ),
                4326
            )
        )
    ).scalar()
    return {"geojson": result}

