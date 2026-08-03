# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the fixture adapter produces the same
# SourceAcquisition records as the live path, with no network access (task T037).
"""``--fixtures`` must not be a second code path, only a second source of bytes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.acquire.fixtures import (
    FixtureSetError,
    acquire_from_fixtures,
    content_fingerprint,
    load_fixture_payloads,
)
from pipeline.config import PipelineConfig
from pipeline.models.source import AcquisitionOutcome, SourceKey

MOMENT = datetime(2026, 8, 2, 9, 0, tzinfo=UTC)


def _make_set(root: Path) -> Path:
    """A tiny synthetic fixture set — invented names throughout, as the rule requires."""
    fixtures = root / "sample"
    (fixtures / "mfm").mkdir(parents=True)
    (fixtures / "wahapedia").mkdir(parents=True)
    (fixtures / "mfm" / "iron-wardens.html").write_text(
        "<html><body><span>STORM RIDERS</span></body></html>", encoding="utf-8"
    )
    (fixtures / "mfm" / "ashen-covenant.html").write_text(
        "<html><body><span>EMBER SEERS</span></body></html>", encoding="utf-8"
    )
    # The real export is UTF-8 with BOM; a fixture carries one so the reader's BOM handling is
    # exercised rather than assumed.
    (fixtures / "wahapedia" / "Datasheets.csv").write_text(
        "id|name\nWHP-1001|Storm Riders\n", encoding="utf-8-sig"
    )
    return fixtures


def test_payloads_are_read_sorted_and_bom_stripped(tmp_path: Path) -> None:
    fixtures = _make_set(tmp_path)

    pages = load_fixture_payloads(fixtures, SourceKey.MFM)
    assert [p.name for p in pages] == ["ashen-covenant", "iron-wardens"]

    csvs = load_fixture_payloads(fixtures, SourceKey.WAHAPEDIA)
    assert csvs[0].name == "Datasheets"
    assert not csvs[0].text.startswith("﻿"), "the BOM must be stripped, as the live path does"


def test_the_acquisition_record_matches_the_live_shape(
    tmp_path: Path, config: PipelineConfig
) -> None:
    fixtures = _make_set(tmp_path)
    acquisition, payloads = acquire_from_fixtures(
        fixtures, SourceKey.MFM, config, retrieved_at=MOMENT
    )

    assert acquisition.source_key is SourceKey.MFM
    assert acquisition.declared_edition_code == config.mfm_edition
    assert acquisition.outcome is AcquisitionOutcome.OK
    assert acquisition.coverage == {"faction_pages": 2}
    assert acquisition.retrieved_at == "2026-08-02T09:00:00Z"
    assert acquisition.acquisition_id.startswith("mfm-20260802T090000Z-")
    assert acquisition.content_fingerprint.startswith("sha256:")
    assert acquisition.request_count == 0
    assert len(payloads) == 2


def test_the_detail_source_declares_its_own_edition(tmp_path: Path, config: PipelineConfig) -> None:
    fixtures = _make_set(tmp_path)
    acquisition, _ = acquire_from_fixtures(
        fixtures, SourceKey.WAHAPEDIA, config, retrieved_at=MOMENT
    )
    assert acquisition.declared_edition_code == config.detail_edition
    assert acquisition.coverage == {"csv_files": 1}
    # The hybrid pairing is the normal case at launch, not an edge case.
    assert acquisition.declared_edition_code != config.mfm_edition


def test_the_fingerprint_is_order_independent_and_content_sensitive(tmp_path: Path) -> None:
    fixtures = _make_set(tmp_path)
    pages = load_fixture_payloads(fixtures, SourceKey.MFM)

    assert content_fingerprint(pages) == content_fingerprint(list(reversed(pages)))

    (fixtures / "mfm" / "iron-wardens.html").write_text("<html>changed</html>", encoding="utf-8")
    assert content_fingerprint(load_fixture_payloads(fixtures, SourceKey.MFM)) != (
        content_fingerprint(pages)
    )


def test_a_missing_or_empty_fixture_set_is_an_invocation_error(tmp_path: Path) -> None:
    with pytest.raises(FixtureSetError, match="no mfm directory"):
        load_fixture_payloads(tmp_path / "absent", SourceKey.MFM)

    (tmp_path / "empty" / "mfm").mkdir(parents=True)
    with pytest.raises(FixtureSetError, match="holds no"):
        load_fixture_payloads(tmp_path / "empty", SourceKey.MFM)
