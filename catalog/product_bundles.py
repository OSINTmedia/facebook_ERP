"""Atomic Product, ProductChoice, and material-fact persistence boundary."""

from django.core.exceptions import ValidationError
from django.db import transaction

from catalog.forms import (
    ProductChoiceFormSet,
    ProductForm,
    ProductMaterialFactFormSet,
)
from catalog.models import Product, ProductChoice, ProductMaterialFact, ProductTag


class ProductBundle:
    """Coordinate Product, choice, and material forms at one atomic boundary."""

    def __init__(
        self,
        *,
        business,
        data=None,
        instance=None,
        choice_prefix="choices",
        material_prefix="materials",
    ):
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
        self.material_formset = ProductMaterialFactFormSet(
            data=data,
            instance=self.product,
            prefix=material_prefix,
            queryset=ProductMaterialFact.objects.filter(business=business),
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
        materials_are_valid = self.material_formset.is_valid()
        self._validated = True
        self._is_valid = (
            product_is_valid and choices_are_valid and materials_are_valid
        )
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
            self.material_formset.instance = product
            material_facts = self.material_formset.save(commit=False)

            for material_fact in self.material_formset.deleted_objects:
                self._validate_material_scope(material_fact, product)
                material_fact.delete()

            for material_fact in material_facts:
                material_fact.business = self.business
                material_fact.product = product
                material_fact.confirmation_state = (
                    ProductMaterialFact.ConfirmationState.CONFIRMED
                )
                material_fact.full_clean()
                material_fact.save()

        return product

    def _validate_choice_scope(self, choice, product):
        if (
            choice.product_id != product.pk
            or choice.business_id != self.business.pk
        ):
            raise ValidationError(
                "Choice must belong to the Product and active Business."
            )

    def _validate_material_scope(self, material_fact, product):
        if (
            material_fact.product_id != product.pk
            or material_fact.business_id != self.business.pk
        ):
            raise ValidationError(
                "Material fact must belong to the Product and active Business."
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
