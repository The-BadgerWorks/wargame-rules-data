# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the deterministic core of the D5
# matching ladder for US1 (needed by the T073 reconcile stage): authored faction mapping, stable
# identity first, faction-scoped normalised exact match with a parent-faction fallback, authored
# aliases, and refusal on ambiguity.
# Completed for US2 (task T088): report-only suggestion ranking, faction-scoped and
# Legends-discriminated registry keys, and alias resolution of the detail-source pairing.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added a publication-id narrowing step to
# stage 2, ahead of REC-AMBIGUOUS-MATCH: when a chapter's FactionMapEntry names its own
# detail-source publication id, candidates are narrowed to it first, and only fall through to the
# ambiguous-match finding if that narrowing does not resolve to exactly one candidate. Fixes the
# real Black Templars case, where its supplement republishes core-codex datasheets under
# colliding names and neither copy is Legends.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added chapter-keyword narrowing after it
# (docs/follow-ups.md item 4): html mode carries no publication id, so the publication-id step is
# inert there and the same collision resurfaced. The signal html mode does carry is the card's own
# faction keywords, read against curation/keyword-classes.json's curator-authored chapter records.
# AI-Assisted: Claude Code (model: claude-opus-5) - 009 rung R01b: `resolve_factions` takes the
# detail ids carry-forward actually used this run (`carried_forward_detail_ids`) and does not
# raise `REC-DETAIL-FACTION-EMPTY` for them. Every carried-forward faction is parentless, so the
# ancestor walk that spares a Space Marine chapter saved none of them, and the splice runs after
# assembly with no way to withdraw a finding already appended -- so 008's approved safety net
# turned exit 0 into exit 30 on exactly the runs it exists for.
"""Pair the points source's units with the detail source's datasheets, deterministically.

The ladder, and the reason each rung exists (research D5):

**Stage 0 — faction mapping is authored, not derived.** The two taxonomies genuinely disagree:
the points source publishes 30 faction pages while the detail source carries 26 faction ids,
splitting the chapters one way and the titan legions the other. No rule derives one from the
other, so `curation/faction-map.json` states it, and an unmapped slug is **blocking** — the
alternative is a faction silently missing from the snapshot.

**Stage 1 — stable identity first.** `curation/unit-map.json` is consulted before any name is
compared. That is what makes an upstream rename land as a changed display name on an *unchanged*
curated id (FR-015), which in turn is what stops a rename from looking like a removal plus an
addition and breaking every saved army that names the unit.

**Stage 2 — normalised exact match**, scoped to the faction, falling back to the parent faction
for chapter sub-factions because the points source lists a chapter unit the detail source files
under its parent. When that scoping still leaves two or more same-named candidates — as it does
for the five Space Marine chapters, which share the parent's detail-source faction id outright —
three narrowing signals are consulted in turn, and each is consulted **only** because the one
before it failed:

1. **the Legends flag**, since two datasheets differing only in Legends status are two datasheets;
2. **``detail_source_publication_id``**, when the mapping names its own — a chapter whose own
   supplement republishes a core-codex datasheet under a colliding name;
3. **the candidates' own faction keywords**, read against the chapter records in
   ``curation/keyword-classes.json``. A datasheet carrying a chapter's faction keyword can be
   fielded by that chapter and by nobody else, so the faction being matched discards every
   candidate claimed by a chapter it is not, and then prefers a candidate claimed by the chapter
   it *is*.

Every one of the three resolves the pair only when it leaves **exactly one** candidate; otherwise
the ladder falls through to ``REC-AMBIGUOUS-MATCH`` unchanged. Rung 3 exists because rung 2 is
inert under ``html`` mode: a datacard page states Legends as a class token and never states which
publication a datasheet came from, so the whole page is one publication and there is nothing to
prefer with (``docs/follow-ups.md`` item 4). It is not a fuzzy match by another name — the chapter
records it reads are authored by a curator and asserted against the faction tree (FR-019), so what
narrows the candidates is a **declaration**, exactly as in rungs 1 and 2. Nothing here infers a
chapter from a keyword's spelling.

**Stage 3 — authored aliases**, for spellings a curator has confirmed once.

**Stage 4 — report, never guess.** *No automatic fuzzy match is ever accepted.* The failure mode
is not a missed match — that is a finding a human resolves once and which then carries forward —
it is a *wrong* match, which is a silently mispriced unit in a player's hands at a tournament.
An ambiguous pair is treated as **no** match and blocks. Edit-distance scoring exists in exactly
one place — :func:`rank_suggestions` — and its output goes into a finding's ``suggestions[]`` for
a human to confirm. Nothing in this module reads a score back.

**Curated ids are keyed by faction, and by Legends status within it.** A bare normalised name is
not an identity: the two sources between them publish the same unit name in different factions
(``Slate Warden`` under two banners) and twice within one faction where only the Legends status
differs. Keying on the name alone would hand two distinct datasheets one curated id, which is the
FR-014 violation that resolves a saved army to the wrong unit.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Final

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry, KeywordClassEntry, UnitMapEntry
from pipeline.models.curated import KeywordClass
from pipeline.models.findings import Finding, Suggestion
from pipeline.normalize.names import normalize_name
from pipeline.reconcile.identity import EntityKind, IdRegistry
from pipeline.report.catalogue import build_finding

#: How many candidates a finding offers a human. Three is enough to recognise the right one and
#: few enough that a report of a thousand findings is still readable.
SUGGESTION_LIMIT: Final = 3

#: Below this the "closest candidate" is not close to anything and listing it is noise.
SUGGESTION_FLOOR: Final = 0.5


@dataclass(frozen=True, slots=True)
class FactionScope:
    """One curated faction, with the detail-source faction ids that may supply its datasheets."""

    faction_id: str
    entry: FactionMapEntry
    detail_faction_ids: tuple[str, ...]
    """The faction's own detail id first, then its ancestors' — the parent fallback (C3/R6)."""

    own_chapter_keywords: frozenset[str] = frozenset()
    """The faction keywords a curator has declared name **this** faction as a chapter.

    Normally empty or a single keyword; a set because nothing stops a chapter being reached by
    two spellings and nothing needs to.
    """

    foreign_chapter_keywords: frozenset[str] = frozenset()
    """The faction keywords naming a *different* chapter within this faction's own lineage.

    A datasheet carrying one of these can be fielded by that chapter and by nobody else, so it is
    not this faction's to take. Scoped to the lineage on purpose: a chapter record hanging off an
    unrelated parent must never change what this faction matches, or authoring one faction would
    quietly move another.
    """


@dataclass(frozen=True, slots=True)
class UnitMatch:
    """One resolved pairing. ``wahapedia_datasheet_id`` is ``None`` when only points exist."""

    datasheet_id: str
    faction_id: str
    display_name: str
    wahapedia_datasheet_id: str | None
    stage: str
    """Which rung resolved it: ``identity`` | ``exact`` | ``alias`` | ``unmatched``."""


@dataclass(slots=True)
class MatchOutcome:
    scopes: list[FactionScope] = field(default_factory=list)
    matches: list[UnitMatch] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def datasheet_key(faction_id: str, normalized_name: str, *, is_legends: bool = False) -> str:
    """The registry key one datasheet is minted under.

    Faction-scoped because the same display name legitimately appears in two factions, and
    Legends-discriminated because it legitimately appears twice in one faction where that is the
    only difference. Both are observed cases, and either collision would give two datasheets one
    curated id (FR-014).
    """
    suffix = "/legends" if is_legends else ""
    return f"{faction_id}/{normalized_name}{suffix}"


def rank_suggestions(
    normalized_name: str,
    candidates: Mapping[str, str],
    *,
    limit: int = SUGGESTION_LIMIT,
    floor: float = SUGGESTION_FLOOR,
) -> tuple[Suggestion, ...]:
    """Rank unmatched detail candidates for a **human**, closest first.

    This is the only place in the pipeline that computes a similarity score, and the score
    leaves here only inside a report finding. Ordering is total — score descending, then entity
    reference — so the same inputs produce the same report bytes regardless of the order the
    candidates were collected in (FR-033).
    """
    scored = [
        (SequenceMatcher(None, normalized_name, normalize_name(name)).ratio(), candidate_id)
        for candidate_id, name in candidates.items()
    ]
    ordered = sorted(
        ((score, candidate_id) for score, candidate_id in scored if score >= floor),
        key=lambda item: (-item[0], item[1]),
    )
    return tuple(
        Suggestion(entity_ref=f"wahapedia:{candidate_id}", score=round(score, 4))
        for score, candidate_id in ordered[:limit]
    )


def _detail_ids_for(entry: FactionMapEntry) -> tuple[str, ...]:
    """Every identifier this entry's own detail faction might be read under, in either arm.

    Normally one value. When the entry also declares ``detail_source_faction_code`` (009
    data-model.md §2), **both** the id and the code are returned, never a choice between them —
    there is no mode parameter here (rule 4/FR-012). Whichever arm actually acquired the data,
    only its own vocabulary's value will ever appear in a real row's ``faction_id`` column, so
    the unused alternative simply never matches anything; arm selection falls out of the data
    rather than a branch.
    """
    code = entry.detail_source_faction_code
    if code and code != entry.detail_source_faction_id:
        return (entry.detail_source_faction_id, code)
    return (entry.detail_source_faction_id,)


def resolve_factions(
    slugs: Sequence[str],
    authored: AuthoredContent,
    *,
    detail_faction_ids_present: Set[str] = frozenset(),
    carried_forward_detail_ids: Set[str] = frozenset(),
) -> MatchOutcome:
    """Stage 0. Map every points-source slug to a curated faction, or block.

    Also reports a detail-source faction id that no mapping references — advisory, because a
    faction the points source does not publish is not a faction a player can field, but it is
    worth an approver knowing about.

    Args:
        detail_faction_ids_present: the faction-id vocabulary actually observed in this run's
            acquired ``Datasheets.csv`` — arm-agnostic; the caller passes what it actually saw,
            whichever arm ran. When non-empty and a scope's own faction ids (its own plus every
            ancestor's, in either vocabulary `_detail_ids_for` returns) share nothing with it,
            the scope is the **blocking** ``REC-DETAIL-FACTION-EMPTY`` (009 FR-015, data-model.md
            §2, plan.md finding 2) — the loud complement to the advisory
            ``REC-DETAIL-FACTION-ORPHAN``, and the one check the coverage ratchets cannot do
            instead, since an empty roster still reads 100% of the OTHER factions' coverage.
            Defaults to empty, which is inert: a caller that has not wired in the acquired
            vocabulary sees exactly today's behaviour.
        carried_forward_detail_ids: the detail-source ids **actually carried forward this run**
            (008 FR-024) — the declared set minus what acquisition returned, resolved at
            acquisition by
            :func:`pipeline.acquire.detail_source.resolve_carried_forward` and passed down as
            plain data. A faction whose ``detail_source_faction_id`` is in this set contributed
            no rows *for a declared, Product-Owner-approved reason*, and
            ``REC-DETAIL-FACTION-EMPTY`` — which is for the **unexplained** case — is not raised
            for it; ``SRC-FACTION-CARRIED-FORWARD`` reports it instead, from
            :func:`pipeline.curate.carry_forward.apply_carried_forward` (rule 10: no second code
            for a condition already reported). Every carried-forward faction is parentless, so
            the ancestor walk below — the thing that spares a Space Marine chapter — rescues none
            of them, and the splice runs *after* assembly with no way to withdraw a finding
            already appended; the exemption therefore has to be made here or not at all.

            **Keyed on "declared and absent", never on "declared".** A declared faction whose
            page answered is not carried this run, is absent from this set, and stays fully
            subject to the guard — which is the case that matters, since "the page answered but
            its rows speak a vocabulary nothing maps" is exactly ``plan.md`` finding 2's shape.
            Empty under any arm that has no per-faction page to fail in the first place, so the
            exemption cannot leak into ``csv`` mode; nothing here knows a mode exists (rule 4).
    """
    outcome = MatchOutcome()
    by_faction = {entry.faction_id: entry for entry in authored.faction_map}
    # Only a chapter the points source models as its own faction can claim a datasheet away from
    # anyone: a chapter with no `chapter_faction_id` is priced on its parent's page, so its
    # datasheets are the parent's to field and discarding them would lose the parent a unit.
    chapters = tuple(
        record
        for record in authored.keyword_classes
        if record.keyword_class == KeywordClass.CHAPTER.value
        and record.chapter_faction_id is not None
    )

    for slug in sorted(slugs):
        entry = authored.faction_for_slug(slug)
        if entry is None:
            outcome.findings.append(
                build_finding(
                    "REC-FACTION-UNMAPPED",
                    entity_refs=[f"mfm:{slug}"],
                    detail={"mfm_slug": slug},
                )
            )
            continue

        detail_ids = list(_detail_ids_for(entry))
        ancestor = entry.parent_faction_id
        seen = {entry.faction_id}
        while ancestor and ancestor not in seen:
            seen.add(ancestor)
            parent = by_faction.get(ancestor)
            if parent is None:
                break
            for parent_id in _detail_ids_for(parent):
                if parent_id not in detail_ids:
                    detail_ids.append(parent_id)
            ancestor = parent.parent_faction_id

        carried_forward = entry.detail_source_faction_id in carried_forward_detail_ids
        if (
            detail_faction_ids_present
            and not carried_forward
            and not (set(detail_ids) & detail_faction_ids_present)
        ):
            outcome.findings.append(
                build_finding(
                    "REC-DETAIL-FACTION-EMPTY",
                    entity_refs=[f"mfm:{slug}"],
                    detail={"faction_id": entry.faction_id, "mfm_slug": slug},
                )
            )

        own, foreign = _chapter_keywords_for(entry.faction_id, lineage=seen, chapters=chapters)
        outcome.scopes.append(
            FactionScope(
                faction_id=entry.faction_id,
                entry=entry,
                detail_faction_ids=tuple(detail_ids),
                own_chapter_keywords=own,
                foreign_chapter_keywords=foreign,
            )
        )

    return outcome


def _chapter_keywords_for(
    faction_id: str, *, lineage: Set[str], chapters: Sequence[KeywordClassEntry]
) -> tuple[frozenset[str], frozenset[str]]:
    """Split the authored chapter keywords into this faction's own and its lineage's others.

    ``lineage`` is the faction plus its ancestors — the same walk the detail-id fallback makes,
    reused rather than repeated so the two can never disagree about who a faction's parent is.
    """
    own = frozenset(
        record.keyword for record in chapters if record.chapter_faction_id == faction_id
    )
    foreign = frozenset(
        record.keyword
        for record in chapters
        if record.chapter_faction_id != faction_id and record.parent_faction_id in lineage
    )
    return own, foreign


def report_orphan_detail_factions(
    detail_faction_ids: Sequence[str], authored: AuthoredContent
) -> list[Finding]:
    """A detail-source faction id no mapping references. Advisory (C3/R6)."""
    referenced = {entry.detail_source_faction_id for entry in authored.faction_map}
    return [
        build_finding(
            "REC-DETAIL-FACTION-ORPHAN",
            entity_refs=[f"wahapedia:{faction_id}"],
            detail={"detail_source_faction_id": faction_id},
        )
        for faction_id in sorted(set(detail_faction_ids) - referenced)
    ]


def _narrow_by_chapter_keyword(
    candidates: Sequence[str],
    scope: FactionScope,
    detail_faction_keywords: Mapping[str, Set[str]],
) -> list[str] | None:
    """The one candidate the faction's chapter keywords leave, or ``None`` for still-ambiguous.

    Two questions, asked in that order and for different reasons:

    1. **Which of these is claimed by the chapter I am?** A datasheet carrying this faction's own
       chapter keyword is this faction's copy; the other is somebody else's.
    2. **Which of these is claimed by a chapter I am not?** Those are not this faction's to field
       at all, so they are discarded — which is what lets the *parent* faction, whose own chapter
       keyword set is empty, still resolve to the copy no chapter has claimed.

    ``None`` for every other outcome. Narrowing that leaves nothing, or that leaves two, is not a
    resolution — it is the same ambiguity, and stage 4's refusal is the correct answer to it.
    """
    if not scope.own_chapter_keywords and not scope.foreign_chapter_keywords:
        return None

    own = [
        candidate
        for candidate in candidates
        if detail_faction_keywords.get(candidate, frozenset()) & scope.own_chapter_keywords
    ]
    if own:
        return own if len(own) == 1 else None

    unclaimed = [
        candidate
        for candidate in candidates
        if not (
            detail_faction_keywords.get(candidate, frozenset()) & scope.foreign_chapter_keywords
        )
    ]
    return unclaimed if len(unclaimed) == 1 else None


def match_units(
    scope: FactionScope,
    *,
    display_names: Sequence[str],
    detail_names: Mapping[str, str],
    detail_is_legends: Mapping[str, bool],
    detail_source_ids: Mapping[str, str],
    detail_faction_keywords: Mapping[str, Set[str]],
    authored: AuthoredContent,
    registry: IdRegistry,
) -> MatchOutcome:
    """Run stages 1-4 for one faction.

    Args:
        display_names: the points source's unit names for this faction, as published.
        detail_names: detail-source ``datasheet_id -> display name`` in scope (own + ancestors).
        detail_is_legends: the Legends flag per detail datasheet id, consulted **before** the
            name, so two datasheets differing only by Legends never collide.
        detail_source_ids: the detail source's own publication id (Wahapedia's ``source_id``)
            per datasheet id. Consulted only when the Legends flag has failed to narrow an
            ambiguous stage-2 match and the scope's ``FactionMapEntry`` names its own
            ``detail_source_publication_id`` — never to accept a fuzzy match, only to prefer a
            chapter's own supplement over a same-named core-codex twin (see module docstring).
        detail_faction_keywords: the **faction** keywords each detail datasheet carries. Consulted
            last of the three narrowing signals, and only against the chapter keywords the scope
            resolved from ``curation/keyword-classes.json``; a faction with no chapter records in
            its lineage never reaches it. Required rather than defaulted: it is the only signal
            ``html`` mode carries for this collision, and a caller that forgot it would get a
            silently blocking run rather than an error.
    """
    outcome = MatchOutcome()

    by_normalised: dict[str, list[str]] = {}
    for candidate_id, candidate_name in detail_names.items():
        by_normalised.setdefault(normalize_name(candidate_name), []).append(candidate_id)

    # Stage 1's index. The authored map is authoritative on its own — the id registry is
    # consulted only when an id has to be *issued*, which by definition is not this case.
    #
    # Faction-scoped when an entry declares `faction_id` (009 data-model.md §1, risk R-C), on
    # the same two-tier shape the sibling alias index a few lines below already uses
    # (`alias.faction_id == scope.faction_id`). This loop runs ONCE PER FACTION SCOPE: an entry
    # with no `faction_id` still matches every scope (today's behaviour, unchanged), but an entry
    # WITH one is a curated decision that ONLY this faction's copy of the shared name resolves to
    # its `datasheet_id` — without this, one entry for a name shared across six Space Marine
    # chapters would `registry.adopt` the SAME `datasheet_id` under six different
    # `datasheet_key`s, collapsing six per-chapter identifiers into one (a direct C1 breach).
    identity_by_name: dict[tuple[str | None, str], UnitMapEntry] = {
        (entry.faction_id, entry.mfm_display_name): entry for entry in authored.unit_map
    }
    # The reverse of it, so an alias can resolve the *detail* pairing too. An alias records a
    # curated id, which is the durable half; the detail-source id that curated id was confirmed
    # against lives in the unit map, and re-deriving it from the name is exactly the derivation
    # the alias exists because nobody could make.
    detail_for_curated = {
        entry.datasheet_id: entry.wahapedia_datasheet_id for entry in authored.unit_map
    }
    aliases = {
        normalize_name(alias.alias): alias.datasheet_id
        for alias in authored.unit_aliases
        if alias.faction_id == scope.faction_id
    }

    # Only candidates nothing has claimed are worth suggesting: proposing a datasheet that is
    # already paired with another unit wastes the curator's attention on a pairing they cannot
    # accept. Names are processed in sorted order, so the set a finding sees is deterministic.
    claimed: set[str] = set()

    for display_name in sorted(set(display_names)):
        unmatched_detail = {
            candidate_id: name
            for candidate_id, name in detail_names.items()
            if candidate_id not in claimed
        }
        normalised = normalize_name(display_name)

        # Stage 1 — stable identity, consulted before any name comparison. The scoped entry
        # (this faction's own) wins when both exist; a scopeless entry (`faction_id=None`)
        # matches every scope, exactly as an entry with no `faction_id` did before this field
        # existed.
        mapped = identity_by_name.get((scope.faction_id, display_name)) or identity_by_name.get(
            (None, display_name)
        )
        if mapped is not None:
            registry.adopt(
                EntityKind.DATASHEET,
                datasheet_key(scope.faction_id, normalised),
                mapped.datasheet_id,
            )
            outcome.matches.append(
                UnitMatch(
                    datasheet_id=mapped.datasheet_id,
                    faction_id=scope.faction_id,
                    display_name=display_name,
                    wahapedia_datasheet_id=mapped.wahapedia_datasheet_id or None,
                    stage="identity",
                )
            )
            if mapped.wahapedia_datasheet_id:
                claimed.add(mapped.wahapedia_datasheet_id)
            continue

        candidates = by_normalised.get(normalised, [])

        # Legends disambiguation happens before the name is trusted to be unique (D5).
        if len(candidates) > 1:
            non_legends = [c for c in candidates if not detail_is_legends.get(c, False)]
            if len(non_legends) == 1:
                candidates = non_legends

        # Publication-id disambiguation, tried only once Legends has failed to narrow it, and
        # only when the mapping names its own detail-source publication (the Black Templars
        # case: its supplement republishes a core-codex datasheet under a colliding name, and
        # neither copy is Legends). Never applied if it would leave zero or 2+ candidates — that
        # is still ambiguous, not resolved, and must still block (D5 stage 4: report, never
        # guess).
        if len(candidates) > 1 and scope.entry.detail_source_publication_id is not None:
            publication_id = scope.entry.detail_source_publication_id
            by_publication = [c for c in candidates if detail_source_ids.get(c) == publication_id]
            if len(by_publication) == 1:
                candidates = by_publication

        # Chapter-keyword narrowing, the last of the three signals and the only one `html` mode
        # carries (module docstring, rung 3). Inert for a faction with no chapter records in its
        # lineage, which is every faction outside a chapter tree.
        if len(candidates) > 1:
            by_chapter = _narrow_by_chapter_keyword(candidates, scope, detail_faction_keywords)
            if by_chapter is not None:
                candidates = by_chapter

        if len(candidates) > 1:
            outcome.findings.append(
                build_finding(
                    "REC-AMBIGUOUS-MATCH",
                    entity_refs=[f"mfm:{scope.entry.mfm_slug}/{normalised}"],
                    detail={
                        "faction_id": scope.faction_id,
                        "normalized_name": normalised,
                        "candidate_count": len(candidates),
                        "candidates": sorted(candidates),
                    },
                    suggestions=rank_suggestions(
                        normalised, {c: detail_names[c] for c in candidates}
                    ),
                )
            )
            continue

        # Stage 3 — authored aliases, after the exact attempt and before giving up.
        alias_target = aliases.get(normalised)

        detail_id: str | None = None
        key = datasheet_key(scope.faction_id, normalised)
        if candidates:
            detail_id = candidates[0]
            key = datasheet_key(
                scope.faction_id, normalised, is_legends=detail_is_legends.get(detail_id, False)
            )
            datasheet_id = registry.mint(EntityKind.DATASHEET, key, display_name)
            stage = "exact"
        elif alias_target is not None:
            datasheet_id = alias_target
            registry.adopt(EntityKind.DATASHEET, key, alias_target)
            stage = "alias"
            detail_id = detail_for_curated.get(alias_target) or None
        else:
            # Stage 4 — reported, never guessed. Priced but with no detail: it still ships, on
            # the points the publisher gave it (FR-026, FR-035). The closest candidates are
            # ranked into the finding for a curator, and no further.
            datasheet_id = registry.mint(EntityKind.DATASHEET, key, display_name)
            stage = "unmatched"
            detail_id = None
            outcome.findings.append(
                build_finding(
                    "REC-UNMATCHED-POINTS-ONLY",
                    entity_refs=[f"mfm:{scope.entry.mfm_slug}/{normalised}"],
                    detail={"faction_id": scope.faction_id, "normalized_name": normalised},
                    suggestions=rank_suggestions(normalised, unmatched_detail),
                )
            )

        if detail_id:
            claimed.add(detail_id)

        outcome.matches.append(
            UnitMatch(
                datasheet_id=datasheet_id,
                faction_id=scope.faction_id,
                display_name=display_name,
                wahapedia_datasheet_id=detail_id,
                stage=stage,
            )
        )

    return outcome
