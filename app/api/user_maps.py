import io
import os
import uuid as uuid_mod

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from PIL import Image

from app.database import get_db
from app.models.user import User
from app.models.user_map import UserMap
from app.schemas.user_map import UserMapCreate, UserMapUpdate, UserMapResponse
from app.core.auth import get_current_user

UPLOAD_DIR = "uploads/maps"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"image/jpeg", "image/png"}

router = APIRouter()


@router.post("/upload-background")
async def upload_map_background(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a background image for a map. Returns URL and image dimensions."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG/PNG files are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    img = Image.open(io.BytesIO(content))
    img_width, img_height = img.size

    ext = "jpg" if file.content_type == "image/jpeg" else "png"
    filename = f"{uuid_mod.uuid4()}.{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/maps/{filename}", "width": img_width, "height": img_height}


@router.get("", response_model=list[UserMapResponse])
def list_user_maps(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return db.query(UserMap).filter(
        UserMap.user_id == current_user.id
    ).order_by(UserMap.created_at.desc()).all()


@router.post("", response_model=UserMapResponse, status_code=201)
def create_user_map(
    data: UserMapCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = UserMap(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(user_map)
    db.commit()
    db.refresh(user_map)
    return user_map


@router.get("/{map_id}", response_model=UserMapResponse)
def get_user_map(
    map_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")
    return user_map


@router.patch("/{map_id}", response_model=UserMapResponse)
def update_user_map(
    map_id: str,
    data: UserMapUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_map, field, value)

    db.commit()
    db.refresh(user_map)
    return user_map


@router.delete("/{map_id}", status_code=204)
def delete_user_map(
    map_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    user_map = db.query(UserMap).filter(
        UserMap.id == map_id,
        UserMap.user_id == current_user.id
    ).first()
    if not user_map:
        raise HTTPException(status_code=404, detail="Map not found")

    db.delete(user_map)
    db.commit()
