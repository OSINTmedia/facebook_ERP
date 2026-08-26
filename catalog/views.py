from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from businesses.selectors import MultipleBusinessesUnsupported, resolve_active_business
from catalog.choice_transfers import transfer_choice_candidate
from catalog.forms import ChoiceVocabularyEditForm, ChoiceVocabularyForm
from catalog.material_transfers import transfer_material_candidate
from catalog.models import (
    BusinessColor,
    BusinessProductType,
    BusinessSize,
    BusinessTag,
    Product,
)
from catalog.product_bundles import ProductBundle
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
    ProductWorkspaceState,
    build_product_workspace_cards,
    product_workspace_products,
)


RECOGNITION_PREVIEW_INTENT = "preview_recognition"
ADD_SIZE_VOCABULARY_INTENT = "add_size_vocabulary"
ADD_COLOR_VOCABULARY_INTENT = "add_color_vocabulary"
ADD_PRODUCT_TYPE_VOCABULARY_INTENT = "add_product_type_vocabulary"
ADD_TAG_VOCABULARY_INTENT = "add_tag_vocabulary"
TRANSFER_CHOICE_CANDIDATE_INTENT = "transfer_choice_candidate"
TRANSFER_MATERIAL_CANDIDATE_INTENT = "transfer_material_candidate"
UPDATE_VOCABULARY_INTENT = "update_vocabulary"

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
    SIZE_VOCABULARY: "Size",
    COLOR_VOCABULARY: "Color",
    PRODUCT_TYPE_VOCABULARY: "Product type",
    TAG_VOCABULARY: "Tag",
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
        self.workspace_state = ProductWorkspaceState.from_query_params(request.GET)
        self.business_policy_blocked = False
        self.active_business = None

        try:
            self.active_business = resolve_active_business(request.user)
        except MultipleBusinessesUnsupported:
            self.business_policy_blocked = True
            context = self.get_context_data()
            return self.render_to_response(context, status=409)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.none()
        product_cards = ()

        if self.active_business is not None:
            products = product_workspace_products(business=self.active_business)
            product_cards = build_product_workspace_cards(
                business=self.active_business,
                products=products,
            )

        context.update(
            {
                "active_business": self.active_business,
                "business_policy_blocked": self.business_policy_blocked,
                "current_nav": "products",
                "product_cards": product_cards,
                "products": products,
                "workspace_return_url": self.workspace_state.return_url,
            }
        )
        return context


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
                vocabulary_error="Unknown vocabulary action. Refresh and try again.",
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
                    f'{VOCABULARY_LABELS[kind]} "{canonical.name}" saved.',
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
                        "Invalid vocabulary selection. Refresh and try again."
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
                        "Invalid vocabulary selection. Refresh and try again."
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
                    f'{VOCABULARY_LABELS[kind]} "{canonical.name}" updated.',
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
        context.setdefault("current_nav", "products")
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
                "title": "Product types",
                "description": (
                    "Use one canonical product category and keep alternative wording "
                    "as explicit aliases."
                ),
                "entries": context["product_type_entries"],
                "add_form": context["product_type_add_form"],
                "add_intent": ADD_PRODUCT_TYPE_VOCABULARY_INTENT,
                "add_summary": "Add canonical product type",
                "add_button": "Add product type",
                "save_button": "Save product type",
                "empty_message": "No canonical product types yet.",
                "warning": (
                    "Renaming updates the label on every Product that references it. "
                    "Deactivation keeps existing Product truth but removes this value "
                    "from new selection and recognition."
                ),
            },
            {
                "kind": TAG_VOCABULARY,
                "title": "Tags",
                "description": (
                    "Use tags for approved product features or groupings and keep "
                    "alternative wording as explicit aliases."
                ),
                "entries": context["tag_entries"],
                "add_form": context["tag_add_form"],
                "add_intent": ADD_TAG_VOCABULARY_INTENT,
                "add_summary": "Add canonical tag",
                "add_button": "Add tag",
                "save_button": "Save tag",
                "empty_message": "No canonical tags yet.",
                "warning": (
                    "Renaming updates the label on every Product that references it. "
                    "Deactivation keeps existing Product truth but removes this value "
                    "from new selection and recognition."
                ),
            },
            {
                "kind": SIZE_VOCABULARY,
                "title": "Sizes",
                "description": "Examples: M with aliases M-ზომა, M ზომა, or M size.",
                "entries": context["size_entries"],
                "add_form": context["size_add_form"],
                "add_intent": ADD_SIZE_VOCABULARY_INTENT,
                "add_summary": "Add canonical size",
                "add_button": "Add size",
                "save_button": "Save size",
                "empty_message": "No canonical sizes yet.",
                "warning": (
                    "Renaming updates this label on every choice that references it. "
                    "Deactivation keeps existing choices but removes this value from "
                    "new selection and recognition."
                ),
            },
            {
                "kind": COLOR_VOCABULARY,
                "title": "Colors",
                "description": (
                    "Prefer a seller-facing Georgian canonical label and keep English "
                    "or inconsistent wording as aliases."
                ),
                "entries": context["color_entries"],
                "add_form": context["color_add_form"],
                "add_intent": ADD_COLOR_VOCABULARY_INTENT,
                "add_summary": "Add canonical color",
                "add_button": "Add color",
                "save_button": "Save color",
                "empty_message": "No canonical colors yet.",
                "warning": (
                    "Renaming updates this label on every choice that references it. "
                    "Deactivation keeps existing choices but removes this value from "
                    "new selection and recognition."
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
        context.setdefault("current_nav", "products")
        context.setdefault("page_title", "Product")
        context.setdefault("return_url", get_safe_product_return_url(request))
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

        context.setdefault(
            "size_vocabulary_form",
            ChoiceVocabularyForm(kind=SIZE_VOCABULARY, prefix="size-vocabulary"),
        )
        context.setdefault(
            "color_vocabulary_form",
            ChoiceVocabularyForm(kind=COLOR_VOCABULARY, prefix="color-vocabulary"),
        )

        return self.base_context(
            request,
            form=bundle.product_form if bundle is not None else None,
            choice_formset=bundle.choice_formset if bundle is not None else None,
            material_formset=bundle.material_formset if bundle is not None else None,
            preview_requested=preview_requested,
            recognition_preview=recognition_preview,
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
                label = "Size" if kind == SIZE_VOCABULARY else "Color"
                vocabulary_feedback = f'{label} "{canonical.name}" saved.'
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
                page_title="Add product",
                submit_label="Create product",
            ),
        )

    def post(self, request, *args, **kwargs):
        self.resolve_business(request)
        if self.business_policy_blocked or self.active_business is None:
            return self.render_business_blocked(request)

        bundle = ProductBundle(
            business=self.active_business,
            data=request.POST,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title="Add product",
                submit_label="Create product",
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
                page_title="Add product",
                submit_label="Create product",
            )

        if self.is_choice_candidate_transfer_request(request):
            return self.handle_choice_candidate_transfer(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
            )

        if self.is_material_candidate_transfer_request(request):
            return self.handle_material_candidate_transfer(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
            )

        if bundle.is_valid():
            bundle.save(actor=request.user)
            messages.success(request, "Product created.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title="Add product",
                submit_label="Create product",
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
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
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
            instance=product,
        )
        if self.is_recognition_preview_request(request):
            context = self.bundle_context(
                request,
                bundle,
                preview_requested=True,
                show_form_errors=False,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
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
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            )

        if self.is_choice_candidate_transfer_request(request):
            return self.handle_choice_candidate_transfer(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            )

        if self.is_material_candidate_transfer_request(request):
            return self.handle_material_candidate_transfer(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            )

        if bundle.is_valid():
            bundle.save(actor=request.user)
            messages.success(request, "Product updated.")
            return redirect(get_safe_product_return_url(request))

        return render(
            request,
            self.template_name,
            self.bundle_context(
                request,
                bundle,
                page_title=f"Edit {product.name}",
                product=product,
                submit_label="Save changes",
            ),
        )
