"""Validation and storage naming for optional Product images."""

import re
import warnings
from uuid import uuid4

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


PRODUCT_MEDIA_MAX_BYTES = 5 * 1024 * 1024
PRODUCT_MEDIA_ALLOWED_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})
PRODUCT_MEDIA_CONTENT_TYPES = {
    "JPEG": frozenset({"image/jpeg"}),
    "PNG": frozenset({"image/png"}),
    "WEBP": frozenset({"image/webp"}),
}
PRODUCT_MEDIA_EXTENSIONS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def inspect_product_media_file(uploaded_file) -> str:
    """Return the decoded image format or reject unsafe media content."""

    if not uploaded_file:
        raise ValidationError("Select a Product image.")

    try:
        file_size = uploaded_file.size
    except (AttributeError, OSError, ValueError) as exc:
        raise ValidationError("The Product image could not be read.") from exc

    if file_size > PRODUCT_MEDIA_MAX_BYTES:
        raise ValidationError("The Product image must be 5 MiB or smaller.")

    try:
        original_position = uploaded_file.tell()
    except (AttributeError, OSError, ValueError):
        original_position = None

    try:
        uploaded_file.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(uploaded_file) as image:
                image_format = image.format
                image.verify()
    except (
        AttributeError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
        ValueError,
    ) as exc:
        raise ValidationError("Upload a valid JPEG, PNG, or WebP image.") from exc
    finally:
        try:
            uploaded_file.seek(original_position or 0)
        except (AttributeError, OSError, ValueError):
            pass

    if image_format not in PRODUCT_MEDIA_ALLOWED_FORMATS:
        raise ValidationError("Upload a JPEG, PNG, or WebP image.")
    return image_format


def validate_product_media_file(uploaded_file):
    inspect_product_media_file(uploaded_file)


def validate_declared_product_media_type(uploaded_file, declared_content_type):
    """Reject a request MIME declaration that contradicts decoded content."""

    image_format = inspect_product_media_file(uploaded_file)
    normalized_content_type = (
        (declared_content_type or "").partition(";")[0].strip().lower()
    )
    if normalized_content_type not in PRODUCT_MEDIA_CONTENT_TYPES[image_format]:
        raise ValidationError("The uploaded file type does not match its image content.")


def product_media_upload_to(instance, _original_filename):
    """Generate a tenant/Product-scoped path without trusting the client filename."""

    if not instance.business_id or not instance.product_id:
        raise ValidationError("Product media requires an owned saved Product.")
    image_format = inspect_product_media_file(instance.image)
    extension = PRODUCT_MEDIA_EXTENSIONS[image_format]
    return (
        f"products/{instance.business_id}/{instance.product_id}/"
        f"{uuid4().hex}.{extension}"
    )


def product_media_storage_name_is_safe(name, *, business_id, product_id):
    expected = re.compile(
        rf"\Aproducts/{business_id}/{product_id}/[0-9a-f]{{32}}\.(?:jpg|png|webp)\Z"
    )
    return bool(name and expected.fullmatch(name))


def product_media_content_type(name):
    extension = (name or "").rsplit(".", 1)[-1].lower()
    return {
        "jpg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(extension)
