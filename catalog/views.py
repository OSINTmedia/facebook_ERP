from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    SuspiciousFileOperation,
    ValidationError,
)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.add_similar import add_similar_product
from catalog.choice_transfers import append_choice_row, transfer_choice_candidate
from catalog.forms import (
    ChoiceVocabularyEditForm,
    ChoiceVocabularyForm,
    ProductWorkspaceSearchForm,
)
from catalog.lifecycle import archive_product, restore_product_to_draft
from catalog.material_transfers import transfer_material_candidate
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    BusinessTag,
    Product,
    ProductMedia,
)
from catalog.product_media import (
    product_media_content_type,
    product_media_storage_name_is_safe,
)
from catalog.product_bundles import ArchivedProductMutationError, ProductBundle
from catalog.readiness import CoverageCorrectionTarget
from catalog.ready_reply import build_product_ready_reply
from catalog.recognition import recognize_product_preview_for_business
from catalog.vocabulary import (
    COLOR_VOCABULARY,
    PRODUCT_TYPE_VOCABULARY,
    SIZE_VOCABULARY,
    TAG_VOCABULARY,
    create_choice_vocabulary_entry,
    update_choice_vocabulary_entry,
)
from catalog.workspace import (
    READINESS_CORRECTIONS,
    ProductWorkspaceState,
    build_product_workspace_context,
)


RECOGNITION_PREVIEW_INTENT = "preview_recognition"
ADD_SIZE_VOCABULARY_INTENT = "add_size_vocabulary"
ADD_COLOR_VOCABULARY_INTENT = "add_color_vocabulary"
ADD_PRODUCT_TYPE_VOCABULARY_INTENT = "add_product_type_vocabulary"
ADD_TAG_VOCABULARY_INTENT = "add_tag_vocabulary"
TRANSFER_CHOICE_CANDIDATE_INTENT = "transfer_choice_candidate"
TRANSFER_MATERIAL_CANDIDATE_INTENT = "transfer_material_candidate"
ADD_CHOICE_ROW_INTENT = "add_choice_row"
UPDATE_VOCABULARY_INTENT = "update_vocabulary"
READINESS_CORRECTION_TARGETS = frozenset(
    target.value for target in CoverageCorrectionTarget
)

ADD_VOCABULARY_INTENTS = {
    ADD_SIZE_VOCABULARY_INTENT: SIZE_VOCABULARY,
    ADD_COLOR_VOCABULARY_INTENT: COLOR_VOCABULARY,
    ADD_PRODUCT_TYPE_VOCABULARY_INTENT: PRODUCT_TYPE_VOCABULARY,
    ADD_TAG_VOCABULARY_INTENT: TAG_VOCABULARY,
}
VOCABULARY_MODELS = {
    SIZE_VOCABULARY: BusinessSize,
    COLOR_VOCABULARY: BusinessColor,
    PRODUCT_TYPE_VOCABULARY: BusinessProductType,
    TAG_VOCABULARY: BusinessTag,
}
VOCABULARY_LABELS = {
    SIZE_VOCABULARY: "ზომა",
    COLOR_VOCABULARY: "ფერი",
    PRODUCT_TYPE_VOCABULARY: "პროდუქტის ტიპი",
    TAG_VOCABULARY: "ჭდე",
}


def get_safe_product_return_url(request):
    candidate = request.POST.get("next") or request.GET.get("next")
    fallback = reverse("catalog:product_list")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return fallback


def get_canonical_product_workspace_return_url(request):
    fallback = reverse("catalog:product_list")
    source = request.POST if "next" in request.POST else request.GET
    candidates = source.getlist("next")
    if len(candidates) != 1:
        return fallback

    if candidates[0] == reverse("shell_home"):
        return candidates[0]

    try:
        return ProductWorkspaceState.from_return_url(candidates[0]).return_url
    except ValueError:
        return fallback


def add_validation_errors_to_form(form, error):
    if hasattr(error, "message_dict"):
        for field_name, messages_for_field in error.message_dict.items():
            target = field_name if field_name in form.fields else None
            if field_name == NON_FIELD_ERRORS:
                target = None
            for message in messages_for_field:
                form.add_error(target, message)
        return

    for message in error.messages:
        form.add_error(None, message)


class ProductListView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/product_list.html"

    def get(self, request, *args, **kwargs):
        self.search_form = ProductWorkspaceSearchForm(request.GET)
        self.workspace_state = ProductWorkspaceState.from_search_form(
            self.search_form
        )
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True
            context = self.get_context_data()
            return self.render_to_response(context, status=409)

        context = self.get_context_data()
        if (
            self.workspace_state.is_valid
            and context["workspace_page_recovered"]
        ):
            return redirect(context["workspace_return_url"])
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_business": self.active_business,
                "business_policy_blocked": self.business_policy_blocked,
                "current_nav": "products",
                "search_form": self.search_form,
            }
        )
        context.update(
            build_product_workspace_context(
                state=self.workspace_state,
                business=self.active_business,
            )
        )
        return context


class ReadyReplyView(LoginRequiredMixin, View):
    template_name = "catalog/_ready_reply_panel.html"

    def get(self, request, *args, **kwargs):
        try:
            business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported as exc:
            raise Http404("Product not found.") from exc
        if business is None:
            raise Http404("Product not found.")

        product = get_object_or_404(
            Product,
            pk=kwargs["pk"],
            business=business,
            lifecycle__in=(Product.Lifecycle.DRAFT, Product.Lifecycle.ACTIVE),
        )
        ready_reply = build_product_ready_reply(
            business=business,
            product=product,
        )
        return_url = get_canonical_product_workspace_return_url(request)
        seller_notes = []
        for note in ready_reply.seller_notes:
            correction_url = ""
            if note.correction_target is not None:
                _label, fragment = READINESS_CORRECTIONS[
                    note.correction_target
                ]
                correction_url = (
                    reverse("catalog:product_edit", kwargs={"pk": product.pk})
                    + "?"
                    + urlencode(
                        {
                            "focus": note.correction_target.value,
                            "next": return_url,
                        }
                    )
                    + fragment
                )
            seller_notes.append(
                {
                    "text": note.text,
                    "correction_url": correction_url,
                }
            )

        response = render(
            request,
            self.template_name,
            {
                "product": product,
                "ready_reply": ready_reply,
                "ready_reply_seller_notes": seller_notes,
            },
        )
        response["Cache-Control"] = "private, no-store"
        return response


class ProductMediaView(LoginRequiredMixin, View):
    """Serve one Product image only inside its owner's active Business."""

    def get(self, request, *args, **kwargs):
        try:
            business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported as exc:
            raise Http404("Product image not found.") from exc
        if business is None:
            raise Http404("Product image not found.")

        media = get_object_or_404(
            ProductMedia.objects.select_related("product"),
            pk=kwargs["pk"],
            business=business,
            product__business=business,
        )
        if not product_media_storage_name_is_safe(
            media.image.name,
            business_id=business.pk,
            product_id=media.product_id,
        ):
            raise Http404("Product image not found.")

        content_type = product_media_content_type(media.image.name)
        if content_type is None:
            raise Http404("Product image not found.")
        try:
            image_file = media.image.open("rb")
        except (FileNotFoundError, OSError, SuspiciousFileOperation) as exc:
            raise Http404("Product image not found.") from exc

        extension = media.image.name.rsplit(".", 1)[-1]
        response = FileResponse(
            image_file,
            content_type=content_type,
            filename=f"product-{media.product_id}.{extension}",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class ChoiceVocabularyView(LoginRequiredMixin, View):
    template_name = "catalog/choice_vocabulary.html"

    def resolve_business(self, request):
        self.business_policy_blocked = False
        self.active_business = None
        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True

    def get(self, request, *args, **kwargs):
        self.resolve_business(request)
        status = 409 if self.business_policy_blocked else 200
        return render(request, self.template_name, self.get_context(request), status=status)

    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return render(
                request,
                self.template_name,
                self.get_context(request),
                status=409,
            )

        intent = request.POST.get("intent", "")
        if intent in ADD_VOCABULARY_INTENTS:
            return self.handle_add(request, intent)
        if intent.startswith(f"{UPDATE_VOCABULARY_INTENT}:"):
            return self.handle_update(request, intent)

        return render(
            request,
            self.template_name,
            self.get_context(
                request,
                vocabulary_error="სიტყვარის უცნობი მოქმედებაა. განაახლეთ და სცადეთ ხელახლა.",
            ),
            status=400,
        )

    def handle_add(self, request, intent):
        kind = ADD_VOCABULARY_INTENTS[intent]
        form = ChoiceVocabularyForm(
            request.POST,
            kind=kind,
            prefix=f"add-{kind}",
        )
        if form.is_valid():
            try:
                canonical = create_choice_vocabulary_entry(
                    business=self.active_business,
                    kind=kind,
                    name=form.cleaned_data["name"],
                    aliases=form.cleaned_data["aliases"],
                )
            except ValidationError as error:
                add_validation_errors_to_form(form, error)
            else:
                messages.success(
                    request,
                    f'{VOCABULARY_LABELS[kind]} „{canonical.name}“ შენახულია.',
                )
                return redirect(request.get_full_path())

        context_key = f"{kind}_add_form"
        return render(
            request,
            self.template_name,
            self.get_context(request, **{context_key: form}),
        )

    def handle_update(self, request, intent):
        try:
            _, kind, raw_entry_id = intent.split(":")
            entry_id = int(raw_entry_id)
        except (TypeError, ValueError):
            return render(
                request,
                self.template_name,
                self.get_context(
                    request,
                    vocabulary_error=(
                        "სიტყვარის არასწორი არჩევანია. განაახლეთ და სცადეთ ხელახლა."
                    ),
                ),
                status=400,
            )

        model = VOCABULARY_MODELS.get(kind)
        if model is None:
            return render(
                request,
                self.template_name,
                self.get_context(
                    request,
                    vocabulary_error=(
                        "სიტყვარის არასწორი არჩევანია. განაახლეთ და სცადეთ ხელახლა."
                    ),
                ),
                status=400,
            )

        entry = get_object_or_404(
            model.objects.prefetch_related("aliases"),
            business=self.active_business,
            pk=entry_id,
        )
        form = ChoiceVocabularyEditForm(
            request.POST,
            kind=kind,
            instance=entry,
            prefix=f"edit-{kind}-{entry.pk}",
        )
        if form.is_valid():
            try:
                canonical = update_choice_vocabulary_entry(
                    business=self.active_business,
                    kind=kind,
                    entry_id=entry.pk,
                    name=form.cleaned_data["name"],
                    aliases=form.cleaned_data["aliases"],
                    is_active=form.cleaned_data["is_active"],
                )
            except ValidationError as error:
                add_validation_errors_to_form(form, error)
            else:
                messages.success(
                    request,
                    f'{VOCABULARY_LABELS[kind]} „{canonical.name}“ განახლებულია.',
                )
                return redirect(request.get_full_path())

        return render(
            request,
            self.template_name,
            self.get_context(
                request,
                bound_edit_kind=kind,
                bound_edit_form=form,
                bound_edit_entry_id=entry.pk,
            ),
        )

    def get_context(self, request, **context):
        context.setdefault("active_business", self.active_business)
        context.setdefault("business_policy_blocked", self.business_policy_blocked)
        context.setdefault("current_nav", "vocabulary")
        context.setdefault("return_url", get_safe_product_return_url(request))
        context.setdefault(
            "size_add_form",
            ChoiceVocabularyForm(kind=SIZE_VOCABULARY, prefix="add-size"),
        )
        context.setdefault(
            "color_add_form",
            ChoiceVocabularyForm(kind=COLOR_VOCABULARY, prefix="add-color"),
        )
        context.setdefault(
            "product_type_add_form",
            ChoiceVocabularyForm(
                kind=PRODUCT_TYPE_VOCABULARY,
                prefix="add-product_type",
            ),
        )
        context.setdefault(
            "tag_add_form",
            ChoiceVocabularyForm(kind=TAG_VOCABULARY, prefix="add-tag"),
        )

        size_entries = BusinessSize.objects.none()
        color_entries = BusinessColor.objects.none()
        product_type_entries = BusinessProductType.objects.none()
        tag_entries = BusinessTag.objects.none()
        if self.active_business is not None:
            size_entries = BusinessSize.objects.filter(
                business=self.active_business
            ).prefetch_related("aliases")
            color_entries = BusinessColor.objects.filter(
                business=self.active_business
            ).prefetch_related("aliases")
            product_type_entries = BusinessProductType.objects.filter(
                business=self.active_business
            ).prefetch_related("aliases")
            tag_entries = BusinessTag.objects.filter(
                business=self.active_business
            ).prefetch_related("aliases")

        context["size_entries"] = self.build_entry_rows(
            size_entries,
            kind=SIZE_VOCABULARY,
            bound_kind=context.get("bound_edit_kind"),
            bound_entry_id=context.get("bound_edit_entry_id"),
            bound_form=context.get("bound_edit_form"),
        )
        context["color_entries"] = self.build_entry_rows(
            color_entries,
            kind=COLOR_VOCABULARY,
            bound_kind=context.get("bound_edit_kind"),
            bound_entry_id=context.get("bound_edit_entry_id"),
            bound_form=context.get("bound_edit_form"),
        )
        context["product_type_entries"] = self.build_entry_rows(
            product_type_entries,
            kind=PRODUCT_TYPE_VOCABULARY,
            bound_kind=context.get("bound_edit_kind"),
            bound_entry_id=context.get("bound_edit_entry_id"),
            bound_form=context.get("bound_edit_form"),
        )
        context["tag_entries"] = self.build_entry_rows(
            tag_entries,
            kind=TAG_VOCABULARY,
            bound_kind=context.get("bound_edit_kind"),
            bound_entry_id=context.get("bound_edit_entry_id"),
            bound_form=context.get("bound_edit_form"),
        )
        context["vocabulary_groups"] = (
            {
                "kind": PRODUCT_TYPE_VOCABULARY,
                "title": "პროდუქტის ტიპები",
                "description": (
                    "აირჩიეთ ერთი მთავარი პროდუქტის კატეგორია და ალტერნატიული "
                    "სიტყვები ცალკე ალიასებად შეინახეთ."
                ),
                "entries": context["product_type_entries"],
                "add_form": context["product_type_add_form"],
                "add_intent": ADD_PRODUCT_TYPE_VOCABULARY_INTENT,
                "add_summary": "პროდუქტის მთავარი ტიპის დამატება",
                "add_button": "პროდუქტის ტიპის დამატება",
                "save_button": "პროდუქტის ტიპის შენახვა",
                "empty_message": "პროდუქტის მთავარი ტიპი ჯერ არ არის.",
                "warning": (
                    "სახელის შეცვლა განაახლებს ყველა პროდუქტს, რომელიც მას იყენებს. "
                    "გაუქმება არსებულ მონაცემს შეინახავს, ახალი არჩევანიდან და ამოცნობიდან კი ამ მნიშვნელობას ამოიღებს."
                ),
            },
            {
                "kind": TAG_VOCABULARY,
                "title": "ჭდეები",
                "description": (
                    "ჭდეები გამოიყენეთ დამტკიცებული თვისებებისა ან ჯგუფებისთვის; "
                    "ალტერნატიული სიტყვები ალიასებად შეინახეთ."
                ),
                "entries": context["tag_entries"],
                "add_form": context["tag_add_form"],
                "add_intent": ADD_TAG_VOCABULARY_INTENT,
                "add_summary": "მთავარი ჭდის დამატება",
                "add_button": "ჭდის დამატება",
                "save_button": "ჭდის შენახვა",
                "empty_message": "მთავარი ჭდე ჯერ არ არის.",
                "warning": (
                    "სახელის შეცვლა განაახლებს ყველა პროდუქტს, რომელიც მას იყენებს. "
                    "გაუქმება არსებულ მონაცემს შეინახავს, ახალი არჩევანიდან და ამოცნობიდან კი ამ მნიშვნელობას ამოიღებს."
                ),
            },
            {
                "kind": SIZE_VOCABULARY,
                "title": "ზომები",
                "description": "მაგალითად: M, ხოლო ალიასებად — M-ზომა, M ზომა ან M size.",
                "entries": context["size_entries"],
                "add_form": context["size_add_form"],
                "add_intent": ADD_SIZE_VOCABULARY_INTENT,
                "add_summary": "მთავარი ზომის დამატება",
                "add_button": "ზომის დამატება",
                "save_button": "ზომის შენახვა",
                "empty_message": "მთავარი ზომა ჯერ არ არის.",
                "warning": (
                    "სახელის შეცვლა განაახლებს ყველა არჩევანს, რომელიც მას იყენებს. "
                    "გაუქმება არსებულ არჩევანს შეინახავს, ახალი არჩევანიდან და ამოცნობიდან კი ამ მნიშვნელობას ამოიღებს."
                ),
            },
            {
                "kind": COLOR_VOCABULARY,
                "title": "ფერები",
                "description": (
                    "მთავარ სახელად ქართული ფორმა აირჩიეთ, ინგლისური ან "
                    "არათანმიმდევრული ფორმები კი ალიასებად შეინახეთ."
                ),
                "entries": context["color_entries"],
                "add_form": context["color_add_form"],
                "add_intent": ADD_COLOR_VOCABULARY_INTENT,
                "add_summary": "მთავარი ფერის დამატება",
                "add_button": "ფერის დამატება",
                "save_button": "ფერის შენახვა",
                "empty_message": "მთავარი ფერი ჯერ არ არის.",
                "warning": (
                    "სახელის შეცვლა განაახლებს ყველა არჩევანს, რომელიც მას იყენებს. "
                    "გაუქმება არსებულ არჩევანს შეინახავს, ახალი არჩევანიდან და ამოცნობიდან კი ამ მნიშვნელობას ამოიღებს."
                ),
            },
        )
        return context

    @staticmethod
    def build_entry_rows(
        entries,
        *,
        kind,
        bound_kind=None,
        bound_entry_id=None,
        bound_form=None,
    ):
        rows = []
        for entry in entries:
            form = ChoiceVocabularyEditForm(
                kind=kind,
                instance=entry,
                prefix=f"edit-{kind}-{entry.pk}",
            )
            if kind == bound_kind and entry.pk == bound_entry_id:
                form = bound_form
            rows.append(
                {
                    "entry": entry,
                    "aliases": tuple(entry.aliases.all()),
                    "form": form,
                }
            )
        return rows


class ProductMutationBusinessMixin(LoginRequiredMixin):
    template_name = "catalog/product_form.html"

    def resolve_business(self, request):
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True

    def base_context(self, request, **context):
        context.setdefault("active_business", self.active_business)
        context.setdefault("business_policy_blocked", self.business_policy_blocked)
        context.setdefault("current_nav", "product_edit")
        context.setdefault("page_title", "პროდუქტი")
        return_url = get_canonical_product_workspace_return_url(request)
        context.setdefault("return_url", return_url)
        context.setdefault(
            "return_label",
            "მიმოხილვაზე დაბრუნება"
            if return_url == reverse("shell_home")
            else "პროდუქტებზე დაბრუნება",
        )
        correction_target = request.GET.get("focus", "")
        if correction_target not in READINESS_CORRECTION_TARGETS:
            correction_target = ""
        context.setdefault("correction_target", correction_target)
        return context

    def render_business_blocked(self, request):
        return render(
            request,
            self.template_name,
            self.base_context(request),
            status=409,
        )

    def bundle_context(
        self,
        request,
        bundle,
        *,
        preview_requested=False,
        show_form_errors=True,
        **context,
    ):
        recognition_preview = None
        if bundle is not None and self.active_business is not None:
            description = bundle.product_form["description"].value()
            recognition_preview = recognize_product_preview_for_business(
                description,
                self.active_business,
            )

        correction_target = request.GET.get("focus", "")
        choice_section_open = correction_target == CoverageCorrectionTarget.CHOICES
        choice_section_open = choice_section_open or any(
            context.get(key)
            for key in (
                "choice_transfer_feedback",
                "choice_transfer_error",
                "choice_row_feedback",
                "choice_row_error",
                "vocabulary_feedback",
            )
        )
        material_section_open = (
            correction_target == CoverageCorrectionTarget.MATERIALS
        )
        material_section_open = material_section_open or any(
            context.get(key)
            for key in (
                "material_transfer_feedback",
                "material_transfer_error",
            )
        )
        if bundle is not None and show_form_errors:
            choice_section_open = choice_section_open or bool(
                bundle.choice_formset.non_form_errors()
            ) or any(bool(form.errors) for form in bundle.choice_formset.forms)
            material_section_open = material_section_open or bool(
                bundle.material_formset.non_form_errors()
            ) or any(bool(form.errors) for form in bundle.material_formset.forms)

        context.setdefault(
            "size_vocabulary_form",
            ChoiceVocabularyForm(kind=SIZE_VOCABULARY, prefix="size-vocabulary"),
        )
        context.setdefault(
            "color_vocabulary_form",
            ChoiceVocabularyForm(kind=COLOR_VOCABULARY, prefix="color-vocabulary"),
        )
        choice_section_open = choice_section_open or bool(
            context["size_vocabulary_form"].errors
            or context["color_vocabulary_form"].errors
        )

        return self.base_context(
            request,
            form=bundle.product_form if bundle is not None else None,
            media_form=bundle.media_form if bundle is not None else None,
            current_media=bundle.current_media if bundle is not None else None,
            media_reselection_required=(
                bool(bundle and bundle.media_upload_was_submitted)
                and (show_form_errors or not request.htmx)
            ),
            choice_formset=bundle.choice_formset if bundle is not None else None,
            material_formset=bundle.material_formset if bundle is not None else None,
            preview_requested=preview_requested,
            recognition_preview=recognition_preview,
            choice_section_open=choice_section_open,
            material_section_open=material_section_open,
            show_form_errors=show_form_errors,
            **context,
        )

    def is_recognition_preview_request(self, request):
        return request.POST.get("intent") == RECOGNITION_PREVIEW_INTENT

    def is_vocabulary_request(self, request):
        return request.POST.get("intent") in {
            ADD_SIZE_VOCABULARY_INTENT,
            ADD_COLOR_VOCABULARY_INTENT,
        }

    def is_choice_candidate_transfer_request(self, request):
        intent = request.POST.get("intent", "")
        return intent.startswith(f"{TRANSFER_CHOICE_CANDIDATE_INTENT}:")

    def is_material_candidate_transfer_request(self, request):
        intent = request.POST.get("intent", "")
        return intent.startswith(f"{TRANSFER_MATERIAL_CANDIDATE_INTENT}:")

    def is_add_choice_row_request(self, request):
        return request.POST.get("intent") == ADD_CHOICE_ROW_INTENT

    def handle_add_choice_row(self, request, bundle, **context):
        choice_row_feedback = None
        choice_row_error = None
        try:
            appended_data = append_choice_row(data=request.POST)
        except ValidationError as error:
            choice_row_error = " ".join(error.messages)
        else:
            bundle = ProductBundle(
                business=self.active_business,
                data=appended_data,
                files=request.FILES,
                instance=bundle.product,
            )
            choice_row_feedback = "კიდევ ერთი ცარიელი არჩევანი მზადაა."

        return render(
            request,
            (
                "catalog/_choice_section.html"
                if request.htmx
                else self.template_name
            ),
            self.bundle_context(
                request,
                bundle,
                show_form_errors=False,
                choice_row_feedback=choice_row_feedback,
                choice_row_error=choice_row_error,
                **context,
            ),
        )

    def handle_choice_candidate_transfer(self, request, bundle, **context):
        intent = request.POST.get("intent", "")
        candidate_reference = intent.removeprefix(
            f"{TRANSFER_CHOICE_CANDIDATE_INTENT}:"
        )
        transfer_feedback = None
        transfer_error = None

        try:
            transfer = transfer_choice_candidate(
                data=request.POST,
                business=self.active_business,
                candidate_reference=candidate_reference,
            )
        except ValidationError as error:
            transfer_error = " ".join(error.messages)
        else:
            bundle = ProductBundle(
                business=self.active_business,
                data=transfer.data,
                files=request.FILES,
                instance=bundle.product,
            )
            transfer_feedback = transfer.feedback

        bundle.is_valid()
        rendered_context = self.bundle_context(
            request,
            bundle,
            choice_transfer_feedback=transfer_feedback,
            choice_transfer_error=transfer_error,
            **context,
        )
        return render(
            request,
            (
                "catalog/_choice_section.html"
                if request.htmx
                else self.template_name
            ),
            rendered_context,
        )

    def handle_material_candidate_transfer(self, request, bundle, **context):
        intent = request.POST.get("intent", "")
        candidate_reference = intent.removeprefix(
            f"{TRANSFER_MATERIAL_CANDIDATE_INTENT}:"
        )
        transfer_feedback = None
        transfer_error = None

        try:
            transfer = transfer_material_candidate(
                data=request.POST,
                business=self.active_business,
                candidate_reference=candidate_reference,
            )
        except ValidationError as error:
            transfer_error = " ".join(error.messages)
        else:
            bundle = ProductBundle(
                business=self.active_business,
                data=transfer.data,
                files=request.FILES,
                instance=bundle.product,
            )
            transfer_feedback = transfer.feedback

        bundle.is_valid()
        rendered_context = self.bundle_context(
            request,
            bundle,
            material_transfer_feedback=transfer_feedback,
            material_transfer_error=transfer_error,
            **context,
        )
        return render(
            request,
            (
                "catalog/_material_section.html"
                if request.htmx
                else self.template_name
            ),
            rendered_context,
        )

    def handle_vocabulary_request(self, request, bundle, **context):
        intent = request.POST.get("intent")
        kind = (
            SIZE_VOCABULARY
            if intent == ADD_SIZE_VOCABULARY_INTENT
            else COLOR_VOCABULARY
        )
        size_form = ChoiceVocabularyForm(
            kind=SIZE_VOCABULARY,
            prefix="size-vocabulary",
        )
        color_form = ChoiceVocabularyForm(
            kind=COLOR_VOCABULARY,
            prefix="color-vocabulary",
        )
        vocabulary_form = ChoiceVocabularyForm(
            request.POST,
            kind=kind,
            prefix=f"{kind}-vocabulary",
        )
        if kind == SIZE_VOCABULARY:
            size_form = vocabulary_form
        else:
            color_form = vocabulary_form

        vocabulary_feedback = None
        if vocabulary_form.is_valid():
            try:
                canonical = create_choice_vocabulary_entry(
                    business=self.active_business,
                    kind=kind,
                    name=vocabulary_form.cleaned_data["name"],
                    aliases=vocabulary_form.cleaned_data["aliases"],
                )
            except ValidationError as error:
                add_validation_errors_to_form(vocabulary_form, error)
            else:
                label = "ზომა" if kind == SIZE_VOCABULARY else "ფერი"
                vocabulary_feedback = f'{label} „{canonical.name}“ შენახულია.'
                if kind == SIZE_VOCABULARY:
                    size_form = ChoiceVocabularyForm(
                        kind=SIZE_VOCABULARY,
                        prefix="size-vocabulary",
                    )
                else:
                    color_form = ChoiceVocabularyForm(
                        kind=COLOR_VOCABULARY,
                        prefix="color-vocabulary",
                    )
                bundle = ProductBundle(
                    business=self.active_business,
                    data=request.POST,
                    files=request.FILES,
                    instance=bundle.product,
                )

        rendered_context = self.bundle_context(
            request,
            bundle,
            show_form_errors=False,
            size_vocabulary_form=size_form,
            color_vocabulary_form=color_form,
            vocabulary_feedback=vocabulary_feedback,
            **context,
        )
        return render(
            request,
            (
                "catalog/_choice_section.html"
                if request.htmx
                else self.template_name
            ),
            rendered_context,
        )

class ProductCreateView(ProductMutationBusinessMixin, View):
    def base_context(self, request, **context):
        context.setdefault("current_nav", "product_create")
        return super().base_context(request, **context)

    def get(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        bundle = None
        if self.active_business is not None:
            bundle = ProductBundle(business=self.active_business)

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return self.render_business_blocked(request)

        bundle = ProductBundle(
            business=self.active_business,
            data=request.POST,
            files=request.FILES,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            )
            return render(
                request,
                (
                    "catalog/_recognition_preview.html"
                    if request.htmx
                    else self.template_name
                ),
                context,
            )

        if self.is_vocabulary_request(request):
            return self.handle_vocabulary_request(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            )

        if self.is_choice_candidate_transfer_request(request):
            return self.handle_choice_candidate_transfer(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            )

        if self.is_add_choice_row_request(request):
            return self.handle_add_choice_row(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            )

        if self.is_material_candidate_transfer_request(request):
            return self.handle_material_candidate_transfer(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            )

        if bundle.is_valid():
            bundle.save(actor=request.user)
            messages.success(request, "პროდუქტი შექმნილია.")
            return redirect(get_canonical_product_workspace_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title="პროდუქტის დამატება",
                submit_label="პროდუქტის შექმნა",
            ),
        )


class ProductUpdateView(ProductMutationBusinessMixin, View):
    def get_product(self):
        if self.active_business is None:
            raise Http404("Product not found.")

        try:
            return Product.objects.get(
                business=self.active_business,
                pk=self.kwargs["pk"],
                lifecycle__in=(Product.Lifecycle.DRAFT, Product.Lifecycle.ACTIVE),
            )
        except Product.DoesNotExist as exc:
            raise Http404("Product not found.") from exc

    def get(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        product = self.get_product()
        bundle = ProductBundle(
            business=self.active_business,
            instance=product,
        )
        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            ),
        )
    def post(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.resolve_business(request)
        if self.business_policy_blocked:
            return self.render_business_blocked(request)

        product = self.get_product()
        bundle = ProductBundle(
            business=self.active_business,
            data=request.POST,
            files=request.FILES,
            instance=product,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            )
            return render(
                request,
                (
                    "catalog/_recognition_preview.html"
                    if request.htmx
                    else self.template_name
                ),
                context,
            )

        if self.is_vocabulary_request(request):
            return self.handle_vocabulary_request(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            )

        if self.is_choice_candidate_transfer_request(request):
            return self.handle_choice_candidate_transfer(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            )

        if self.is_add_choice_row_request(request):
            return self.handle_add_choice_row(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            )

        if self.is_material_candidate_transfer_request(request):
            return self.handle_material_candidate_transfer(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            )

        if bundle.is_valid():
            try:
                bundle.save(actor=request.user)
            except ArchivedProductMutationError as error:
                messages.error(request, error.messages[0])
                return redirect(get_canonical_product_workspace_return_url(request))
            messages.success(request, "პროდუქტი განახლებულია.")
            return redirect(get_canonical_product_workspace_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title=f"{product.name} — რედაქტირება",
                product=product,
                submit_label="ცვლილებების შენახვა",
            ),
        )


class ProductAddSimilarView(ProductMutationBusinessMixin, View):
    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return self.render_business_blocked(request)

        try:
            product = add_similar_product(
                business=self.active_business,
                source_product_id=kwargs["pk"],
            )
        except Product.DoesNotExist as error:
            raise Http404("Product not found.") from error

        return_url = get_canonical_product_workspace_return_url(request)
        messages.success(
            request,
            "მსგავსი პროდუქტი მონახაზად შეიქმნა. გაადამოწმეთ გააქტიურებამდე.",
        )
        edit_url = reverse("catalog:product_edit", args=[product.pk])
        return redirect(f"{edit_url}?{urlencode({'next': return_url})}")


class ProductLifecycleMutationView(LoginRequiredMixin, View):
    command = None
    success_message = ""

    def post(self, request, *args, **kwargs):
        try:
            business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported as error:
            raise Http404("Product not found.") from error
        if business is None:
            raise Http404("Product not found.")

        return_url = get_canonical_product_workspace_return_url(request)
        try:
            self.command(
                business=business,
                product_id=kwargs["pk"],
            )
        except Product.DoesNotExist as error:
            raise Http404("Product not found.") from error
        except ValidationError as error:
            messages.error(request, error.messages[0])
            return redirect(return_url)

        messages.success(request, self.success_message)
        return redirect(return_url)


class ProductArchiveView(ProductLifecycleMutationView):
    command = staticmethod(archive_product)
    success_message = "პროდუქტი დაარქივებულია. მისი ისტორია და მარაგი შენახულია."


class ProductRestoreView(ProductLifecycleMutationView):
    command = staticmethod(restore_product_to_draft)
    success_message = "პროდუქტი გადასახედად მონახაზის სტატუსით აღდგა."
