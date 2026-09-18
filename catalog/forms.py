import re
import unicodedata

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
from catalog.product_media import validate_declared_product_media_type
from catalog.vocabulary import (
    COLOR_VOCABULARY,
    PRODUCT_TYPE_VOCABULARY,
    SIZE_VOCABULARY,
    TAG_VOCABULARY,
)
from dashboard.attention import ATTENTION_FILTER_CHOICES


PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH = 120
PRODUCT_WORKSPACE_SEARCH_MAX_TOKENS = 8
PRODUCT_WORKSPACE_LIFECYCLE_CHOICES = (
    ("", "ყველა სტატუსი"),
    (Product.Lifecycle.ACTIVE, "აქტიური"),
    (Product.Lifecycle.DRAFT, "მონახაზი"),
    (Product.Lifecycle.ARCHIVED, "დაარქივებული"),
)
PRODUCT_WORKSPACE_AVAILABILITY_CHOICES = (
    ("", "ყველა ხელმისაწვდომობა"),
    ("available", "მარაგშია"),
    ("sold_out", "ამოიწურა"),
)
PRODUCT_WORKSPACE_ORIGIN_CHOICES = (
    ("", ""),
    ("dashboard", "მიმოხილვა"),
)
PRODUCT_FORM_LIFECYCLE_CHOICES = (
    (Product.Lifecycle.DRAFT, "მონახაზი"),
    (Product.Lifecycle.ACTIVE, "აქტიური"),
)


class ProductWorkspaceSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="პროდუქტების ძიება",
        help_text="გამოიყენეთ მაქსიმუმ 8 სიტყვა.",
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "autocomplete": "off",
                "maxlength": PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH,
                "placeholder": "აღწერა, ტიპი, ჭდე, არჩევანი ან მასალა",
            }
        ),
    )
    lifecycle = forms.ChoiceField(
        required=False,
        label="სტატუსი",
        choices=PRODUCT_WORKSPACE_LIFECYCLE_CHOICES,
        error_messages={"invalid_choice": "აირჩიეთ დასაშვები მნიშვნელობა."},
    )
    availability = forms.ChoiceField(
        required=False,
        label="ხელმისაწვდომობა",
        choices=PRODUCT_WORKSPACE_AVAILABILITY_CHOICES,
        error_messages={"invalid_choice": "აირჩიეთ დასაშვები მნიშვნელობა."},
    )
    attention = forms.ChoiceField(
        required=False,
        label="საჭიროებს ყურადღებას",
        choices=ATTENTION_FILTER_CHOICES,
        error_messages={"invalid_choice": "აირჩიეთ დასაშვები მნიშვნელობა."},
    )
    origin = forms.ChoiceField(
        required=False,
        choices=PRODUCT_WORKSPACE_ORIGIN_CHOICES,
        widget=forms.HiddenInput,
        error_messages={"invalid_choice": "აირჩიეთ დასაშვები მნიშვნელობა."},
    )

    def clean_q(self):
        if hasattr(self.data, "getlist") and len(self.data.getlist("q")) > 1:
            raise ValidationError("შეიყვანეთ ერთი საძიებო მოთხოვნა.")

        query = " ".join((self.cleaned_data.get("q") or "").split())
        if any(
            unicodedata.category(character) in {"Cc", "Cs"}
            for character in query
        ):
            raise ValidationError("ძიება შეუთავსებელ სიმბოლოებს შეიცავს.")
        if len(query) > PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH:
            raise ValidationError(
                f"ძიება მაქსიმუმ {PRODUCT_WORKSPACE_SEARCH_MAX_LENGTH} სიმბოლოს უნდა შეიცავდეს."
            )
        if len(query.split()) > PRODUCT_WORKSPACE_SEARCH_MAX_TOKENS:
            raise ValidationError(
                f"ძიებაში მაქსიმუმ {PRODUCT_WORKSPACE_SEARCH_MAX_TOKENS} სიტყვა გამოიყენეთ."
            )
        return query

    def clean_lifecycle(self):
        if (
            hasattr(self.data, "getlist")
            and len(self.data.getlist("lifecycle")) > 1
        ):
            raise ValidationError("აირჩიეთ ერთი სტატუსის ფილტრი.")
        return self.cleaned_data.get("lifecycle", "")

    def clean_availability(self):
        if (
            hasattr(self.data, "getlist")
            and len(self.data.getlist("availability")) > 1
        ):
            raise ValidationError("აირჩიეთ ერთი ხელმისაწვდომობის ფილტრი.")
        return self.cleaned_data.get("availability", "")

    def clean_attention(self):
        if (
            hasattr(self.data, "getlist")
            and len(self.data.getlist("attention")) > 1
        ):
            raise ValidationError("აირჩიეთ ერთი საყურადღებო ფილტრი.")
        return self.cleaned_data.get("attention", "")

    def clean_origin(self):
        if (
            hasattr(self.data, "getlist")
            and len(self.data.getlist("origin")) > 1
        ):
            raise ValidationError("აირჩიეთ ერთი დასაბრუნებელი სივრცე.")
        return self.cleaned_data.get("origin", "")


class ProductForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=BusinessTag.objects.none(),
        required=False,
        label="დადასტურებული ჭდეები",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "classification-options"}
        ),
    )

    class Meta:
        model = Product
        fields = [
            "description",
            "price",
            "product_type",
            "tags",
            "lifecycle",
        ]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "autofocus": True,
                    "rows": 4,
                    "hx-post": ".",
                    "hx-trigger": "input changed delay:600ms",
                    "hx-target": "#recognition-preview-region",
                    "hx-swap": "outerHTML",
                    "hx-include": "closest form",
                    "hx-vals": '{"intent": "preview_recognition"}',
                    "hx-indicator": "#recognition-preview-loading",
                    "hx-sync": "closest form:replace",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "min": "0.01",
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
        }
        help_texts = {
            "description": (
                "დაიწყეთ იმ სიტყვებით, რომლებსაც ამ პროდუქტისთვის უკვე იყენებთ. "
                "ამოცნობილი მნიშვნელობა დადასტურებამდე მხოლოდ შეთავაზებაა."
            ),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].label = "აღწერა"
        self.fields["lifecycle"].label = "სტატუსი"
        self.fields["lifecycle"].choices = PRODUCT_FORM_LIFECYCLE_CHOICES
        product_types = BusinessProductType.objects.none()
        tags = BusinessTag.objects.none()

        if business is not None:
            self.fields["price"].label = f"ფასი ({business.default_currency})"
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
        self.fields["product_type"].empty_label = "დადასტურებული ტიპი არ არის"
        self.fields["product_type"].label = "დადასტურებული პროდუქტის ტიპი"
        self.fields["tags"].queryset = tags

    def clean_description(self):
        description = self.cleaned_data["description"]
        derived_name = " ".join(description.split())
        name_max_length = Product._meta.get_field("name").max_length
        self.instance.name = derived_name[:name_max_length]
        return description


class ProductMediaForm(forms.Form):
    image = forms.ImageField(
        required=False,
        label="პროდუქტის სურათი",
        help_text="არასავალდებულო JPEG, PNG ან WebP სურათი, მაქსიმუმ 5 MiB.",
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp"}
        ),
    )

    def __init__(self, *args, existing_media=None, **kwargs):
        files = kwargs.get("files")
        submitted_images = (
            files.getlist("image")
            if files is not None and hasattr(files, "getlist")
            else []
        )
        self._multiple_uploads = len(submitted_images) > 1
        submitted_image = files.get("image") if files is not None else None
        self._declared_content_type = getattr(
            submitted_image,
            "content_type",
            None,
        )
        self.existing_media = existing_media
        super().__init__(*args, **kwargs)
        if existing_media is not None:
            self.fields["image"].label = "პროდუქტის სურათის შეცვლა"

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if self._multiple_uploads:
            raise ValidationError("აირჩიეთ მხოლოდ ერთი პროდუქტის სურათი.")
        if image is not None:
            validate_declared_product_media_type(
                image,
                self._declared_content_type,
            )
        return image


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
        self.fields["size"].empty_label = "აირჩიეთ ზომა"
        self.fields["color"].queryset = color_queryset
        self.fields["color"].empty_label = "აირჩიეთ ფერი"
        if self.instance.pk:
            self.fields["quantity"].disabled = True
            self.fields["quantity"].label = "მიმდინარე მარაგი"
            self.fields["quantity"].help_text = (
                "მარაგის შემდეგი ცვლილებისთვის გამოიყენეთ -1 და +1 ღილაკები."
            )
        else:
            self.fields["quantity"].label = "საწყისი მარაგი"
            self.fields["quantity"].help_text = (
                "ახალი არჩევანის მარაგი ახლავე მიუთითეთ. შემდეგი ცვლილებისთვის გამოიყენება -1 და +1."
            )
            self.fields["quantity"].widget.attrs.update(
                {"min": "0", "step": "1", "inputmode": "numeric"}
            )

    def has_changed(self):
        """Ignore untouched extra rows whose only values are model defaults."""
        if self.is_bound and not self.instance.pk:
            size = self.data.get(self.add_prefix("size"))
            color = self.data.get(self.add_prefix("color"))
            quantity = str(
                self.data.get(self.add_prefix("quantity")) or ""
            ).strip()
            if (
                not str(size or "").strip()
                and not str(color or "").strip()
                and quantity in ("", "0")
            ):
                return False
        return super().has_changed()


class ProductMaterialFactForm(forms.ModelForm):
    class Meta:
        model = ProductMaterialFact
        fields = ["canonical_material", "percentage", "original_text", "source"]
        labels = {
            "canonical_material": "მასალის მთავარი სახელი",
            "percentage": "პროცენტი",
            "original_text": "გამყიდველის საწყისი ფორმულირება",
            "source": "წყარო",
        }
        widgets = {
            "percentage": forms.NumberInput(attrs={"min": 1, "max": 100}),
        }

    def __init__(self, *args, business=None, **kwargs):
        self.business = business
        super().__init__(*args, **kwargs)
        self.fields["percentage"].widget.attrs.update({"min": 1, "max": 100})
        self.fields["source"].choices = (
            (ProductMaterialFact.Source.DESCRIPTION, "აღწერა"),
            (ProductMaterialFact.Source.MANUAL, "ხელით მითითებული"),
        )
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
                "მასალის მონაცემი აქტიურ ბიზნესს უნდა ეკუთვნოდეს."
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
            attrs={"placeholder": "არასავალდებულო: მძიმით გამოყოფილი ალტერნატიული სიტყვები"}
        ),
    )

    def __init__(self, *args, kind, **kwargs):
        labels = {
            SIZE_VOCABULARY: "ზომა",
            COLOR_VOCABULARY: "ფერი",
            PRODUCT_TYPE_VOCABULARY: "პროდუქტის ტიპი",
            TAG_VOCABULARY: "ჭდე",
        }
        if kind not in labels:
            raise ValueError("Unsupported vocabulary kind.")
        self.kind = kind
        super().__init__(*args, **kwargs)

        label = labels[kind]
        self.fields["name"].label = f"მთავარი მნიშვნელობა — {label}"
        self.fields["name"].max_length = 40 if kind == SIZE_VOCABULARY else 80
        self.fields["aliases"].label = "დამტკიცებული ალიასები"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError("მთავარი მნიშვნელობა სავალდებულოა.")
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
                    f"თითოეული ალიასი მაქსიმუმ {max_length} სიმბოლოს უნდა შეიცავდეს."
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
                "ალიასი მთავარი მნიშვნელობისგან უნდა განსხვავდებოდეს.",
            )
        return cleaned_data


class ChoiceVocabularyEditForm(ChoiceVocabularyForm):
    is_active = forms.BooleanField(
        required=False,
        label="ხელმისაწვდომია ახალი არჩევანისა და ამოცნობისთვის",
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
            "ხელმისაწვდომია ახალი არჩევანისა და ამოცნობისთვის"
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
            if not form.cleaned_data:
                continue
            if self._should_delete_form(form):
                if form.instance.pk:
                    form.add_error(
                        "DELETE",
                        (
                            "შენახული არჩევანი ვერ წაიშლება. "
                            "მის ნაცვლად გააუქმეთ არჩევანი."
                        ),
                    )
                continue
            if form.cleaned_data.get("is_active"):
                active_choices += 1

        if (
            self.instance.lifecycle == Product.Lifecycle.ACTIVE
            and active_choices == 0
        ):
            raise ValidationError(
                "აქტიურ პროდუქტს მინიმუმ ერთი აქტიური არჩევანი სჭირდება."
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
