# Type/Tag Assistant Planning

## Purpose

Type/Tag Assistant is not a taxonomy manager.

It is an assistant layer that:

- reads product description
- compares it with existing business product types and tags
- recognizes existing matches
- suggests conservative new candidates only when safe
- requires seller confirmation before creating anything
- never blocks product creation
- leaves product description searchable even if no type/tag is recognized

Core sentence:

**Product description is the primary input. Existing business types and tags are seller memory.**

## Domain-Agnostic Scope

Type/Tag Assistant is not only for clothing.

Clothing is the first MVP domain because it is rich in choices, descriptions, and seller wording variation. The assistant concept itself must stay domain-agnostic and business-specific.

Future support should make sense across many seller domains, including:

- clothing
- toys
- cosmetics
- handmade products
- gifts
- food and sweets
- accessories
- household products
- small family-business products

Types and tags are business-specific seller memory, not a universal platform taxonomy.

Examples:

- A clothing seller may have:
  - Type: `კაბა`
  - Tag: `პალაცო`
- A toy seller may have:
  - Type: `თოჯინა`
  - Tag: `საგანმანათლებლო`
- A cosmetics seller may have:
  - Type: `კრემი`
  - Tag: `მგრძნობიარე კანისთვის`
- A cake seller may have:
  - Type: `ტორტი`
  - Tag: `უშაქრო`

The system should not impose one global list on all businesses.

## Product Description, Type, and Tag Relationship

### Product description

Product description:

- always remains searchable
- is the seller's natural memory/input
- is the safest fallback

Example:

`ბამბის თეთრი კაბა ბრეტელებით`

Even if no type or tag is recognized, the description still works for search.

### Type

Type answers:

**"ეს რა პროდუქტია?"**

Examples:

- Clothing MVP examples:
- კაბა
- შარვალი
- მაისური
- ჩანთა
- ფეხსაცმელი
- პიჟამა
- ქუდი
- Cross-domain examples:
- სათამაშო
- თოჯინა
- კონსტრუქტორი
- კრემი
- შამპუნი
- სუნამო
- ტორტი
- ნამცხვარი
- სანთელი
- სამკაული
- ჭიქა

Type should be the seller's own useful product kind, not necessarily a platform-wide category.

Type should usually be:

- short
- canonical
- noun-like
- one primary product kind

Type should **not** be:

- color
- size
- material
- price
- availability state
- full product description
- marketing phrase

Bad type examples:

- ყვითელი კაბა
- ლურჯი ზოლებით კაბა
- ბამბის თეთრი კაბა ბრეტელებით
- ახალი
- ფასდაკლება
- M
- ბამბის

### Tag

Tag answers:

**"რა ნიშნით შეიძლება ეს პროდუქტი მოიძებნოს ან გამოირჩეს?"**

Examples:

- Clothing MVP examples:
  - მინი-კაბა
  - ბრეტელებიანი
  - oversize
- Toys:
  - საგანმანათლებლო
  - მუსიკალური
  - ხის
- Cosmetics:
  - დამატენიანებელი
  - მგრძნობიარე კანისთვის
  - travel-size
- Food and sweets:
  - უშაქრო
  - სადღესასწაულო
  - საბავშვო
- Handmade and gifts:
  - ხელნაკეთი
  - პერსონალიზებული
  - სასაჩუქრე

Tag is optional.

Tag should help:

- search
- filtering
- future chatbot retrieval

Tag should **not** become a dumping ground for every token.
It should be useful enough that the seller may want to reuse it later.

Avoid automatically turning these into tags:

- colors such as `თეთრი`, `შავი`, `ყვითელი`
- sizes such as `S`, `M`, `L`, `42`
- stock states
- prices
- every adjective
- material words, until material strategy is implemented separately

Important:

A word can remain searchable without becoming a tag.

Example:

`თეთრი` can be a searchable token from product description, but should not automatically become a tag.

## No Global Taxonomy in MVP

MVP should not ship with default global product types or tags.

Reasons:

- different businesses use different vocabulary
- Georgian wording varies
- seller domains differ too much
- a global taxonomy may confuse sellers
- clean production start is a product decision

The assistant should learn and reuse each business's own types and tags.

## Existing Registry Matching

When seller types product description, future assistant should first compare words and phrases against existing `BusinessProductType` and `BusinessTag` values.

If existing type match is found, future UI may show:

`ამოვიცანი: ტიპი — კაბა`

If existing tag match is found, future UI may show:

`ამოვიცანი: თეგი — მინი-კაბა`

Purpose:

- remind seller of already-created taxonomy
- prevent duplicates
- reward consistent wording
- reduce seller memory burden

Important:

Existing match is safer than new suggestion.

Do not create duplicate types/tags if existing match is found.

## New Candidate Suggestion

When no existing type/tag match is found, future assistant may suggest conservative candidates.

Example:

Product description:

`ყვითელი კაბა ლურჯი ზოლებით`

If no type exists:

`შესაძლო ტიპი: კაბა`

Actions:

- `დადასტურება`
- `გამოტოვება`

If a useful descriptive phrase is detected:

`საძიებო ნიშნად დავიმახსოვრო?`

Candidate:

`ლურჯი ზოლებით`

Actions:

- `დადასტურება`
- `გამოტოვება`

Rules:

- never silently create type/tag
- always require confirmation
- uncertainty should result in no suggestion
- product creation must not be blocked

## UI Wording Principles

Preferred recognition wording:

- `ამოვიცანი: ტიპი — კაბა`
- `ამოვიცანი: თეგი — მინი-კაბა`

Preferred candidate wording:

- `შესაძლო ტიპი: კაბა`
- `საძიებო ნიშნად დავიმახსოვრო?`

Preferred actions:

- `დადასტურება`
- `გამოტოვება`

Avoid:

- `შექმენი ტაქსონომია`
- `მართე თეგები`
- `აირჩიე კატეგორია`
- technical wording
- long explanations

Tone:

- assistive
- quiet
- compact
- rewarding
- not demanding

## Georgian Morphology Problem

Georgian morphology is a first-class issue, not an edge case.

Examples:

- კაბა / კაბის / კაბები
- შარვალი / შარვლის / შარვლები
- ბამბა / ბამბის
- ბავშვი / ბავშვის / საბავშვო
- ზოლი / ზოლები / ზოლებით

Planning conclusion:

Future implementation must avoid creating duplicate types/tags for simple Georgian case/plural variants.

This planning document does **not** implement morphology logic.

## Material Boundary

Material is related, but intentionally deferred to **8L Material Strategy**.

Examples:

- ბამბა
- ბამბის
- 100% ბამბა
- 100 % ბამბა
- cotton
- კოტონი

Current rule:

Material words may remain in product description and search tokens.

Do not turn material into type/tag automatically yet.

Do not add material field in 8K.

## Failure Mode / Safety Rule

If assistant is unsure:

- show nothing
- do not create type/tag
- do not interrupt seller
- product description remains searchable

This is acceptable.

Assistant failure must be non-destructive.

## Current Implementation Decision

Phase 1 is now implemented as:

- existing type and tag recognition preview from current business taxonomy
- read-only `ამოვიცანი` wording near the product description token preview
- inline type creation escape hatch on the product form
- inline tag creation escape hatch on the product form

Still deferred:

- candidate suggestion from arbitrary description text
- confirm-to-create from assistant-generated candidates
- morphology-aware matching
- material assistant behavior

Material remains deferred to **8L Material Strategy**.

## Future Implementation Phases

### Phase 1

- exact existing type/tag match from product description tokens and phrases
- show `ამოვიცანი`
- keep product creation unblocked with inline type/tag escape hatch

### Phase 2

- conservative candidate suggestion
- confirmation required

### Phase 3

- normalization/morphology helpers
- duplicate prevention

### Phase 4

- material assistant integration after 8L strategy

### Phase 5

- optional advanced taxonomy management for power users only

## Explicit Non-Goals

Not in 8K:

- no code
- no migrations
- no model changes
- no automatic detection implementation
- no AI
- no fuzzy search
- no material model
- no alias registry
- no taxonomy editor
- no UI changes
