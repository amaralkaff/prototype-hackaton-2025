"""
Photo Upload API Routes
Handles photo upload, storage, and management
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
import os
from pathlib import Path
from supabase import create_client, Client

from utils.config import get_settings
from utils.logger import logger

settings = get_settings()
router = APIRouter(prefix="/photos", tags=["photos"])

# Supabase client for storage and database
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# Allowed file extensions and max size
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class PhotoUploadResponse(BaseModel):
    photo_id: UUID4
    borrower_id: UUID4
    photo_url: str
    photo_type: str
    file_size_kb: int
    uploaded_at: datetime
    message: str

class PhotoMetadata(BaseModel):
    photo_id: UUID4
    borrower_id: UUID4
    photo_type: str
    photo_url: str
    file_size_kb: int
    uploaded_at: datetime

def validate_image(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded image file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    # Check content type
    if not file.content_type.startswith("image/"):
        return False, "File must be an image"

    return True, "Valid"

@router.post("/upload", response_model=PhotoUploadResponse)
async def upload_photo(
    borrower_id: str,
    photo_type: str,
    file: UploadFile = File(...)
):
    """
    Upload a photo for a borrower

    Args:
        borrower_id: UUID of the borrower
        photo_type: Type of photo (business_exterior, business_interior, house_exterior, house_interior, field_documentation)
        file: Image file to upload

    Returns:
        PhotoUploadResponse with photo metadata
    """
    try:
        # Validate image
        is_valid, message = validate_image(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Check file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{borrower_id}/{photo_type}_{timestamp}{file_ext}"

        # Upload to Supabase Storage
        bucket_name = "borrower-photos"

        try:
            # Upload file
            response = supabase.storage.from_(bucket_name).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": file.content_type}
            )

            # Get public URL
            photo_url = supabase.storage.from_(bucket_name).get_public_url(filename)

        except Exception as storage_error:
            logger.error(f"Supabase storage error: {str(storage_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to storage: {str(storage_error)}"
            )

        # Save metadata to database via Supabase
        photo_data = {
            "borrower_id": borrower_id,
            "photo_type": photo_type,
            "photo_url": photo_url,
            "storage_path": filename,
            "file_size_kb": file_size // 1024,  # Convert bytes to KB
            "vision_analysis_status": "pending"
        }

        db_response = supabase.table('photos').insert(photo_data).execute()

        if not db_response.data or len(db_response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to save photo metadata")

        photo = db_response.data[0]
        logger.info(f"Photo uploaded successfully: {photo['id']}")

        return PhotoUploadResponse(
            photo_id=photo['id'],
            borrower_id=photo['borrower_id'],
            photo_url=photo['photo_url'],
            photo_type=photo['photo_type'],
            file_size_kb=photo['file_size_kb'],
            uploaded_at=photo['uploaded_at'],
            message="Photo uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/borrower/{borrower_id}", response_model=List[PhotoMetadata])
async def get_borrower_photos(borrower_id: str):
    """Get all photos for a borrower"""
    try:
        response = supabase.table('photos').select('*').eq('borrower_id', borrower_id).execute()

        if response.data:
            return [
                PhotoMetadata(
                    photo_id=photo['id'],
                    borrower_id=photo['borrower_id'],
                    photo_type=photo['photo_type'],
                    photo_url=photo['photo_url'],
                    file_size_kb=photo['file_size_kb'],
                    uploaded_at=photo['uploaded_at']
                )
                for photo in response.data
            ]
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{photo_id}")
async def delete_photo(photo_id: str):
    """Delete a photo"""
    try:
        # Get photo info
        response = supabase.table('photos').select('*').eq('id', photo_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Photo not found")

        photo = response.data[0]

        # Delete from Supabase Storage
        try:
            bucket_name = "borrower-photos"
            supabase.storage.from_(bucket_name).remove([photo['storage_path']])
        except Exception as storage_error:
            logger.warning(f"Failed to delete from storage: {str(storage_error)}")

        # Delete from database
        delete_response = supabase.table('photos').delete().eq('id', photo_id).execute()

        return {"message": "Photo deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting photo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
