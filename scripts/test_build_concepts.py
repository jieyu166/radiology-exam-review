"""Focused regression tests for deterministic concept generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import build_concepts as build


CONCEPT_TEMPLATE = """---
concepts: [{slug}]
name: {name}
aliases: [{name_zh}]
subspecialty: [NR]
---
**Definition.**

## Summary — first
- **First**: One.[^1]

### Nested classification
- **Nested**: Two.[^2]

## Summary — later
- **Later**: Three.[^3]

## References
[^1]: One.
[^2]: Two.
[^3]: Three.
"""


def write_concept(path: Path, slug: str) -> None:
    path.write_text(
        CONCEPT_TEMPLATE.format(slug=slug, name=slug.title(), name_zh="測試"),
        encoding="utf-8",
        newline="",
    )


def test_extract_links_preserves_balanced_doi_parentheses() -> None:
    content = """
[^1]: DOI: [10.6705/j.jacme.202103_11(1).0002](https://doi.org/10.6705/j.jacme.202103_11(1).0002)（全文已讀）。
[^2]: DOI: [10.1016/S0140-6736(00)02237-6](https://doi.org/10.1016/S0140-6736(00)02237-6)（PubMed PMID 10905241）。
"""
    links = build.extract_links([("參考來源", 3, content)])
    urls = [link["url"] for link in links]

    assert "https://doi.org/10.6705/j.jacme.202103_11(1).0002" in urls
    assert "https://doi.org/10.1016/S0140-6736(00)02237-6" in urls


def test_extract_links_stops_before_chinese_doi_explanations() -> None:
    content = """
[^1]: doi:10.1161/STROKEAHA.107.511162（pc-ASPECTS 原始研究）。
[^2]: doi:10.3174/ajnr.A0689（CTP-ASPECTS 驗證）。
"""
    links = build.extract_links([("參考來源", 3, content)])

    assert [link["url"] for link in links] == [
        "https://doi.org/10.1161/STROKEAHA.107.511162",
        "https://doi.org/10.3174/ajnr.A0689",
    ]
    assert all(urlparse(link["url"]).scheme == "https" for link in links)
    assert all("（" not in link["url"] for link in links)


def test_bare_url_fallback_stops_before_fullwidth_semicolon_prose() -> None:
    content = """
[^1]: DOI [10.53347/rID-57136](https://doi.org/10.53347/rID-57136)；實際查證 accessed 2026-07-06。
[^2]: DOI [10.1161/STR.0000000000000211](https://doi.org/10.1161/STR.0000000000000211)；Hsieh et al.
"""
    links = build.extract_links([("參考來源", 3, content)])

    assert [link["url"] for link in links] == [
        "https://doi.org/10.53347/rID-57136",
        "https://doi.org/10.1161/STR.0000000000000211",
    ]


def test_index_rebuild_uses_only_existing_detail_json_metadata() -> None:
    assert hasattr(build, "build_index_from_detail_files"), (
        "build_concepts must expose deterministic existing-detail index rebuild"
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        details = root / "concepts"
        index_path = root / "concepts-index.json"
        details.mkdir()
        fixtures = [
            {
                "slug": "zeta",
                "name": "Zeta",
                "nameZh": "乙",
                "subspecialty": "NR",
                "checked": False,
                "keyPoints": [],
            },
            {
                "slug": "alpha",
                "name": "Alpha",
                "nameZh": "甲",
                "subspecialty": "NR",
                "checked": True,
                "keyPoints": [],
            },
        ]
        for detail in fixtures:
            (details / f"{detail['slug']}.json").write_text(
                json.dumps(detail),
                encoding="utf-8",
            )

        report = build.build_index_from_detail_files(
            str(details),
            str(index_path),
        )

        assert report == {
            "concepts": [
                {
                    "slug": "alpha",
                    "name": "Alpha",
                    "nameZh": "甲",
                    "subspecialty": "NR",
                    "checked": True,
                },
                {
                    "slug": "zeta",
                    "name": "Zeta",
                    "nameZh": "乙",
                    "subspecialty": "NR",
                    "checked": False,
                },
            ]
        }
        assert json.loads(index_path.read_text(encoding="utf-8")) == report


def test_build_concept_aggregates_all_summary_variants_and_subsections() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "multi-summary.md"
        write_concept(path, "multi-summary")
        detail, warning = build.build_concept(str(path))

    assert warning is None
    assert detail["keyPoints"] == [
        "**First**: One.",
        "**Nested**: Two.",
        "**Later**: Three.",
    ]


def test_batch_scoped_build_is_byte_idempotent_and_never_writes_nonpilot_detail() -> None:
    assert hasattr(build, "build_selected_concepts")
    assert hasattr(build, "load_batch_slugs")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        sources = root / "vault" / "concepts"
        details = root / "data" / "concepts"
        index_path = root / "data" / "concepts-index.json"
        batch_path = root / "docs" / "batch-00.json"
        sources.mkdir(parents=True)
        details.mkdir(parents=True)
        batch_path.parent.mkdir(parents=True)

        selected = ("alpha", "beta")
        for slug in (*selected, "nonpilot"):
            write_concept(sources / f"{slug}.md", slug)
        nonpilot_detail = {
            "slug": "nonpilot",
            "name": "Nonpilot",
            "nameZh": "非試行",
            "subspecialty": "NR",
            "definition": "Reviewed nonpilot bytes.",
            "imagingFindings": "",
            "differentialDiagnosis": [],
            "externalLinks": [],
            "keyPoints": ["Reviewed nonpilot bytes."],
            "management": "",
            "checked": True,
        }
        nonpilot_path = details / "nonpilot.json"
        nonpilot_path.write_text(
            json.dumps(nonpilot_detail, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="",
        )
        batch_path.write_text(
            json.dumps({"notes": [{"slug": slug} for slug in selected]}),
            encoding="utf-8",
        )
        nonpilot_bytes = nonpilot_path.read_bytes()
        nonpilot_mtime = nonpilot_path.stat().st_mtime_ns

        slugs = build.load_batch_slugs(str(batch_path))
        first = build.build_selected_concepts(
            slugs,
            src_dir=str(sources),
            out_dir=str(details),
            index_path=str(index_path),
        )
        first_bytes = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted((root / "data").rglob("*.json"))
        }
        first_mtimes = {
            path.relative_to(root).as_posix(): path.stat().st_mtime_ns
            for path in sorted((root / "data").rglob("*.json"))
        }

        second = build.build_selected_concepts(
            slugs,
            src_dir=str(sources),
            out_dir=str(details),
            index_path=str(index_path),
        )
        second_bytes = {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted((root / "data").rglob("*.json"))
        }
        second_mtimes = {
            path.relative_to(root).as_posix(): path.stat().st_mtime_ns
            for path in sorted((root / "data").rglob("*.json"))
        }

    assert first["builtSlugs"] == list(selected)
    assert second["builtSlugs"] == list(selected)
    assert nonpilot_path.name not in first["writtenFiles"]
    assert first_bytes == second_bytes
    assert first_mtimes == second_mtimes
    assert first_bytes["data/concepts/nonpilot.json"] == nonpilot_bytes
    assert first_mtimes["data/concepts/nonpilot.json"] == nonpilot_mtime


def run_smoke() -> None:
    test_extract_links_preserves_balanced_doi_parentheses()
    test_extract_links_stops_before_chinese_doi_explanations()
    test_bare_url_fallback_stops_before_fullwidth_semicolon_prose()
    test_index_rebuild_uses_only_existing_detail_json_metadata()
    test_build_concept_aggregates_all_summary_variants_and_subsections()
    test_batch_scoped_build_is_byte_idempotent_and_never_writes_nonpilot_detail()
    print("BUILD_CONCEPTS_TEST_OK")


if __name__ == "__main__":
    run_smoke()
