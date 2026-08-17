from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from catalog.models import Product, ProductChoice


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "lifecycle"]


class ProductChoiceForm(forms.ModelForm):
    class Meta:
        model = ProductChoice
        fields = ["size", "color", "quantity", "is_active"]

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
