from decimal import Decimal
from unittest.mock import patch
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import Client, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.add_similar import add_similar_product
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    BusinessTag,
    Product,
    ProductChoice,
    ProductMaterialFact,
    ProductMedia,
    ProductTag,
)
from catalog.test_media import TemporaryMediaMixin, product_image_upload
from inventory.models import InventoryAdjustment
from inventory.mutations import initialize_choice_quantity


class AddSimilarFixtureMixin:
    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="similar-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="similar-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Seller Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Private Studio",
        )
        self.product_type = BusinessProductType.objects.create(
            business=self.business,
            name="Trousers",
        )
        self.tag = BusinessTag.objects.create(
            business=self.business,
            name="Classic",
        )
        self.size = BusinessSize.objects.create(
            business=self.business,
            name="M",
        )
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.source = Product.objects.create(
            business=self.business,
            product_type=self.product_type,
            name="Classic black trousers",
            description="Classic black trousers",
            price=Decimal("129.90"),
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        ProductTag.objects.create(
            business=self.business,
            product=self.source,
            tag=self.tag,
        )
        self.material = ProductMaterialFact.objects.create(
            business=self.business,
            product=self.source,
            canonical_material="Cotton",
            percentage=70,
            original_text="70% cotton",
            source=ProductMaterialFact.Source.DESCRIPTION,
        )
        self.stocked_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.source,
            size=self.size,
            color=self.color,
            quantity=0,
        )
        initialize_choice_quantity(
            business=self.business,
            choice=self.stocked_choice,
            actor=self.owner,
            quantity=4,
        )
        self.duplicate_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.source,
            size=self.size,
            color=self.color,
            quantity=0,
        )
        self.inactive_choice = ProductChoice.objects.create(
            business=self.business,
            product=self.source,
            size=self.size,
            color=self.color,
            quantity=3,
            is_active=False,
        )

    def edit_data(self, product, *, description):
        choices = list(product.choices.order_by("id"))
        materials = list(product.material_facts.order_by("id"))
        data = {
            "description": description,
            "price": str(product.price or ""),
            "product_type": str(product.product_type_id or ""),
            "tags": [str(tag.pk) for tag in product.tags.all()],
            "lifecycle": product.lifecycle,
            "choices-TOTAL_FORMS": str(len(choices)),
            "choices-INITIAL_FORMS": str(len(choices)),
            "choices-MIN_NUM_FORMS": "0",
            "choices-MAX_NUM_FORMS": "1000",
            "materials-TOTAL_FORMS": str(len(materials)),
            "materials-INITIAL_FORMS": str(len(materials)),
            "materials-MIN_NUM_FORMS": "0",
            "materials-MAX_NUM_FORMS": "1000",
        }
        for index, choice in enumerate(choices):
            data.update(
                {
                    f"choices-{index}-id": str(choice.pk),
                    f"choices-{index}-size": str(choice.size_id),
                    f"choices-{index}-color": str(choice.color_id),
                    f"choices-{index}-quantity": str(choice.quantity),
                    f"choices-{index}-is_active": "on",
                }
            )
        for index, material in enumerate(materials):
            data.update(
                {
                    f"materials-{index}-id": str(material.pk),
                    f"materials-{index}-canonical_material": (
                        material.canonical_material
                    ),
                    f"materials-{index}-percentage": str(
                        material.percentage or ""
                    ),
                    f"materials-{index}-original_text": material.original_text,
                    f"materials-{index}-source": material.source,
                }
            )
        return data


class AddSimilarServiceTests(
    TemporaryMediaMixin,
    AddSimilarFixtureMixin,
    TestCase,
):
    def test_copies_approved_truth_into_new_zero_stock_draft(self):
        ProductMedia.objects.create(
            business=self.business,
            product=self.source,
            image=product_image_upload(),
        )
        source_choice_ids = set(self.source.choices.values_list("pk", flat=True))
        source_adjustment_ids = set(
            InventoryAdjustment.objects.filter(
                choice__product=self.source
            ).values_list("pk", flat=True)
        )

        destination = add_similar_product(
            business=self.business,
            source_product_id=self.source.pk,
        )

        self.assertNotEqual(destination.pk, self.source.pk)
        self.assertEqual(destination.business, self.business)
        self.assertEqual(destination.lifecycle, Product.Lifecycle.DRAFT)
        self.assertEqual(destination.name, self.source.name)
        self.assertEqual(destination.description, self.source.description)
        self.assertEqual(destination.price, self.source.price)
        self.assertEqual(destination.product_type, self.source.product_type)
        self.assertEqual(list(destination.tags.all()), [self.tag])
        copied_material = destination.material_facts.get()
        self.assertEqual(copied_material.canonical_material, "Cotton")
        self.assertEqual(copied_material.percentage, 70)
        self.assertEqual(copied_material.original_text, "70% cotton")
        self.assertEqual(copied_material.source, self.material.source)
        self.assertEqual(
            copied_material.confirmation_state,
            ProductMaterialFact.ConfirmationState.CONFIRMED,
        )

        copied_choices = list(destination.choices.order_by("id"))
        self.assertEqual(len(copied_choices), 2)
        self.assertTrue(all(choice.is_active for choice in copied_choices))
        self.assertTrue(all(choice.quantity == 0 for choice in copied_choices))
        self.assertTrue(
            all(
                choice.size_id == self.size.pk
                and choice.color_id == self.color.pk
                for choice in copied_choices
            )
        )
        self.assertTrue(
            source_choice_ids.isdisjoint(choice.pk for choice in copied_choices)
        )
        self.assertFalse(ProductMedia.objects.filter(product=destination).exists())
        self.assertFalse(
            InventoryAdjustment.objects.filter(
                choice__product=destination
            ).exists()
        )

        self.source.refresh_from_db()
        self.assertEqual(self.source.lifecycle, Product.Lifecycle.ACTIVE)
        self.assertEqual(self.stocked_choice.quantity, 0)
        self.stocked_choice.refresh_from_db()
        self.assertEqual(self.stocked_choice.quantity, 4)
        self.assertEqual(
            set(
                InventoryAdjustment.objects.filter(
                    choice__product=self.source
                ).values_list("pk", flat=True)
            ),
            source_adjustment_ids,
        )
        self.assertTrue(ProductMedia.objects.filter(product=self.source).exists())

    def test_cross_business_source_is_rejected_without_writes(self):
        starting_product_count = Product.objects.count()

        with self.assertRaises(Product.DoesNotExist):
            add_similar_product(
                business=self.other_business,
                source_product_id=self.source.pk,
            )

        self.assertEqual(Product.objects.count(), starting_product_count)

    def test_related_write_failure_rolls_back_entire_destination(self):
        starting_product_ids = set(Product.objects.values_list("pk", flat=True))
        starting_tag_links = ProductTag.objects.count()
        starting_materials = ProductMaterialFact.objects.count()

        with patch(
            "catalog.add_similar.ProductChoice.save",
            side_effect=DatabaseError("choice write failed"),
        ):
            with self.assertRaises(DatabaseError):
                add_similar_product(
                    business=self.business,
                    source_product_id=self.source.pk,
                )

        self.assertEqual(
            set(Product.objects.values_list("pk", flat=True)),
            starting_product_ids,
        )
        self.assertEqual(ProductTag.objects.count(), starting_tag_links)
        self.assertEqual(ProductMaterialFact.objects.count(), starting_materials)


class AddSimilarViewTests(AddSimilarFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("catalog:product_list")
        self.url = reverse(
            "catalog:product_add_similar",
            args=[self.source.pk],
        )

    def test_requires_authentication_and_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

        self.client.force_login(self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_csrf_failure_creates_nothing(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        starting_product_count = Product.objects.count()

        response = csrf_client.post(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.count(), starting_product_count)

    def test_cross_business_request_returns_not_found_without_writes(self):
        self.client.force_login(self.other_owner)
        starting_product_count = Product.objects.count()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Product.objects.count(), starting_product_count)

    def test_workspace_action_creates_draft_and_opens_normal_edit_flow(self):
        self.client.force_login(self.owner)
        workspace_url = f"{self.list_url}?q=classic&lifecycle=active"

        workspace_response = self.client.get(workspace_url)

        self.assertContains(workspace_response, f'action="{self.url}"', count=1)
        self.assertContains(workspace_response, ">Add similar</button>", count=1)

        response = self.client.post(self.url, {"next": workspace_url})
        destination = Product.objects.exclude(pk=self.source.pk).get()
        expected_edit_url = reverse(
            "catalog:product_edit",
            args=[destination.pk],
        )
        expected_location = (
            f"{expected_edit_url}?{urlencode({'next': workspace_url})}"
        )

        self.assertRedirects(
            response,
            expected_location,
            fetch_redirect_response=False,
        )
        edit_response = self.client.get(response.url)
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(edit_response.context["product"], destination)
        self.assertEqual(edit_response.context["return_url"], workspace_url)
        self.assertContains(
            edit_response,
            "Similar Product created as a Draft. Review it before activation.",
        )

        edit_data = self.edit_data(
            destination,
            description="Classic black trousers with a new detail",
        )
        edit_data["next"] = workspace_url
        save_response = self.client.post(expected_edit_url, edit_data)

        self.assertRedirects(
            save_response,
            workspace_url,
            fetch_redirect_response=False,
        )
        destination.refresh_from_db()
        self.assertEqual(
            destination.description,
            "Classic black trousers with a new detail",
        )

    def test_unsafe_return_falls_back_to_workspace(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            {"next": "https://example.com/escape"},
        )
        destination = Product.objects.exclude(pk=self.source.pk).get()
        expected_edit_url = reverse(
            "catalog:product_edit",
            args=[destination.pk],
        )

        self.assertRedirects(
            response,
            f"{expected_edit_url}?{urlencode({'next': self.list_url})}",
            fetch_redirect_response=False,
        )
