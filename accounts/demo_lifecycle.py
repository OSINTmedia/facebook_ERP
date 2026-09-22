"""Safe, deterministic lifecycle for the synthetic interactive demo."""

from dataclasses import dataclass
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from PIL import Image

from businesses.models import Business
from catalog.lifecycle import archive_product
from catalog.media_mutations import attach_or_replace_product_media
from catalog.models import (
    BusinessColor,
    BusinessColorAlias,
    BusinessProductType,
    BusinessProductTypeAlias,
    BusinessSize,
    BusinessSizeAlias,
    BusinessTag,
    BusinessTagAlias,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductMedia,
    ProductTag,
)
from catalog.product_media import product_media_storage_name_is_safe
from inventory.models import InventoryAdjustment
from inventory.mutations import initialize_choice_quantity


DEMO_BUSINESS_NAME = "Synthetic Demo Shop"


class DemoLifecycleError(Exception):
    """Raised when the demo lifecycle cannot identify or mutate a safe scope."""


@dataclass(frozen=True, slots=True)
class DemoLifecycleResult:
    action: str
    user_created: bool
    business_created: bool
    products: int
    choices: int


@dataclass(frozen=True, slots=True)
class _StoredMedia:
    storage: object
    name: str

    def delete(self):
        self.storage.delete(self.name)


def preview_demo_lifecycle(*, action):
    """Validate configuration and return the current scoped object counts."""
    email = _configured_demo_email()
    _validate_action(action)

    user_model = get_user_model()
    user = user_model.objects.filter(email=email).first()
    if user is None:
        if action == "reset":
            raise DemoLifecycleError("The configured demo user does not exist.")
        return DemoLifecycleResult(action, True, True, 0, 0)

    business = _find_demo_business(user=user, allow_missing=action != "reset")
    if business is None:
        return DemoLifecycleResult(action, False, True, 0, 0)

    return DemoLifecycleResult(
        action=action,
        user_created=False,
        business_created=False,
        products=Product.objects.filter(business=business).count(),
        choices=ProductChoice.objects.filter(business=business).count(),
    )


def apply_demo_lifecycle(*, action):
    """Apply one confirmed demo action inside one database transaction."""
    email = _configured_demo_email()
    _validate_action(action)
    old_media = ()
    new_media_writes = []

    try:
        with transaction.atomic():
            user, user_created = _ensure_demo_user(email=email, action=action)
            business, business_created = _ensure_demo_business(
                user=user,
                action=action,
            )
            old_media = _clear_demo_catalog(business=business)

            if action in {"seed", "reseed"}:
                _create_demo_baseline(
                    business=business,
                    actor=user,
                    new_media_writes=new_media_writes,
                )

            result = DemoLifecycleResult(
                action=action,
                user_created=user_created,
                business_created=business_created,
                products=Product.objects.filter(business=business).count(),
                choices=ProductChoice.objects.filter(business=business).count(),
            )
    except Exception:
        for media_write in new_media_writes:
            media_write.discard_new_file()
        raise

    _delete_stored_media(old_media)
    return result


def _configured_demo_email():
    if not settings.DEMO_ACCESS_ENABLED:
        raise DemoLifecycleError("Demo access is disabled.")
    if not settings.DEMO_USER_EMAIL.strip() or not settings.DEMO_USER_PASSWORD:
        raise DemoLifecycleError(
            "DEMO_USER_EMAIL and DEMO_USER_PASSWORD must be configured."
        )
    return get_user_model().objects.normalize_email(
        settings.DEMO_USER_EMAIL
    ).lower()


def _validate_action(action):
    if action not in {"seed", "reset", "reseed"}:
        raise DemoLifecycleError("Unknown demo lifecycle action.")


def _ensure_demo_user(*, email, action):
    user_model = get_user_model()
    try:
        user = user_model.objects.select_for_update().get(email=email)
        created = False
    except user_model.DoesNotExist:
        if action == "reset":
            raise DemoLifecycleError(
                "The configured demo user does not exist."
            ) from None
        user = user_model(email=email)
        created = True

    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.set_password(settings.DEMO_USER_PASSWORD)
    user.save()
    return user, created


def _find_demo_business(*, user, allow_missing):
    owned_businesses = list(
        Business.objects.filter(owner=user).order_by("pk")[:2]
    )
    if len(owned_businesses) > 1:
        raise DemoLifecycleError(
            "The configured demo user owns multiple Businesses; reset was refused."
        )
    if owned_businesses:
        return owned_businesses[0]
    if allow_missing:
        return None
    raise DemoLifecycleError("The protected demo Business does not exist.")


def _ensure_demo_business(*, user, action):
    business = _find_demo_business(user=user, allow_missing=action != "reset")
    if business is not None:
        business = Business.objects.select_for_update().get(pk=business.pk)
        if business.owner_id != user.pk:
            raise DemoLifecycleError(
                "The protected demo Business owner does not match."
            )
        if action in {"seed", "reseed"} and business.default_currency != "GEL":
            business.default_currency = "GEL"
            business.save(update_fields=["default_currency", "updated_at"])
        return business, False
    business = Business.objects.create(
        owner=user,
        name=DEMO_BUSINESS_NAME,
        default_currency="GEL",
    )
    return business, True


def _clear_demo_catalog(*, business):
    media_rows = list(
        ProductMedia.objects.filter(
            business=business,
            product__business=business,
        ).select_related("product")
    )
    stored_media = []
    for media in media_rows:
        name = media.image.name
        if not product_media_storage_name_is_safe(
            name,
            business_id=business.pk,
            product_id=media.product_id,
        ):
            raise DemoLifecycleError(
                "Demo media has an unsafe storage path; reset was refused."
            )
        stored_media.append(_StoredMedia(media.image.storage, name))

    adjustments = InventoryAdjustment.objects.filter(
        business=business,
        choice__business=business,
        choice__product__business=business,
    )
    adjustments._raw_delete(adjustments.db)
    ProductMaterialFact.objects.filter(
        business=business,
        product__business=business,
    ).delete()
    ProductMedia.objects.filter(
        business=business,
        product__business=business,
    ).delete()
    ProductTag.objects.filter(
        business=business,
        product__business=business,
        tag__business=business,
    ).delete()
    ProductChoice.objects.filter(
        business=business,
        product__business=business,
        size__business=business,
        color__business=business,
    ).delete()
    Product.objects.filter(business=business).delete()
    BusinessProductTypeAlias.objects.filter(business=business).delete()
    BusinessTagAlias.objects.filter(business=business).delete()
    BusinessSizeAlias.objects.filter(business=business).delete()
    BusinessColorAlias.objects.filter(business=business).delete()
    BusinessProductType.objects.filter(business=business).delete()
    BusinessTag.objects.filter(business=business).delete()
    BusinessSize.objects.filter(business=business).delete()
    BusinessColor.objects.filter(business=business).delete()
    return tuple(stored_media)


def _delete_stored_media(stored_media):
    cleanup_failures = 0
    for item in stored_media:
        try:
            item.delete()
        except Exception:
            cleanup_failures += 1
    if cleanup_failures:
        raise DemoLifecycleError(
            "Demo data was reset, but scoped media cleanup failed for "
            f"{cleanup_failures} file(s)."
        )


def _create_demo_baseline(*, business, actor, new_media_writes):
    dress = BusinessProductType.objects.create(business=business, name="კაბა")
    jacket = BusinessProductType.objects.create(business=business, name="ჟაკეტი")
    BusinessProductTypeAlias.objects.create(
        business=business,
        product_type=dress,
        alias="dress",
    )
    party = BusinessTag.objects.create(business=business, name="სადღესასწაულო")
    casual = BusinessTag.objects.create(business=business, name="ყოველდღიური")
    BusinessTagAlias.objects.create(
        business=business,
        tag=casual,
        alias="casual",
    )
    sizes = {
        name: BusinessSize.objects.create(business=business, name=name)
        for name in ("S", "M", "L", "Free size")
    }
    colors = {
        name: BusinessColor.objects.create(business=business, name=name)
        for name in ("შავი", "წითელი", "ლურჯი")
    }
    BusinessSizeAlias.objects.create(
        business=business,
        size=sizes["Free size"],
        alias="უნივერსალური",
    )
    BusinessColorAlias.objects.create(
        business=business,
        color=colors["შავი"],
        alias="black",
    )

    strong = _create_product(
        business=business,
        actor=actor,
        name="შავი ბამბის კაბა",
        description="შავი ბამბის კაბა საღამოსთვის",
        price="129.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=dress,
        tags=(party,),
        material=("ბამბა", 100, "100% ბამბა"),
        choices=((sizes["S"], colors["შავი"], 5),),
    )
    new_media_writes.append(
        attach_or_replace_product_media(
            business=business,
            product=strong,
            image=_synthetic_image(),
        )
    )
    _create_product(
        business=business,
        actor=actor,
        name="წითელი ჟაკეტი",
        description="წითელი ყოველდღიური ჟაკეტი",
        price="159.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=jacket,
        tags=(casual,),
        choices=((sizes["M"], colors["წითელი"], 1),),
    )
    _create_product(
        business=business,
        actor=actor,
        name="ლურჯი კაბა",
        description="ლურჯი კაბა ორი ზომით",
        price="119.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=dress,
        choices=(
            (sizes["S"], colors["ლურჯი"], 0),
            (sizes["M"], colors["ლურჯი"], 4),
        ),
    )
    _create_product(
        business=business,
        actor=actor,
        name="გაყიდული კაბა",
        description="შავი კაბა, მარაგი ამოიწურა",
        price="99.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=dress,
        choices=((sizes["L"], colors["შავი"], 0),),
    )
    _create_product(
        business=business,
        actor=actor,
        name="შესავსები მონახაზი",
        description="კაბა",
        price=None,
        lifecycle=Product.Lifecycle.DRAFT,
    )
    _create_product(
        business=business,
        actor=actor,
        name="ფასის გარეშე ჟაკეტი",
        description="ლურჯი ჟაკეტი, ფასი დასაზუსტებელია",
        price=None,
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=jacket,
        choices=((sizes["M"], colors["ლურჯი"], 2),),
    )
    _create_product(
        business=business,
        actor=actor,
        name="განმეორებადი არჩევანის კაბა",
        description="ორი ცალკე ერთნაირი არჩევანის კაბა",
        price="139.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=dress,
        choices=(
            (sizes["M"], colors["შავი"], 2),
            (sizes["M"], colors["შავი"], 1),
        ),
    )
    archived = _create_product(
        business=business,
        actor=actor,
        name="არქივირებული ჟაკეტი",
        description="ძველი ლურჯი ჟაკეტი",
        price="89.00",
        lifecycle=Product.Lifecycle.ACTIVE,
        product_type=jacket,
        choices=((sizes["S"], colors["ლურჯი"], 3),),
    )
    archive_product(business=business, product_id=archived.pk)


def _create_product(
    *,
    business,
    actor,
    name,
    description,
    price,
    lifecycle,
    product_type=None,
    tags=(),
    material=None,
    choices=(),
):
    product = Product.objects.create(
        business=business,
        product_type=product_type,
        name=name,
        description=description,
        price=price,
        lifecycle=lifecycle,
    )
    for tag in tags:
        ProductTag.objects.create(
            business=business,
            product=product,
            tag=tag,
        )
    if material:
        canonical_material, percentage, original_text = material
        ProductMaterialFact.objects.create(
            business=business,
            product=product,
            canonical_material=canonical_material,
            percentage=percentage,
            original_text=original_text,
            source=ProductMaterialFact.Source.DESCRIPTION,
            confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
        )
    for size, color, quantity in choices:
        choice = ProductChoice.objects.create(
            business=business,
            product=product,
            size=size,
            color=color,
            quantity=0,
        )
        if quantity:
            initialize_choice_quantity(
                business=business,
                choice=choice,
                actor=actor,
                quantity=quantity,
            )
    return product


def _synthetic_image():
    content = BytesIO()
    Image.new("RGB", (24, 18), color="#334155").save(content, format="PNG")
    return SimpleUploadedFile(
        "synthetic-demo.png",
        content.getvalue(),
        content_type="image/png",
    )
