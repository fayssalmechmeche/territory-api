from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text, func, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from database import Base, engine
from dependencies import get_db, get_async_db
from auth import hash_password, verify_password, create_access_token,get_current_user_email
from cache import get_cached, set_cached
import models
import schemas


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base.metadata.create_all(bind=engine)


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
async def create_point(
    point: schemas.PointOfInterestCreate,
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
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
async def points_nearby(latitude: float, longitude: float, radius_meters: float = 1000, db: AsyncSession = Depends(get_async_db)):
    cache_key = f"nearby:{latitude}:{longitude}:{radius_meters}"
    cached_result = get_cached(cache_key)
    if cached_result is not None:
        return cached_result

    origin = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
    query = select(models.PointOfInterest).where(
        func.ST_DWithin(
            func.cast(models.PointOfInterest.geom, Geography),
            func.cast(origin, Geography),
            radius_meters
        )
    )
    result_db = await db.execute(query)
    points = result_db.scalars().all()

    result = [_point_to_out(p).model_dump() for p in points]
    set_cached(cache_key, result, expire_seconds=60)
    return result

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

@app.get("/points/{point_id}", response_model=schemas.PointOfInterestOut)
async def get_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(models.PointOfInterest).filter(models.PointOfInterest.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    return _point_to_out(point)

@app.put("/points/{point_id}", response_model=schemas.PointOfInterestOut)
async def update_point(point_id: int, point: schemas.PointOfInterestCreate, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    db_point = db.query(models.PointOfInterest).filter(models.PointOfInterest.id == point_id).first()
    if not db_point:
        raise HTTPException(status_code=404, detail="Point not found")

    db_point.name = point.name
    db_point.category = point.category
    db_point.geom = WKTElement(f"POINT({point.longitude} {point.latitude})", srid=4326)

    db.commit()
    db.refresh(db_point)
    return _point_to_out(db_point)

@app.delete("/points/{point_id}")
async def delete_point(point_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    point = db.query(models.PointOfInterest).filter(models.PointOfInterest.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    db.delete(point)
    db.commit()
    return {"deleted": True}


@app.post("/auth/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}