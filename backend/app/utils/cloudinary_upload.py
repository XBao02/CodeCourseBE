import os
from typing import Tuple
import cloudinary
import cloudinary.uploader

# Initialize Cloudinary using environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

DEFAULT_FOLDER = os.getenv("CLOUDINARY_FOLDER", "codecourse_videos")


def upload_video(file_stream, filename: str) -> Tuple[str, str]:
    """
    Upload a video to Cloudinary.
    Returns: (public_id, secure_url)
    """
    result = cloudinary.uploader.upload(
        file_stream,
        resource_type="video",
        folder=DEFAULT_FOLDER,
        public_id=os.path.splitext(filename)[0],
        overwrite=True,
    )
    return result.get("public_id"), result.get("secure_url")
