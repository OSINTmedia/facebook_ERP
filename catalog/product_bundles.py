"""Atomic Product and ProductChoice validation and persistence boundary."""

from django.core.exceptions import ValidationError
from django.db import transaction

from catalog.forms import ProductChoiceFormSet, ProductForm
from catalog.models import Product, ProductChoice, ProductTag


class ProductBundle:
    """Coordinate Product and choice forms without trusting ownership input."""

    def __init__(self, *, business, data=None, instance=None, choice_prefix="choices"):
        self.business = business
        self.product = instance or Product()
        self.product_form = ProductForm(
            data=data,
            instance=self.product,
            business=business,
        )
        self.choice_formset = ProductChoiceFormSet(
            data=data,
            instance=self.product,
            prefix=choice_prefix,
            queryset=ProductChoice.objects.filter(business=business),
            form_kwargs={"business": business},
        )
        self._validated = False
        self._is_valid = False

    def is_valid(self):
        """Validate Product first so its cleaned lifecycle drives formset rules."""
        product_is_valid = self.product_form.is_valid()

        if (
            self.product.pk
            and self.product.business_id != self.business.pk
        ):
            self.product_form.add_error(
                None,
                "Product must belong to the active Business.",
            )
            product_is_valid = False

        choices_are_valid = self.choice_formset.is_valid()
        self._validated = True
        self._is_valid = product_is_valid and choices_are_valid
        return self._is_valid

    def save(self):
        """Persist a previously validated bundle as one database transaction."""
        if not self._validated:
            raise ValueError("Validate the Product bundle before saving it.")
        if not self._is_valid:
            raise ValueError("Cannot save an invalid Product bundle.")

        with transaction.atomic():
            product = self.product_form.save(commit=False)
            product.business = self.business
            product.full_clean()
            product.save()

            self.choice_formset.instance = product
            choices = self.choice_formset.save(commit=False)

            for choice in self.choice_formset.deleted_objects:
                self._validate_choice_scope(choice, product)
                choice.delete()

            for choice in choices:
                choice.business = self.business
                choice.product = product
                choice.full_clean()
                choice.save()

            self.choice_formset.save_m2m()
            self._replace_product_tags(
                product,
                tuple(self.product_form.cleaned_data["tags"]),
            )

        return product

    def _validate_choice_scope(self, choice, product):
        if (
            choice.product_id != product.pk
            or choice.business_id != self.business.pk
        ):
            raise ValidationError(
                "Choice must belong to the Product and active Business."
            )

    def _replace_product_tags(self, product, selected_tags):
        selected_tag_ids = set()
        for tag in selected_tags:
            if tag.business_id != self.business.pk:
                raise ValidationError("Tag must belong to the active Business.")
            selected_tag_ids.add(tag.pk)

        existing_links = list(
            ProductTag.objects.select_for_update().filter(product=product)
        )
        for link in existing_links:
            if link.business_id != self.business.pk:
                raise ValidationError(
                    "Product tags must belong to the active Business."
                )

        existing_tag_ids = {link.tag_id for link in existing_links}
        for link in existing_links:
            if link.tag_id not in selected_tag_ids:
                link.delete()

        for tag in selected_tags:
            if tag.pk in existing_tag_ids:
                continue
            link = ProductTag(
                business=self.business,
                product=product,
                tag=tag,
            )
            link.full_clean()
            link.save()
