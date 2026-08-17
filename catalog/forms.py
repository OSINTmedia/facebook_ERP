import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from catalog.models import BusinessColor, BusinessSize, Product, ProductChoice
from catalog.vocabulary import COLOR_VOCABULARY, SIZE_VOCABULARY


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "lifecycle"]
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


class ChoiceVocabularyForm(forms.Form):
    name = forms.CharField()
    aliases = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Optional: comma-separated alternative wording"}
        ),
    )

    def __init__(self, *args, kind, **kwargs):
        if kind not in {SIZE_VOCABULARY, COLOR_VOCABULARY}:
            raise ValueError("Choice vocabulary kind must be size or color.")
        self.kind = kind
        super().__init__(*args, **kwargs)

        label = "Size" if kind == SIZE_VOCABULARY else "Color"
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
        max_length = 80 if self.kind == SIZE_VOCABULARY else 120

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
