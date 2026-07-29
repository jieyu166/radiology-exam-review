"""Deterministic structural checks for NR concept-note Summary sections.

This module intentionally audits Markdown and evidence metadata only.  It does
not synthesize or rewrite medical content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SUMMARY_HEADING_RE = re.compile(r"^##\s+Summary(?:\s+.*)?\s*$", re.IGNORECASE)
LEVEL_TWO_HEADING_RE = re.compile(r"^##(?:\s|$)")
FOOTNOTE_DEFINITION_RE = re.compile(r"^\[\^(?P<id>[^\]\r\n]+)\]:", re.MULTILINE)
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^(?P<id>[^\]\r\n]+)\]")
VALID_BULLET_RE = re.compile(r"^- \*\*[^*]+\*\*[:：]")
TOP_LEVEL_BULLET_RE = re.compile(r"^-\s*(?P<content>.*)$")
NESTED_BULLET_RE = re.compile(r"^\s{2,}[-*+]\s+")
CALLOUT_RE = re.compile(r"^\s*>\s*\[![^\]]+\]", re.IGNORECASE)
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")


@dataclass(frozen=True)
class SummarySection:
    heading: str
    content: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class NoteRecord:
    path: Path
    slug: str
    subspecialties: tuple[str, ...]
    summaries: tuple[SummarySection, ...]
    footnote_refs: frozenset[str]
    footnote_defs: frozenset[str]
    sha256: str

    @property
    def in_scope(self) -> bool:
        return "NR" in self.subspecialties


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def _parse_frontmatter_array(frontmatter: str, key: str) -> tuple[str, ...]:
    """Read the vault's simple inline YAML arrays without a YAML dependency."""
    match = re.search(rf"(?m)^{re.escape(key)}\s*:\s*(?P<value>.+?)\s*$", frontmatter)
    if not match:
        return ()

    value = match.group("value").strip()
    if value.startswith("[") and value.endswith("]"):
        values = value[1:-1].split(",")
    else:
        values = [value]
    return tuple(item.strip().strip("'\"") for item in values if item.strip())


def extract_summary_sections(body: str) -> list[SummarySection]:
    """Extract each level-two Summary variant, retaining level-three content."""
    lines = body.splitlines()
    sections: list[SummarySection] = []
    start_index: int | None = None

    for index, line in enumerate(lines):
        if start_index is None:
            if SUMMARY_HEADING_RE.match(line):
                start_index = index
            continue

        if LEVEL_TWO_HEADING_RE.match(line):
            sections.append(
                SummarySection(
                    heading=lines[start_index].strip()[3:].strip(),
                    content="\n".join(lines[start_index + 1 : index]).strip(),
                    start_line=start_index + 1,
                    end_line=index,
                )
            )
            start_index = index if SUMMARY_HEADING_RE.match(line) else None

    if start_index is not None:
        sections.append(
            SummarySection(
                heading=lines[start_index].strip()[3:].strip(),
                content="\n".join(lines[start_index + 1 :]).strip(),
                start_line=start_index + 1,
                end_line=len(lines),
            )
        )
    return sections


def parse_note_text(path: Path, text: str) -> NoteRecord:
    """Parse a UTF-8 Obsidian concept note supplied as text."""
    frontmatter_match = FRONTMATTER_RE.match(text)
    frontmatter = frontmatter_match.group("frontmatter") if frontmatter_match else ""
    body = text[frontmatter_match.end() :] if frontmatter_match else text
    definitions = frozenset(match.group("id") for match in FOOTNOTE_DEFINITION_RE.finditer(text))
    references: set[str] = set()
    for line in text.splitlines():
        if FOOTNOTE_DEFINITION_RE.match(line):
            continue
        references.update(match.group("id") for match in FOOTNOTE_REFERENCE_RE.finditer(line))

    return NoteRecord(
        path=path,
        slug=path.stem,
        subspecialties=_parse_frontmatter_array(frontmatter, "subspecialty"),
        summaries=tuple(extract_summary_sections(body)),
        footnote_refs=frozenset(references),
        footnote_defs=definitions,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def parse_note(path: Path) -> NoteRecord:
    """Read and parse one UTF-8 concept Markdown file."""
    return parse_note_text(path, path.read_text(encoding="utf-8"))


def _finding(code: str, note: NoteRecord, message: str) -> Finding:
    return Finding(severity="error", code=code, path=note.path.as_posix(), message=message)


def validate_summary(note: NoteRecord) -> list[Finding]:
    """Return deterministic structural findings for an in-scope NR note."""
    if not note.in_scope:
        return []

    findings: list[Finding] = []
    if not note.summaries:
        findings.append(_finding("summary-missing", note, "NR note has no Summary section."))

    for section in note.summaries:
        valid_bullets = 0
        for relative_line, line in enumerate(section.content.splitlines(), start=1):
            line_number = section.start_line + relative_line
            if NESTED_BULLET_RE.match(line):
                findings.append(_finding("summary-nested-bullet", note, f"Nested bullet at line {line_number}."))
            if CALLOUT_RE.match(line):
                findings.append(_finding("summary-callout", note, f"Callout at line {line_number}."))
            if TABLE_RE.match(line):
                findings.append(_finding("summary-table", note, f"Table row at line {line_number}."))

            bullet_match = TOP_LEVEL_BULLET_RE.match(line)
            if not bullet_match:
                continue
            bullet = bullet_match.group("content").strip()
            if not bullet:
                findings.append(_finding("summary-empty-bullet", note, f"Empty bullet at line {line_number}."))
                continue
            if not VALID_BULLET_RE.match(line) or not FOOTNOTE_REFERENCE_RE.search(bullet):
                findings.append(
                    _finding(
                        "summary-bullet-label",
                        note,
                        f"Bullet at line {line_number} must start with a bold label and cite a footnote.",
                    )
                )
                continue
            valid_bullets += 1

        if valid_bullets == 0:
            findings.append(
                _finding("summary-bullet-label", note, f"{section.heading!r} has no valid top-level bullet.")
            )

    for reference in sorted(note.footnote_refs - note.footnote_defs):
        findings.append(_finding("footnote-undefined", note, f"Footnote reference [^{reference}] has no definition."))
    return findings


def validate_evidence(report: dict, notes: dict[str, NoteRecord]) -> list[Finding]:
    """Validate a batch evidence report.

    Task 1 establishes this callable boundary.  Fact-unit/source mapping rules
    are added with the evidence schema in the following task.
    """
    del report, notes
    return []


def _findings_have_errors(findings: Iterable[Finding]) -> bool:
    return any(finding.severity == "error" for finding in findings)


def _print_findings(findings: Sequence[Finding]) -> None:
    print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))


def _inventory(root: Path) -> dict:
    records = [parse_note(path) for path in sorted(root.rglob("*.md"), key=lambda item: item.as_posix())]
    nr_records = [record for record in records if record.in_scope]
    return {
        "schemaVersion": 1,
        "scope": "NR",
        "notes": [
            {
                "slug": record.slug,
                "path": record.path.as_posix(),
                "subspecialty": list(record.subspecialties),
                "summaryHeadings": [section.heading for section in record.summaries],
                "sha256": record.sha256,
            }
            for record in nr_records
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit NR concept Summary structure.")
    commands = parser.add_subparsers(dest="command", required=True)

    inventory = commands.add_parser("inventory", help="Write a deterministic NR concept inventory.")
    inventory.add_argument("--root", type=Path, required=True)
    inventory.add_argument("--output", type=Path, required=True)

    validate_note = commands.add_parser("validate-note", help="Validate one concept note.")
    validate_note.add_argument("path", type=Path)

    validate_batch = commands.add_parser("validate-batch", help="Validate an evidence batch report.")
    validate_batch.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inventory":
        report = _inventory(args.root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    if args.command == "validate-note":
        findings = validate_summary(parse_note(args.path))
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    if args.command == "validate-batch":
        report = json.loads(args.path.read_text(encoding="utf-8"))
        findings = validate_evidence(report, {})
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
