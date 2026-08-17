"""Pure semantic-recognition contract for seller product descriptions."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
import re


class SemanticDestination(StrEnum):
    PRODUCT_TYPE = "product_type"
    TAG = "tag"
    MATERIAL = "material"
    CHOICE_SIZE = "choice_size"
    CHOICE_COLOR = "choice_color"
    MEASUREMENT = "measurement"
    SEARCH_TOKEN = "search_token"

    @property
    def label(self) -> str:
        return {
            self.PRODUCT_TYPE: "Product type",
            self.TAG: "Tag",
            self.MATERIAL: "Material",
            self.CHOICE_SIZE: "Choice size",
            self.CHOICE_COLOR: "Choice color",
            self.MEASUREMENT: "Measurement",
            self.SEARCH_TOKEN: "Search token",
        }[self]


class CandidateSource(StrEnum):
    SUPPLIED_TERM = "supplied_term"


@dataclass(frozen=True)
class RecognitionTerm:
    """Caller-provided vocabulary term available to the recognition service."""

    destination: SemanticDestination
    canonical_value: str
    aliases: tuple[str, ...] = field(default_factory=tuple)

    def match_values(self) -> tuple[str, ...]:
        values = (self.canonical_value, *self.aliases)
        seen = set()
        normalized_values = []

        for value in values:
            normalized = value.strip()
            key = normalized.casefold()
            if normalized and key not in seen:
                seen.add(key)
                normalized_values.append(normalized)

        return tuple(normalized_values)


@dataclass(frozen=True)
class RecognitionCandidate:
    """Transient candidate meaning found in observed seller text."""

    destination: SemanticDestination
    canonical_value: str
    observed_text: str
    span_start: int
    span_end: int
    source: CandidateSource = CandidateSource.SUPPLIED_TERM
    requires_confirmation: bool = field(default=True, init=False)
    is_confirmed: bool = field(default=False, init=False)


@dataclass(frozen=True)
class ConfirmedFact:
    """Structured truth that must come from later seller confirmation/persistence."""

    destination: SemanticDestination
    value: str


@dataclass(frozen=True)
class RecognitionResult:
    """Recognition output that keeps observed, candidate, and confirmed layers apart."""

    observed_text: str
    candidates: tuple[RecognitionCandidate, ...] = field(default_factory=tuple)
    confirmed_facts: tuple[ConfirmedFact, ...] = field(default_factory=tuple)

    def candidates_for(
        self,
        destination: SemanticDestination,
    ) -> tuple[RecognitionCandidate, ...]:
        return tuple(
            candidate
            for candidate in self.candidates
            if candidate.destination == destination
        )


NEGATION_MARKERS = ("არ", "არა", "no", "not", "without")


def recognize_product_description(
    description: str | None,
    terms: Iterable[RecognitionTerm] = (),
) -> RecognitionResult:
    """Return transient candidates from observed text without confirming facts."""
    observed_text = description or ""
    candidate_rows = []
    seen_candidates = set()

    for term in terms:
        canonical_value = term.canonical_value.strip()
        if not canonical_value:
            continue

        for match_value in term.match_values():
            for match in _find_phrase_matches(observed_text, match_value):
                if _is_negated_match(observed_text, match.start(), match.end()):
                    continue

                candidate_key = (
                    term.destination,
                    canonical_value.casefold(),
                    match.start(),
                    match.end(),
                )
                if candidate_key in seen_candidates:
                    continue

                seen_candidates.add(candidate_key)
                candidate_rows.append(
                    (
                        match.start(),
                        match.end(),
                        canonical_value.casefold(),
                        RecognitionCandidate(
                            destination=term.destination,
                            canonical_value=canonical_value,
                            observed_text=match.group(0),
                            span_start=match.start(),
                            span_end=match.end(),
                        ),
                    )
                )

    candidates = tuple(
        row[3] for row in sorted(candidate_rows, key=lambda row: row[:3])
    )
    return RecognitionResult(observed_text=observed_text, candidates=candidates)


def product_type_terms_for_business(business) -> tuple[RecognitionTerm, ...]:
    """Return recognition terms for Product Types owned by one Business."""
    if business is None:
        return ()

    from catalog.models import BusinessProductType

    return tuple(
        RecognitionTerm(
            destination=SemanticDestination.PRODUCT_TYPE,
            canonical_value=product_type.name,
            aliases=tuple(alias.alias for alias in product_type.aliases.all()),
        )
        for product_type in BusinessProductType.objects.filter(
            business=business
        ).prefetch_related("aliases")
    )


def recognize_product_types_for_business(
    description: str | None,
    business,
) -> RecognitionResult:
    """Recognize Product Type candidates from one Business's vocabulary only."""
    return recognize_product_description(
        description,
        terms=product_type_terms_for_business(business),
    )


def tag_terms_for_business(business) -> tuple[RecognitionTerm, ...]:
    """Return recognition terms for Tags owned by one Business."""
    if business is None:
        return ()

    from catalog.models import BusinessTag

    return tuple(
        RecognitionTerm(
            destination=SemanticDestination.TAG,
            canonical_value=tag.name,
            aliases=tuple(alias.alias for alias in tag.aliases.all()),
        )
        for tag in BusinessTag.objects.filter(business=business).prefetch_related(
            "aliases"
        )
    )


def recognize_tags_for_business(
    description: str | None,
    business,
) -> RecognitionResult:
    """Recognize Tag candidates from one Business's vocabulary only."""
    return recognize_product_description(
        description,
        terms=tag_terms_for_business(business),
    )


def material_terms_for_business(business) -> tuple[RecognitionTerm, ...]:
    """Return material recognition terms from confirmed facts owned by one Business."""
    if business is None:
        return ()

    from catalog.models import ProductMaterialFact

    terms = []
    seen_materials = set()

    material_values = (
        ProductMaterialFact.objects.filter(
            business=business,
            confirmation_state=ProductMaterialFact.ConfirmationState.CONFIRMED,
        )
        .order_by("canonical_material", "id")
        .values_list("canonical_material", flat=True)
    )
    for material in material_values:
        canonical_material = material.strip()
        key = canonical_material.casefold()
        if not canonical_material or key in seen_materials:
            continue

        seen_materials.add(key)
        terms.append(
            RecognitionTerm(
                destination=SemanticDestination.MATERIAL,
                canonical_value=canonical_material,
            )
        )

    return tuple(terms)


def recognize_materials_for_business(
    description: str | None,
    business,
) -> RecognitionResult:
    """Recognize Material candidates from one Business's confirmed facts only."""
    return recognize_product_description(
        description,
        terms=material_terms_for_business(business),
    )


def choice_suggestion_terms(
    size_values: Iterable[str] | None = None,
    color_values: Iterable[str] | None = None,
) -> tuple[RecognitionTerm, ...]:
    """Return caller-supplied size/color terms for choice suggestions."""
    terms = []
    terms.extend(
        _terms_from_values(
            destination=SemanticDestination.CHOICE_SIZE,
            values=size_values,
        )
    )
    terms.extend(
        _terms_from_values(
            destination=SemanticDestination.CHOICE_COLOR,
            values=color_values,
        )
    )
    return tuple(terms)


def recognize_choice_suggestions(
    description: str | None,
    size_values: Iterable[str] | None = None,
    color_values: Iterable[str] | None = None,
) -> RecognitionResult:
    """Recognize transient size/color candidates for later choice creation."""
    return recognize_product_description(
        description,
        terms=choice_suggestion_terms(
            size_values=size_values,
            color_values=color_values,
        ),
    )


def recognize_product_preview_for_business(
    description: str | None,
    business,
) -> RecognitionResult:
    """Compose transient Product candidates from one Business's stored truth."""
    if business is None:
        return recognize_product_description(description)

    from catalog.models import ProductChoice

    choice_values = ProductChoice.objects.filter(
        business=business,
        product__business=business,
    ).order_by("size", "color", "id").values_list("size", "color")
    size_values = []
    color_values = []
    for size, color in choice_values:
        size_values.append(size)
        color_values.append(color)

    terms = (
        *product_type_terms_for_business(business),
        *tag_terms_for_business(business),
        *material_terms_for_business(business),
        *choice_suggestion_terms(
            size_values=size_values,
            color_values=color_values,
        ),
    )
    return recognize_product_description(description, terms=terms)


def _find_phrase_matches(text: str, phrase: str) -> Iterable[re.Match]:
    pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
    return re.finditer(pattern, text, flags=re.IGNORECASE)


def _terms_from_values(
    destination: SemanticDestination,
    values: Iterable[str] | None,
) -> tuple[RecognitionTerm, ...]:
    if not values:
        return ()

    terms = []
    seen_values = set()
    for value in values:
        canonical_value = value.strip()
        key = canonical_value.casefold()
        if not canonical_value or key in seen_values:
            continue

        seen_values.add(key)
        terms.append(
            RecognitionTerm(
                destination=destination,
                canonical_value=canonical_value,
            )
        )

    return tuple(terms)


def _is_negated_match(text: str, start: int, end: int) -> bool:
    before = text[max(0, start - 24) : start].casefold().strip(" \t\n,.;:-")
    after = text[end : end + 24].casefold().strip(" \t\n,.;:-")

    return (
        any(before.endswith(marker) for marker in NEGATION_MARKERS)
        or any(after.startswith(marker) for marker in NEGATION_MARKERS)
    )
