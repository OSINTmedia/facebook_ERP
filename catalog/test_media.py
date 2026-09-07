from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.utils.datastructures import MultiValueDict
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from businesses.models import Business
from catalog.forms import ProductMediaForm
from catalog.media_mutations import attach_or_replace_product_media
from catalog.models import Product, ProductMedia
from catalog.product_bundles import ProductBundle
from catalog.product_media import PRODUCT_MEDIA_MAX_BYTES


def product_image_upload(
    name="seller supplied.png",
    *,
    image_format="PNG",
    content_type="image/png",
    color="navy",
):
    content = BytesIO()
    Image.new("RGB", (12, 9), color=color).save(content, format=image_format)
    return SimpleUploadedFile(name, content.getvalue(), content_type=content_type)


def draft_bundle_data(**overrides):
    data = {
        "name": "Media product",
        "description": "Product with optional media.",
        "price": "",
        "product_type": "",
        "tags": [],
        "lifecycle": Product.Lifecycle.DRAFT,
        "choices-TOTAL_FORMS": "0",
        "choices-INITIAL_FORMS": "0",
        "choices-MIN_NUM_FORMS": "0",
        "choices-MAX_NUM_FORMS": "1000",
        "materials-TOTAL_FORMS": "0",
        "materials-INITIAL_FORMS": "0",
        "materials-MIN_NUM_FORMS": "0",
        "materials-MAX_NUM_FORMS": "1000",
    }
    data.update(overrides)
    return data


class TemporaryMediaMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media_directory = TemporaryDirectory()
        cls._media_override = override_settings(
            MEDIA_ROOT=cls._media_directory.name
        )
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        cls._media_directory.cleanup()
        super().tearDownClass()

    def stored_files(self):
        return tuple(
            path
            for path in Path(self._media_directory.name).rglob("*")
            if path.is_file()
        )

    def tearDown(self):
        for path in sorted(
            Path(self._media_directory.name).rglob("*"),
            reverse=True,
        ):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        super().tearDown()


class ProductMediaFormAndModelTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="media-model-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="media-model-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Media Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Media Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Media product",
            description="Product media model coverage.",
        )

    def test_form_accepts_only_the_approved_decoded_formats(self):
        cases = (
            ("photo.jpeg", "JPEG", "image/jpeg"),
            ("photo.png", "PNG", "image/png"),
            ("photo.webp", "WEBP", "image/webp"),
        )

        for name, image_format, content_type in cases:
            with self.subTest(image_format=image_format):
                form = ProductMediaForm(
                    data={},
                    files={
                        "image": product_image_upload(
                            name,
                            image_format=image_format,
                            content_type=content_type,
                        )
                    },
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_malformed_oversized_and_mismatched_uploads(self):
        valid_png = product_image_upload()
        oversized = SimpleUploadedFile(
            "large.png",
            valid_png.read() + b"0" * PRODUCT_MEDIA_MAX_BYTES,
            content_type="image/png",
        )
        invalid_uploads = (
            SimpleUploadedFile(
                "broken.png",
                b"not an image",
                content_type="image/png",
            ),
            oversized,
            product_image_upload(content_type="image/jpeg"),
        )

        for uploaded_file in invalid_uploads:
            with self.subTest(uploaded_file=uploaded_file.name):
                form = ProductMediaForm(
                    data={},
                    files={"image": uploaded_file},
                )
                self.assertFalse(form.is_valid())
                self.assertIn("image", form.errors)

    def test_form_rejects_repeated_image_fields(self):
        form = ProductMediaForm(
            data={},
            files=MultiValueDict(
                {
                    "image": [
                        product_image_upload("first.png"),
                        product_image_upload("second.png"),
                    ]
                }
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Select only one Product image.", form.errors["image"])

    def test_model_rejects_cross_business_media_before_file_write(self):
        media = ProductMedia(
            business=self.other_business,
            product=self.product,
            image=product_image_upload(),
        )

        with self.assertRaises(ValidationError):
            media.save()

        self.assertEqual(self.stored_files(), ())

    def test_media_path_is_generated_and_one_primary_row_is_enforced(self):
        with transaction.atomic():
            write = attach_or_replace_product_media(
                business=self.business,
                product=self.product,
                image=product_image_upload("../../seller name.PNG"),
            )

        media = ProductMedia.objects.get()
        self.assertEqual(media, write.media)
        self.assertRegex(
            media.image.name,
            rf"^products/{self.business.pk}/{self.product.pk}/[0-9a-f]{{32}}\.png$",
        )
        self.assertNotIn("seller", media.image.name)
        stored_name = media.image.name
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductMedia.objects.create(
                    business=self.business,
                    product=self.product,
                    image=product_image_upload("second.png"),
                )
        self.assertEqual(
            tuple(
                path.relative_to(self._media_directory.name).as_posix()
                for path in self.stored_files()
            ),
            (stored_name,),
        )

    def test_replace_keeps_one_row_and_deletes_old_file_after_commit(self):
        with transaction.atomic():
            first_write = attach_or_replace_product_media(
                business=self.business,
                product=self.product,
                image=product_image_upload(color="red"),
            )
        old_path = Path(self._media_directory.name, first_write.new_name)
        self.assertTrue(old_path.exists())

        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                second_write = attach_or_replace_product_media(
                    business=self.business,
                    product=self.product,
                    image=product_image_upload(
                        "replacement.webp",
                        image_format="WEBP",
                        content_type="image/webp",
                        color="green",
                    ),
                )

        self.assertEqual(ProductMedia.objects.count(), 1)
        self.assertNotEqual(first_write.new_name, second_write.new_name)
        self.assertFalse(old_path.exists())
        self.assertTrue(
            Path(self._media_directory.name, second_write.new_name).exists()
        )

    def test_replacement_cleanup_callback_cannot_break_committed_media_truth(self):
        with transaction.atomic():
            attach_or_replace_product_media(
                business=self.business,
                product=self.product,
                image=product_image_upload(),
            )

        with patch("catalog.media_mutations.transaction.on_commit") as on_commit:
            with transaction.atomic():
                write = attach_or_replace_product_media(
                    business=self.business,
                    product=self.product,
                    image=product_image_upload(color="green"),
                )

        on_commit.assert_called_once_with(write.delete_replaced_file, robust=True)

    def test_media_mutation_rejects_cross_business_product(self):
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                attach_or_replace_product_media(
                    business=self.other_business,
                    product=self.product,
                    image=product_image_upload(),
                )

        self.assertFalse(ProductMedia.objects.exists())
        self.assertEqual(self.stored_files(), ())


class ProductMediaBundleTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            email="media-bundle-owner@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Bundle Media Studio",
        )

    def create_product(self):
        return Product.objects.create(
            business=self.business,
            name="Existing media product",
            description="Existing Product media coverage.",
        )

    def attach_initial_media(self, product):
        with transaction.atomic():
            return attach_or_replace_product_media(
                business=self.business,
                product=product,
                image=product_image_upload(color="red"),
            ).media

    def test_bundle_creates_product_and_owned_media_atomically(self):
        bundle = ProductBundle(
            business=self.business,
            data=draft_bundle_data(),
            files={"image": product_image_upload()},
        )

        self.assertTrue(bundle.is_valid(), bundle.media_form.errors)
        product = bundle.save(actor=self.owner)

        media = ProductMedia.objects.get()
        self.assertEqual(media.business, self.business)
        self.assertEqual(media.product, product)
        self.assertEqual(len(self.stored_files()), 1)

    def test_invalid_bundle_writes_neither_product_media_nor_file(self):
        bundle = ProductBundle(
            business=self.business,
            data=draft_bundle_data(name=""),
            files={"image": product_image_upload()},
        )

        self.assertFalse(bundle.is_valid())

        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductMedia.objects.exists())
        self.assertEqual(self.stored_files(), ())

    def test_media_save_failure_rolls_back_product_and_removes_new_file(self):
        bundle = ProductBundle(
            business=self.business,
            data=draft_bundle_data(),
            files={"image": product_image_upload()},
        )
        self.assertTrue(bundle.is_valid(), bundle.media_form.errors)
        original_save = ProductMedia.save

        def save_then_fail(media, *args, **kwargs):
            original_save(media, *args, **kwargs)
            raise RuntimeError("simulated media database failure")

        with patch.object(ProductMedia, "save", new=save_then_fail):
            with self.assertRaisesMessage(
                RuntimeError,
                "simulated media database failure",
            ):
                bundle.save(actor=self.owner)

        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductMedia.objects.exists())
        self.assertEqual(self.stored_files(), ())

    def test_failed_replacement_preserves_existing_media_and_removes_new_file(self):
        product = self.create_product()
        existing_media = self.attach_initial_media(product)
        old_name = existing_media.image.name
        old_path = Path(self._media_directory.name, old_name)
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=draft_bundle_data(name=product.name),
            files={
                "image": product_image_upload(
                    "replacement.webp",
                    image_format="WEBP",
                    content_type="image/webp",
                )
            },
        )
        self.assertTrue(bundle.is_valid(), bundle.media_form.errors)
        original_save = ProductMedia.save

        def save_then_fail(media, *args, **kwargs):
            original_save(media, *args, **kwargs)
            raise RuntimeError("simulated replacement failure")

        with patch.object(ProductMedia, "save", new=save_then_fail):
            with self.assertRaisesMessage(
                RuntimeError,
                "simulated replacement failure",
            ):
                bundle.save(actor=self.owner)

        existing_media.refresh_from_db()
        self.assertEqual(existing_media.image.name, old_name)
        self.assertTrue(old_path.exists())
        self.assertEqual(self.stored_files(), (old_path,))

    def test_edit_without_upload_preserves_existing_media(self):
        product = self.create_product()
        existing_media = self.attach_initial_media(product)
        old_name = existing_media.image.name
        bundle = ProductBundle(
            business=self.business,
            instance=product,
            data=draft_bundle_data(name=product.name),
        )

        self.assertTrue(bundle.is_valid(), bundle.media_form.errors)
        bundle.save(actor=self.owner)

        existing_media.refresh_from_db()
        self.assertEqual(existing_media.image.name, old_name)
        self.assertTrue(Path(self._media_directory.name, old_name).exists())


class ProductMediaViewTests(TemporaryMediaMixin, TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="media-view-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="media-view-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="View Media Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other View Media Studio",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="View media product",
            description="Media response coverage.",
        )
        with transaction.atomic():
            self.media = attach_or_replace_product_media(
                business=self.business,
                product=self.product,
                image=product_image_upload(),
            ).media
        self.url = reverse("catalog:product_media", kwargs={"pk": self.media.pk})

    def test_media_response_requires_auth_and_exact_business_ownership(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

        self.client.force_login(self.other_owner)
        self.assertEqual(self.client.get(self.url).status_code, 404)

        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\x89PNG"))

    def test_media_response_rejects_unsafe_or_missing_storage_state(self):
        safe_name = self.media.image.name
        safe_path = Path(self._media_directory.name, safe_name)
        ProductMedia.objects.filter(pk=self.media.pk).update(image="../private.env")
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(self.url).status_code, 404)

        ProductMedia.objects.filter(pk=self.media.pk).update(image=safe_name)
        safe_path.unlink()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_media_response_rejects_unresolved_business_states(self):
        no_business_owner = get_user_model().objects.create_user(
            email="media-no-business@example.com",
            password="test-password",
        )
        self.client.force_login(no_business_owner)
        self.assertEqual(self.client.get(self.url).status_code, 404)

        Business.objects.create(owner=self.owner, name="Second owned Business")
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_product_create_renders_upload_contract_and_saves_image(self):
        self.client.force_login(self.owner)
        create_url = reverse("catalog:product_create")

        get_response = self.client.get(create_url)
        self.assertContains(get_response, 'enctype="multipart/form-data"')
        self.assertContains(
            get_response,
            'accept="image/jpeg,image/png,image/webp"',
        )
        self.assertContains(get_response, 'aria-describedby="id_image_helptext"')
        self.assertContains(get_response, 'id="id_image_helptext"')
        self.assertContains(get_response, "No Product image selected")

        response = self.client.post(
            create_url,
            {**draft_bundle_data(name="Created with media"), "image": product_image_upload()},
        )

        self.assertRedirects(response, reverse("catalog:product_list"))
        created_media = ProductMedia.objects.exclude(pk=self.media.pk).get()
        self.assertEqual(created_media.business, self.business)
        self.assertEqual(created_media.product.name, "Created with media")

    def test_validation_failure_explains_that_upload_must_be_reselected(self):
        self.client.force_login(self.owner)
        create_url = reverse("catalog:product_create")

        response = self.client.post(
            create_url,
            {**draft_bundle_data(name=""), "image": product_image_upload()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Select the image again before saving.",
        )
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(ProductMedia.objects.count(), 1)

    def test_invalid_image_does_not_create_partial_product_or_media(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("catalog:product_create"),
            {
                **draft_bundle_data(name="Must not persist"),
                "image": SimpleUploadedFile(
                    "broken.png",
                    b"not an image",
                    content_type="image/png",
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload a valid image")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(
            response,
            'aria-describedby="id_image_helptext id_image_error"',
        )
        self.assertContains(response, 'id="id_image_error"')
        self.assertFalse(Product.objects.filter(name="Must not persist").exists())
        self.assertEqual(ProductMedia.objects.count(), 1)

    def test_non_htmx_helper_action_warns_when_browser_clears_selected_file(self):
        self.client.force_login(self.owner)
        data = draft_bundle_data(intent="preview_recognition")

        response = self.client.post(
            reverse("catalog:product_create"),
            {**data, "image": product_image_upload()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Select the image again before saving.",
        )
        self.assertFalse(Product.objects.filter(name="Media product").exists())

    def test_product_edit_attaches_and_then_replaces_one_image(self):
        media_path = Path(self._media_directory.name, self.media.image.name)
        self.client.force_login(self.owner)
        edit_url = reverse(
            "catalog:product_edit",
            kwargs={"pk": self.product.pk},
        )

        get_response = self.client.get(edit_url)
        self.assertContains(get_response, self.url)
        self.assertContains(get_response, "Replace Product image")

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                edit_url,
                {
                    **draft_bundle_data(name=self.product.name),
                    "image": product_image_upload(
                        "replacement.webp",
                        image_format="WEBP",
                        content_type="image/webp",
                    ),
                },
            )

        self.assertRedirects(response, reverse("catalog:product_list"))
        self.media.refresh_from_db()
        self.assertTrue(self.media.image.name.endswith(".webp"))
        self.assertFalse(media_path.exists())
        self.assertEqual(ProductMedia.objects.filter(product=self.product).count(), 1)

    def test_workspace_renders_protected_image_url_and_accessible_placeholder(self):
        product_without_media = Product.objects.create(
            business=self.business,
            name="No media product",
            description="Placeholder coverage.",
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("catalog:product_list"))

        self.assertContains(response, self.url)
        self.assertContains(response, f'alt="Image of {self.product.name}"')
        self.assertContains(
            response,
            f'aria-label="No image available for {product_without_media.name}"',
        )
