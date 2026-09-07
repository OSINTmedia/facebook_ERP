"""Atomic persistence support for one optional primary Product image."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction

from catalog.models import ProductMedia
from catalog.product_media import product_media_storage_name_is_safe


@dataclass(frozen=True)
class ProductMediaWrite:
    media: ProductMedia
    new_name: str
    replaced_name: str

    def discard_new_file(self):
        if product_media_storage_name_is_safe(
            self.new_name,
            business_id=self.media.business_id,
            product_id=self.media.product_id,
        ):
            self.media.image.storage.delete(self.new_name)

    def delete_replaced_file(self):
        if self.replaced_name and product_media_storage_name_is_safe(
            self.replaced_name,
            business_id=self.media.business_id,
            product_id=self.media.product_id,
        ):
            self.media.image.storage.delete(self.replaced_name)


def attach_or_replace_product_media(*, business, product, image):
    """Write one owned primary image inside the caller's database transaction."""

    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Product media must be saved inside a database transaction.")
    if not product.pk or product.business_id != business.pk:
        raise ValidationError("Product media must belong to the active Business.")

    media = ProductMedia.objects.select_for_update().filter(product=product).first()
    if media is not None and media.business_id != business.pk:
        raise ValidationError("Product media must belong to the active Business.")

    if media is None:
        media = ProductMedia(business=business, product=product)

    replaced_name = media.image.name if media.image else ""
    if replaced_name and not product_media_storage_name_is_safe(
        replaced_name,
        business_id=business.pk,
        product_id=product.pk,
    ):
        raise ValidationError("Existing Product media has an unsafe storage path.")

    media.image = image
    try:
        media.full_clean()
        media.save()
    except Exception:
        candidate_name = media.image.name if media.image else ""
        if candidate_name != replaced_name and product_media_storage_name_is_safe(
            candidate_name,
            business_id=business.pk,
            product_id=product.pk,
        ):
            media.image.storage.delete(candidate_name)
        raise

    write = ProductMediaWrite(
        media=media,
        new_name=media.image.name,
        replaced_name=replaced_name,
    )
    if replaced_name and replaced_name != write.new_name:
        transaction.on_commit(write.delete_replaced_file, robust=True)
    return write
