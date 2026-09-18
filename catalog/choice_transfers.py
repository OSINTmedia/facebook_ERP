"""Server-truth transfer of transient Size/Color candidates into formset data."""

from dataclasses import dataclass
from urllib.parse import unquote

from django.core.exceptions import ValidationError
from django.http import QueryDict

from catalog.forms import ProductChoiceFormSet
from catalog.models import BusinessColor, BusinessSize
from catalog.recognition import (
    RecognitionCandidate,
    SemanticDestination,
    recognize_product_preview_for_business,
)


@dataclass(frozen=True)
class ChoiceCandidateTransfer:
    """One validated, unsaved candidate transfer into an editable choice row."""

    data: QueryDict
    candidate: RecognitionCandidate
    row_index: int
    label: str
    already_present: bool = False

    @property
    def feedback(self) -> str:
        if self.already_present:
            return (
                f'{self.label} „{self.candidate.canonical_value}“ უკვე არის '
                f'არჩევანში {self.row_index + 1}. გამოიყენეთ „კიდევ ერთი '
                "არჩევანის დამატება“, თუ იმავე მნიშვნელობით ცალკე არჩევანი გსურთ."
            )
        return (
            f'{self.label} „{self.candidate.canonical_value}“ დაემატა '
            f"არჩევანს {self.row_index + 1}. შენახვამდე გადაამოწმეთ რიგი."
        )


def transfer_choice_candidate(
    *,
    data,
    business,
    candidate_reference,
    choice_prefix="choices",
) -> ChoiceCandidateTransfer:
    """Return copied form data with one current Business candidate transferred."""
    candidate = _current_choice_candidate(
        data=data,
        business=business,
        candidate_reference=candidate_reference,
    )
    field_name, canonical, label = _canonical_choice_value(
        business=business,
        candidate=candidate,
    )
    transferred_data = data.copy()
    total_forms = _validated_total_forms(transferred_data, choice_prefix)
    existing_row_index = _first_matching_row(
        transferred_data,
        prefix=choice_prefix,
        total_forms=total_forms,
        field_name=field_name,
        canonical_id=canonical.pk,
    )
    if existing_row_index is not None:
        return ChoiceCandidateTransfer(
            data=transferred_data,
            candidate=candidate,
            row_index=existing_row_index,
            label=label,
            already_present=True,
        )

    row_index = _first_available_row(
        transferred_data,
        prefix=choice_prefix,
        total_forms=total_forms,
        field_name=field_name,
    )

    if row_index is None:
        if total_forms >= ProductChoiceFormSet.max_num:
            raise ValidationError("არჩევანის დამატებითი რიგი ვეღარ დაემატება.")
        row_index = total_forms
        transferred_data[f"{choice_prefix}-TOTAL_FORMS"] = str(total_forms + 1)
        transferred_data[f"{choice_prefix}-{row_index}-size"] = ""
        transferred_data[f"{choice_prefix}-{row_index}-color"] = ""
        transferred_data[f"{choice_prefix}-{row_index}-quantity"] = "0"
        transferred_data[f"{choice_prefix}-{row_index}-is_active"] = "on"

    transferred_data[f"{choice_prefix}-{row_index}-{field_name}"] = str(
        canonical.pk
    )
    return ChoiceCandidateTransfer(
        data=transferred_data,
        candidate=candidate,
        row_index=row_index,
        label=label,
    )


def append_choice_row(*, data, choice_prefix="choices") -> QueryDict:
    """Return copied form data with one deliberate empty choice row appended."""
    appended_data = data.copy()
    total_forms = _validated_total_forms(appended_data, choice_prefix)
    if total_forms >= ProductChoiceFormSet.max_num:
        raise ValidationError("არჩევანის დამატებითი რიგი ვეღარ დაემატება.")

    appended_data[f"{choice_prefix}-TOTAL_FORMS"] = str(total_forms + 1)
    appended_data[f"{choice_prefix}-{total_forms}-size"] = ""
    appended_data[f"{choice_prefix}-{total_forms}-color"] = ""
    appended_data[f"{choice_prefix}-{total_forms}-quantity"] = "0"
    appended_data[f"{choice_prefix}-{total_forms}-is_active"] = "on"
    return appended_data


def _current_choice_candidate(*, data, business, candidate_reference):
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
        raise ValidationError("არჩეული შეთავაზება არასწორია.") from exc

    preview = recognize_product_preview_for_business(
        data.get("description"),
        business,
    )
    if candidate_index < 0 or candidate_index >= len(preview.candidates):
        raise ValidationError(
            "ეს შეთავაზება აღარ არის ხელმისაწვდომი. "
            "გადაამოწმეთ აღწერა და სცადეთ ხელახლა."
        )

    candidate = preview.candidates[candidate_index]
    if (
        candidate.destination != expected_destination
        or (candidate.span_start, candidate.span_end) != expected_span
        or candidate.canonical_value != expected_canonical_value
    ):
        raise ValidationError(
            "ეს შეთავაზება აღარ არის ხელმისაწვდომი. "
            "გადაამოწმეთ აღწერა და სცადეთ ხელახლა."
        )
    if candidate.destination not in {
        SemanticDestination.CHOICE_SIZE,
        SemanticDestination.CHOICE_COLOR,
    }:
        raise ValidationError(
            "არჩევანში მხოლოდ ზომისა და ფერის შეთავაზებების გამოყენება შეიძლება."
        )
    return candidate


def _canonical_choice_value(*, business, candidate):
    if candidate.destination == SemanticDestination.CHOICE_SIZE:
        model = BusinessSize
        field_name = "size"
        label = "ზომა"
    else:
        model = BusinessColor
        field_name = "color"
        label = "ფერი"

    try:
        canonical = model.objects.get(
            business=business,
            is_active=True,
            name=candidate.canonical_value,
        )
    except model.DoesNotExist as exc:
        raise ValidationError(
            f"{label} ამ ბიზნესისთვის აღარ არის ხელმისაწვდომი."
        ) from exc
    return field_name, canonical, label


def _validated_total_forms(data, prefix):
    try:
        total_forms = int(data[f"{prefix}-TOTAL_FORMS"])
        initial_forms = int(data[f"{prefix}-INITIAL_FORMS"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError(
            "არჩევანის ფორმის მდგომარეობა არასწორია. განაახლეთ გვერდი და სცადეთ ხელახლა."
        ) from exc

    if (
        total_forms < 0
        or initial_forms < 0
        or initial_forms > total_forms
        or total_forms > ProductChoiceFormSet.absolute_max
    ):
        raise ValidationError(
            "არჩევანის ფორმის მდგომარეობა არასწორია. განაახლეთ გვერდი და სცადეთ ხელახლა."
        )
    return total_forms


def _first_available_row(data, *, prefix, total_forms, field_name):
    for row_index in range(total_forms):
        if _is_checked(data.get(f"{prefix}-{row_index}-DELETE")):
            continue
        if not str(data.get(f"{prefix}-{row_index}-{field_name}", "")).strip():
            return row_index
    return None


def _first_matching_row(
    data,
    *,
    prefix,
    total_forms,
    field_name,
    canonical_id,
):
    expected_value = str(canonical_id)
    for row_index in range(total_forms):
        if _is_checked(data.get(f"{prefix}-{row_index}-DELETE")):
            continue
        current_value = str(
            data.get(f"{prefix}-{row_index}-{field_name}", "")
        ).strip()
        if current_value == expected_value:
            return row_index
    return None


def _is_checked(value):
    return str(value or "").casefold() in {"1", "true", "on", "yes"}
