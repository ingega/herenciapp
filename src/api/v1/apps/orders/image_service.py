# invercrypto/src/api/v1/apps/orders/image_service.py
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError


PRODUCT_PHOTO_DIR = Path("media/products")
PRODUCT_PHOTO_DIR.mkdir(parents=True, exist_ok=True)

MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_IMAGE_SIZE = (1200, 1200)


def save_product_photo(photo: UploadFile) -> str:
    """
    Validate, optimize, convert, and save a product photo locally.

    Returns the relative path stored in the Product.photo field.
    """

    # 1. Basic content-type validation
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if photo.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed formats: JPG, PNG, WebP.",
        )

    # 2. Read uploaded data
    photo_data = photo.file.read()

    if len(photo_data) > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Photo exceeds the maximum allowed size of 2 MB.",
        )

    # 3. Validate that the bytes are actually an image
    try:
        from io import BytesIO

        image = Image.open(BytesIO(photo_data))
        image.verify()

        # Reopen because verify() invalidates the image object
        image = Image.open(BytesIO(photo_data))

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid image.",
        )

    # 4. Normalize image mode for WebP
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")

    # 5. Resize while preserving aspect ratio
    image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)

    # 6. Generate server-controlled filename
    filename = f"{uuid4().hex}.webp"
    output_path = PRODUCT_PHOTO_DIR / filename

    # 7. Save optimized WebP
    image.save(
        output_path,
        format="WEBP",
        quality=85,
        optimize=True,
    )

    # 8. Return the storage key, not the OS-specific path
    return f"products/{filename}"