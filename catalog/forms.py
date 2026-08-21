import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    BusinessTag,
    Product,
    ProductChoice,
    ProductMaterialFact,
)
from catalog.vocabulary import (
    COLOR_VOCABULARY,
    PRODUCT_TYPE_VOCABULARY,
    SIZE_VOCABULARY,
    TAG_VOCABULARY,
)


class ProductForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=BusinessTag.objects.none(),
        required=False,
        label="Confirmed tags",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "classification-options"}
        ),
    )

    class Meta:
        model = Product
        fields = ["name", "description", "product_type", "tags", "lifecycle"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "hx-post": ".",
                    "hx-trigger": "input changed delay:600ms",
                    "hx-target": "#recognition-preview-region",
                    "hx-swap": "outerHTML",
                    "hx-include": "closest form",
                    "hx-vals": '{"intent": "preview_recognition"}',
                    "hx-indicator": "#recognition-preview-loading",
                    "hx-sync": "closest form:replace",
                }
            )
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        product_types = BusinessProductType.objects.none()
        tags = BusinessTag.objects.none()

        if business is not None:
            product_type_filter = Q(business=business, is_active=True)
            tag_filter = Q(business=business, is_active=True)
            if self.instance.pk and self.instance.business_id == business.pk:
                product_type_filter = Q(business=business) & (
                    Q(is_active=True) | Q(pk=self.instance.product_type_id)
                )
                tag_filter = Q(business=business) & (
                    Q(is_active=True) | Q(products=self.instance)
                )

            product_types = BusinessProductType.objects.filter(
                product_type_filter
            ).order_by("name", "id")
            tags = BusinessTag.objects.filter(tag_filter).distinct().order_by(
                "name",
                "id",
            )
            if (
                not self.is_bound
                and self.instance.pk
                and self.instance.business_id == business.pk
            ):
                self.initial["tags"] = self.instance.tags.filter(
                    product_links__business=business
                )

        self.fields["product_type"].queryset = product_types
        self.fields["product_type"].empty_label = "No confirmed product type"
        self.fields["product_type"].label = "Confirmed product type"
        self.fields["tags"].queryset = tags


class ProductChoiceForm(forms.ModelForm):
    class Meta:
        model = ProductChoice
        fields = ["size", "color", "quantity", "is_active"]

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        size_queryset = BusinessSize.objects.none()
        color_queryset = BusinessColor.objects.none()

        if business is not None:
            size_filter = Q(business=business, is_active=True)
            color_filter = Q(business=business, is_active=True)
            if self.instance.pk and self.instance.business_id == business.pk:
                size_filter |= Q(pk=self.instance.size_id)
                color_filter |= Q(pk=self.instance.color_id)

            size_queryset = BusinessSize.objects.filter(size_filter).order_by("name", "id")
            color_queryset = BusinessColor.objects.filter(color_filter).order_by(
                "name",
                "id",
            )

        self.fields["size"].queryset = size_queryset
        self.fields["size"].empty_label = "Select size"
        self.fields["color"].queryset = color_queryset
        self.fields["color"].empty_label = "Select color"

    def has_changed(self):
        """Ignore untouched extra rows whose only values are model defaults."""
        if self.is_bound and not self.instance.pk:
            size = self.data.get(self.add_prefix("size"))
            color = self.data.get(self.add_prefix("color"))
            quantity = self.data.get(self.add_prefix("quantity"))
            if (
                not str(size or "").strip()
                and not str(color or "").strip()
                and quantity in (None, "", "0", 0)
            ):
                return False
        return super().has_changed()


class ProductMaterialFactForm(forms.ModelForm):
    class Meta:
        model = ProductMaterialFact
        fields = ["canonical_material", "percentage", "original_text", "source"]
        labels = {
            "canonical_material": "Canonical material",
            "percentage": "Percentage",
            "original_text": "Original seller wording",
            "source": "Source",
        }
        widgets = {
            "percentage": forms.NumberInput(attrs={"min": 1, "max": 100}),
        }

    def __init__(self, *args, business=None, **kwargs):
        self.business = business
        super().__init__(*args, **kwargs)
        self.fields["percentage"].widget.attrs.update({"min": 1, "max": 100})
        if not self.is_bound and not self.instance.pk:
            self.initial.setdefault("source", ProductMaterialFact.Source.MANUAL)

    def clean(self):
        cleaned_data = super().clean()
        if (
            self.business is not None
            and self.instance.pk
            and self.instance.business_id != self.business.pk
        ):
            raise ValidationError(
                "Material fact must belong to the active Business."
            )
        return cleaned_data

    def has_changed(self):
        """Ignore untouched extra rows even when Manual is the displayed source."""
        if self.is_bound and not self.instance.pk:
            material = self.data.get(self.add_prefix("canonical_material"))
            percentage = self.data.get(self.add_prefix("percentage"))
            original_text = self.data.get(self.add_prefix("original_text"))
            delete = self.data.get(self.add_prefix("DELETE"))
            if (
                not str(material or "").strip()
                and not str(percentage or "").strip()
                and not str(original_text or "").strip()
                and str(delete or "").casefold() not in {"1", "true", "on", "yes"}
            ):
                return False
        return super().has_changed()


class ChoiceVocabularyForm(forms.Form):
    name = forms.CharField()
    aliases = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Optional: comma-separated alternative wording"}
        ),
    )

    def __init__(self, *args, kind, **kwargs):
        labels = {
            SIZE_VOCABULARY: "Size",
            COLOR_VOCABULARY: "Color",
            PRODUCT_TYPE_VOCABULARY: "Product type",
            TAG_VOCABULARY: "Tag",
        }
        if kind not in labels:
            raise ValueError("Unsupported vocabulary kind.")
        self.kind = kind
        super().__init__(*args, **kwargs)

        label = labels[kind]
        self.fields["name"].label = f"Canonical {label.lower()}"
        self.fields["name"].max_length = 40 if kind == SIZE_VOCABULARY else 80
        self.fields["aliases"].label = "Approved aliases"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError("Canonical value is required.")
        return name

    def clean_aliases(self):
        raw_aliases = self.cleaned_data.get("aliases", "")
        aliases = []
        seen = set()
        max_length = 120 if self.kind == COLOR_VOCABULARY else 80

        for raw_alias in re.split(r"[,\n]+", raw_aliases):
            alias = raw_alias.strip()
            if not alias:
                continue
            if len(alias) > max_length:
                raise ValidationError(
                    f"Each alias must contain at most {max_length} characters."
                )
            normalized = alias.casefold()
            if normalized not in seen:
                seen.add(normalized)
                aliases.append(alias)

        return tuple(aliases)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        aliases = cleaned_data.get("aliases", ())
        if name and name.casefold() in {alias.casefold() for alias in aliases}:
            self.add_error(
                "aliases",
                "An alias must differ from the canonical value.",
            )
        return cleaned_data


class ChoiceVocabularyEditForm(ChoiceVocabularyForm):
    is_active = forms.BooleanField(
        required=False,
        label="Available for new choices and recognition",
    )

    def __init__(self, *args, kind, instance, **kwargs):
        self.instance = instance
        initial = kwargs.setdefault("initial", {})
        initial.setdefault("name", instance.name)
        initial.setdefault(
            "aliases",
            ", ".join(alias.alias for alias in instance.aliases.all()),
        )
        initial.setdefault("is_active", instance.is_active)
        super().__init__(*args, kind=kind, **kwargs)
        self.fields["is_active"].label = (
            "Available for new selection and recognition"
        )


class BaseProductChoiceFormSet(BaseInlineFormSet):
    """Validate Product choices together at the Product bundle boundary."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["id"].queryset = self.get_queryset()

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        active_choices = 0
        for form in self.forms:
            if not form.cleaned_data or self._should_delete_form(form):
                continue
            if form.cleaned_data.get("is_active"):
                active_choices += 1

        if (
            self.instance.lifecycle == Product.Lifecycle.ACTIVE
            and active_choices == 0
        ):
            raise ValidationError(
                "An active product requires at least one active choice."
            )


ProductChoiceFormSet = inlineformset_factory(
    Product,
    ProductChoice,
    form=ProductChoiceForm,
    formset=BaseProductChoiceFormSet,
    fields=["size", "color", "quantity", "is_active"],
    extra=1,
    can_delete=True,
)


class BaseProductMaterialFactFormSet(BaseInlineFormSet):
    """Keep material fact identity scoped to the active Product bundle."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["id"].queryset = self.get_queryset()


ProductMaterialFactFormSet = inlineformset_factory(
    Product,
    ProductMaterialFact,
    form=ProductMaterialFactForm,
    formset=BaseProductMaterialFactFormSet,
    fields=["canonical_material", "percentage", "original_text", "source"],
    extra=2,
    can_delete=True,
)
