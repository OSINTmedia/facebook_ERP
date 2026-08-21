"""Server-truth transfer of a transient material candidate into formset data."""

from dataclasses import dataclass
from urllib.parse import unquote

from django.core.exceptions import ValidationError
from django.http import QueryDict

from catalog.forms import ProductMaterialFactFormSet
from catalog.models import ProductMaterialFact
from catalog.recognition import (
    RecognitionCandidate,
    SemanticDestination,
    recognize_product_preview_for_business,
)


@dataclass(frozen=True)
class MaterialCandidateTransfer:
    """One validated, unsaved material candidate placed in an editable row."""

    data: QueryDict
    candidate: RecognitionCandidate
    row_index: int

    @property
    def feedback(self) -> str:
        return (
            f'Material "{self.candidate.canonical_value}" added to '
            f"Material {self.row_index + 1}. Review the fact before saving."
        )


def transfer_material_candidate(
    *,
    data,
    business,
    candidate_reference,
    material_prefix="materials",
) -> MaterialCandidateTransfer:
    """Return copied form data containing one current Business material candidate."""
    candidate = _current_material_candidate(
        data=data,
        business=business,
        candidate_reference=candidate_reference,
    )
    transferred_data = data.copy()
    total_forms = _validated_total_forms(transferred_data, material_prefix)
    row_index = _first_empty_row(
        transferred_data,
        prefix=material_prefix,
        total_forms=total_forms,
    )

    if row_index is None:
        if total_forms >= ProductMaterialFactFormSet.max_num:
            raise ValidationError("No additional material row can be added.")
        row_index = total_forms
        transferred_data[f"{material_prefix}-TOTAL_FORMS"] = str(total_forms + 1)
        transferred_data[f"{material_prefix}-{row_index}-percentage"] = ""

    transferred_data[f"{material_prefix}-{row_index}-canonical_material"] = (
        candidate.canonical_value
    )
    transferred_data[f"{material_prefix}-{row_index}-original_text"] = (
        candidate.observed_text
    )
    transferred_data[f"{material_prefix}-{row_index}-source"] = (
        ProductMaterialFact.Source.DESCRIPTION
    )
    return MaterialCandidateTransfer(
        data=transferred_data,
        candidate=candidate,
        row_index=row_index,
    )


def _current_material_candidate(*, data, business, candidate_reference):
    try:
        (
            index,
            destination,
            span_start,
            span_end,
            encoded_canonical_value,
        ) = str(candidate_reference).split(":", 4)
        candidate_index = int(index)
        expected_destination = SemanticDestination(destination)
        expected_span = (int(span_start), int(span_end))
        expected_canonical_value = unquote(encoded_canonical_value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("The selected candidate is invalid.") from exc

    preview = recognize_product_preview_for_business(
        data.get("description"),
        business,
    )
    if candidate_index < 0 or candidate_index >= len(preview.candidates):
        raise ValidationError(
            "That candidate is no longer available. "
            "Review the description and try again."
        )

    candidate = preview.candidates[candidate_index]
    if (
        candidate.destination != expected_destination
        or (candidate.span_start, candidate.span_end) != expected_span
        or candidate.canonical_value != expected_canonical_value
    ):
        raise ValidationError(
            "That candidate is no longer available. "
            "Review the description and try again."
        )
    if candidate.destination != SemanticDestination.MATERIAL:
        raise ValidationError("Only Material candidates can become material facts.")
    return candidate


def _validated_total_forms(data, prefix):
    try:
        total_forms = int(data[f"{prefix}-TOTAL_FORMS"])
        initial_forms = int(data[f"{prefix}-INITIAL_FORMS"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError(
            "Material form state is invalid. Refresh and try again."
        ) from exc

    if (
        total_forms < 0
        or initial_forms < 0
        or initial_forms > total_forms
        or total_forms > ProductMaterialFactFormSet.absolute_max
    ):
        raise ValidationError("Material form state is invalid. Refresh and try again.")
    return total_forms


def _first_empty_row(data, *, prefix, total_forms):
    for row_index in range(total_forms):
        if _is_checked(data.get(f"{prefix}-{row_index}-DELETE")):
            continue
        material = data.get(f"{prefix}-{row_index}-canonical_material", "")
        original_text = data.get(f"{prefix}-{row_index}-original_text", "")
        if not str(material).strip() and not str(original_text).strip():
            return row_index
    return None


def _is_checked(value):
    return str(value or "").casefold() in {"1", "true", "on", "yes"}
