from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.api.auth import get_current_active_user
from app.models.user import User
from app.utils.s3_uploader import s3_uploader

router = APIRouter()


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """Upload an image file to S3."""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 10MB)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Reset file position
    await file.seek(0)

    try:
        url = s3_uploader.upload_file(file, folder="poll-images")
        return {"url": url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a video file to S3."""
    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Validate file size (max 50MB)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    # Reset file position
    await file.seek(0)

    try:
        url = s3_uploader.upload_file(file, folder="poll-videos")
        return {"url": url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
