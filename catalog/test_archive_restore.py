from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from businesses.models import Business
from catalog.add_similar import add_similar_product
from catalog.lifecycle import archive_product, restore_product_to_draft
from catalog.models import BusinessColor, BusinessSize, Product, ProductChoice
from catalog.product_bundles import ArchivedProductMutationError, ProductBundle
from catalog.readiness import build_product_buyer_question_coverage
from catalog.ready_reply import build_product_ready_reply
from inventory.models import InventoryAdjustment
from inventory.mutations import (
    apply_choice_quantity_delta,
    initialize_choice_quantity,
    set_choice_quantity,
)


class ArchiveRestoreFixtureMixin:
    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            email="archive-owner@example.com",
            password="test-password",
        )
        self.other_owner = user_model.objects.create_user(
            email="archive-other@example.com",
            password="test-password",
        )
        self.business = Business.objects.create(
            owner=self.owner,
            name="Archive Studio",
        )
        self.other_business = Business.objects.create(
            owner=self.other_owner,
            name="Other Archive Studio",
        )
        self.size = BusinessSize.objects.create(business=self.business, name="M")
        self.color = BusinessColor.objects.create(
            business=self.business,
            name="Black",
        )
        self.product = Product.objects.create(
            business=self.business,
            name="Archive trousers",
            description="Archive trousers",
            lifecycle=Product.Lifecycle.ACTIVE,
        )
        self.choice = ProductChoice.objects.create(
            business=self.business,
            product=self.product,
            size=self.size,
            color=self.color,
            quantity=0,
        )
        initialize_choice_quantity(
            business=self.business,
            choice=self.choice,
            actor=self.owner,
            quantity=4,
        )
        self.list_url = reverse("catalog:product_list")
        self.archive_url = reverse(
            "catalog:product_archive",
            args=[self.product.pk],
        )
        self.restore_url = reverse(
            "catalog:product_restore",
            args=[self.product.pk],
        )

    def bundle_data(self):
        return {
            "description": self.product.description,
            "price": "",
            "product_type": "",
            "tags": [],
            "lifecycle": Product.Lifecycle.ACTIVE,
            "choices-TOTAL_FORMS": "1",
            "choices-INITIAL_FORMS": "1",
            "choices-MIN_NUM_FORMS": "0",
            "choices-MAX_NUM_FORMS": "1000",
            "choices-0-id": str(self.choice.pk),
            "choices-0-size": str(self.size.pk),
            "choices-0-color": str(self.color.pk),
            "choices-0-quantity": str(self.choice.quantity),
            "choices-0-is_active": "on",
            "materials-TOTAL_FORMS": "0",
            "materials-INITIAL_FORMS": "0",
            "materials-MIN_NUM_FORMS": "0",
            "materials-MAX_NUM_FORMS": "1000",
        }

    def assert_related_truth_is_preserved(self):
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.quantity, 4)
        self.assertTrue(self.choice.is_active)
        adjustment = InventoryAdjustment.objects.get(choice=self.choice)
        self.assertEqual(adjustment.quantity_before, 0)
        self.assertEqual(adjustment.quantity_after, 4)


class ProductArchiveRestoreServiceTests(ArchiveRestoreFixtureMixin, TestCase):
    def test_archive_and_restore_preserve_truth_and_restore_only_to_draft(self):
        archived = archive_product(
            business=self.business,
            product_id=self.product.pk,
        )

        self.assertEqual(archived.lifecycle, Product.Lifecycle.ARCHIVED)
        self.assert_related_truth_is_preserved()

        restored = restore_product_to_draft(
            business=self.business,
            product_id=self.product.pk,
        )

        self.assertEqual(restored.lifecycle, Product.Lifecycle.DRAFT)
        self.assert_related_truth_is_preserved()

    def test_archive_accepts_draft_but_repeated_transitions_are_rejected(self):
        self.product.lifecycle = Product.Lifecycle.DRAFT
        self.product.save(update_fields=["lifecycle", "updated_at"])

        archive_product(business=self.business, product_id=self.product.pk)

        with self.assertRaisesMessage(
            ValidationError,
            "Only a Draft or Active Product can be archived.",
        ):
            archive_product(business=self.business, product_id=self.product.pk)

        restore_product_to_draft(
            business=self.business,
            product_id=self.product.pk,
        )
        with self.assertRaisesMessage(
            ValidationError,
            "Only an archived Product can be restored.",
        ):
            restore_product_to_draft(
                business=self.business,
                product_id=self.product.pk,
            )

    def test_archived_truth_is_unavailable_to_sellable_consumers(self):
        archive_product(business=self.business, product_id=self.product.pk)
        self.product.refresh_from_db()

        with self.assertRaisesMessage(
            ValidationError,
            "Archived Products do not have sellable buyer-question coverage.",
        ):
            build_product_buyer_question_coverage(
                business=self.business,
                product=self.product,
            )
        with self.assertRaisesMessage(
            ValidationError,
            "Archived Products cannot produce a Ready Reply.",
        ):
            build_product_ready_reply(
                business=self.business,
                product=self.product,
            )
        with self.assertRaises(Product.DoesNotExist):
            add_similar_product(
                business=self.business,
                source_product_id=self.product.pk,
            )

    def test_archived_choices_reject_every_stock_command_without_new_ledger(self):
        archive_product(business=self.business, product_id=self.product.pk)

        commands = (
            lambda: apply_choice_quantity_delta(
                business=self.business,
                choice=self.choice,
                actor=self.owner,
                delta=1,
            ),
            lambda: set_choice_quantity(
                business=self.business,
                choice=self.choice,
                actor=self.owner,
                quantity=8,
            ),
            lambda: initialize_choice_quantity(
                business=self.business,
                choice=self.choice,
                actor=self.owner,
                quantity=8,
            ),
        )
        for command in commands:
            with self.subTest(command=command):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Archived Product stock cannot be changed.",
                ):
                    command()

        self.assert_related_truth_is_preserved()
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_validated_edit_cannot_overwrite_a_concurrent_archive(self):
        bundle = ProductBundle(
            business=self.business,
            data=self.bundle_data(),
            instance=self.product,
        )
        self.assertTrue(bundle.is_valid(), bundle.product_form.errors)
        archive_product(business=self.business, product_id=self.product.pk)

        with self.assertRaisesMessage(
            ArchivedProductMutationError,
            "Restore the archived Product to Draft before editing it.",
        ):
            bundle.save(actor=self.owner)

        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ARCHIVED)
        self.assert_related_truth_is_preserved()


class ProductArchiveRestoreViewTests(ArchiveRestoreFixtureMixin, TestCase):
    def test_mutations_require_authentication_post_and_csrf(self):
        response = self.client.post(self.archive_url)
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.archive_url}",
        )

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.archive_url).status_code, 405)
        self.assertEqual(self.client.get(self.restore_url).status_code, 405)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        self.assertEqual(csrf_client.post(self.archive_url).status_code, 403)
        self.assertEqual(csrf_client.post(self.restore_url).status_code, 403)
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_archive_and_restore_preserve_canonical_workspace_return(self):
        self.client.force_login(self.owner)
        active_workspace = f"{self.list_url}?q=archive&lifecycle=active"

        archive_response = self.client.post(
            self.archive_url,
            {"next": active_workspace},
        )

        self.assertRedirects(
            archive_response,
            active_workspace,
            fetch_redirect_response=False,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ARCHIVED)

        archived_workspace = f"{self.list_url}?lifecycle=archived"
        restore_response = self.client.post(
            self.restore_url,
            {"next": archived_workspace},
        )

        self.assertRedirects(
            restore_response,
            archived_workspace,
            fetch_redirect_response=False,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.DRAFT)
        self.assert_related_truth_is_preserved()

    def test_unsafe_return_falls_back_to_workspace(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            self.archive_url,
            {"next": "https://example.com/escape"},
        )

        self.assertRedirects(
            response,
            self.list_url,
            fetch_redirect_response=False,
        )

    def test_archived_product_blocks_normal_mutation_and_reply_views(self):
        archive_product(business=self.business, product_id=self.product.pk)
        self.client.force_login(self.owner)

        blocked_urls = (
            reverse("catalog:product_edit", args=[self.product.pk]),
            reverse("catalog:product_add_similar", args=[self.product.pk]),
            reverse("catalog:product_ready_reply", args=[self.product.pk]),
        )
        self.assertEqual(self.client.get(blocked_urls[0]).status_code, 404)
        self.assertEqual(self.client.post(blocked_urls[1]).status_code, 404)
        self.assertEqual(self.client.get(blocked_urls[2]).status_code, 404)

    def test_archived_product_rejects_direct_stock_route_without_writes(self):
        archive_product(business=self.business, product_id=self.product.pk)
        self.client.force_login(self.owner)
        stock_url = reverse(
            "inventory:choice_stock_adjust",
            args=[self.choice.pk],
        )

        response = self.client.post(
            stock_url,
            {"delta": "1", "next": self.list_url},
        )

        self.assertRedirects(
            response,
            self.list_url,
            fetch_redirect_response=False,
        )
        self.assert_related_truth_is_preserved()
        self.assertEqual(InventoryAdjustment.objects.count(), 1)

    def test_missing_and_invalid_state_requests_write_nothing(self):
        self.client.force_login(self.owner)
        missing_archive_url = reverse("catalog:product_archive", args=[999999])

        self.assertEqual(self.client.post(missing_archive_url).status_code, 404)
        response = self.client.post(
            self.restore_url,
            {"next": self.list_url},
        )

        self.assertRedirects(
            response,
            self.list_url,
            fetch_redirect_response=False,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)
        self.assert_related_truth_is_preserved()


class ProductArchiveRestoreWorkspaceTests(ArchiveRestoreFixtureMixin, TestCase):
    def test_default_workspace_excludes_archived_and_filter_retrieves_it(self):
        archive_product(business=self.business, product_id=self.product.pk)
        self.client.force_login(self.owner)

        default_response = self.client.get(self.list_url)
        archived_response = self.client.get(
            self.list_url,
            {"lifecycle": Product.Lifecycle.ARCHIVED},
        )

        self.assertNotContains(default_response, self.product.name)
        self.assertContains(
            default_response,
            "ყოველდღიურ სამუშაოში პროდუქტები არ არის. დაარქივებული პროდუქტები შენახულია.",
        )
        self.assertContains(
            default_response,
            f'href="{self.list_url}?lifecycle=archived"',
            count=1,
        )
        self.assertEqual(
            list(archived_response.context["products"]),
            [self.product],
        )
        self.assertContains(archived_response, "სტატუსი — დაარქივებული")
        self.assertContains(archived_response, "დაარქივებული პროდუქტი")
        self.assertContains(archived_response, ">მონახაზად აღდგენა</button>")
        self.assertContains(
            archived_response,
            f'action="{self.restore_url}"',
            count=1,
        )
        self.assertNotContains(
            archived_response,
            reverse("inventory:choice_stock_adjust", args=[self.choice.pk]),
        )
        self.assertNotContains(
            archived_response,
            reverse("catalog:product_ready_reply", args=[self.product.pk]),
        )
        self.assertNotContains(
            archived_response,
            reverse("catalog:product_edit", args=[self.product.pk]),
        )
        self.assertNotContains(
            archived_response,
            reverse("catalog:product_add_similar", args=[self.product.pk]),
        )

    def test_daily_card_requires_explicit_secondary_archive_confirmation(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.list_url)
        content = response.content.decode()

        self.assertContains(response, "<summary>პროდუქტის დაარქივება</summary>")
        self.assertContains(response, ">დაარქივების დადასტურება</button>")
        self.assertContains(response, f'action="{self.archive_url}"', count=1)
        self.assertLess(
            content.index(">+1</button>"),
            content.index("პროდუქტის დაარქივება"),
        )


class ProductArchiveRestoreIsolationTests(ArchiveRestoreFixtureMixin, TestCase):
    def test_service_scope_rejects_another_business_without_mutation(self):
        with self.assertRaises(Product.DoesNotExist):
            archive_product(
                business=self.other_business,
                product_id=self.product.pk,
            )

        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)

    def test_view_scope_returns_not_found_without_disclosing_or_mutating(self):
        self.client.force_login(self.other_owner)

        response = self.client.post(self.archive_url)

        self.assertEqual(response.status_code, 404)
        self.product.refresh_from_db()
        self.assertEqual(self.product.lifecycle, Product.Lifecycle.ACTIVE)
