"""Focused regression tests for deterministic concept generation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import build_concepts as build


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


def run_smoke() -> None:
    test_extract_links_preserves_balanced_doi_parentheses()
    test_extract_links_stops_before_chinese_doi_explanations()
    test_bare_url_fallback_stops_before_fullwidth_semicolon_prose()
    test_index_rebuild_uses_only_existing_detail_json_metadata()
    print("BUILD_CONCEPTS_TEST_OK")


if __name__ == "__main__":
    run_smoke()
