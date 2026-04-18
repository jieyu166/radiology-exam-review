#!/usr/bin/env python3
"""Import Obsidian spaced-repetition exchange questions into JSON data files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET = SCRIPT_DIR.parent
DEFAULT_VAULT = DEFAULT_TARGET.parent / "0\u7b46\u8a18" / "Radiology"

YEAR_TAG_RE = re.compile(r"#(\d{4})\u4ea4\u63db")
SR_COMMENT_RE = re.compile(r"<!--SR:[\s\S]*?-->")
ANS_RE = re.compile(r"^\s*Ans\s*:\s*([A-Ea-e])\b[\.\)]?", re.IGNORECASE)
TAG_TOKEN_RE = re.compile(r"^\s*(?:#[^\s#]+\s*)+")
LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*]\s+|\d+[\.\)]\s*)+")
QUOTE_RE = re.compile(r"^\s*>\s?")
CODE_FENCE_RE = re.compile(r"^\s*```")
UNKNOWN_SPECIALTY_TAG_RE = re.compile(r"#\S+\u8003")
OBSIDIAN_EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")

VALID_SUBSPECIALTIES = {
    "ABD",
    "CV",
    "CH",
    "NR",
    "MSK",
    "H&N",
    "PED",
    "IR",
    "Physics",
    "Breast",
    "US",
    "Unknown",
}
SUBSPECIALTY_TAGS = {
    "#NR\u8003": "NR",
}
OPTION_LETTERS = ["A", "B", "C", "D", "E"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@dataclass
class Skip:
    source: str
    line: int
    reason: str
    detail: str = ""


@dataclass
class Candidate:
    source_path: Path
    rel_path: str
    line_number: int
    lines: list[str]
    yaml_subspecialty: str | None


@dataclass
class ParsedQuestion:
    source: str
    line: int
    years: list[int]
    canonical_year: int
    subspecialty: str
    subspecialty_confidence: str
    question_text: str
    options: list[dict[str, str]]
    correct_answer: str
    explanation: str
    reference: str = ""


@dataclass
class Report:
    scanned_files: int = 0
    candidates: int = 0
    imported: int = 0
    skipped: list[Skip] = field(default_factory=list)
    kept_existing: int = 0
    replaced_existing: int = 0
    updated_existing: int = 0
    yaml_fallbacks: list[dict[str, object]] = field(default_factory=list)
    unknown_specialty_tags: list[dict[str, object]] = field(default_factory=list)
    per_year: Counter = field(default_factory=Counter)
    per_subspecialty: Counter = field(default_factory=Counter)
    written_files: list[str] = field(default_factory=list)
    copied_images: list[dict[str, str]] = field(default_factory=list)
    missing_image_embeds: list[dict[str, object]] = field(default_factory=list)
    ambiguous_image_embeds: list[dict[str, object]] = field(default_factory=list)
    unsupported_embeds: list[dict[str, object]] = field(default_factory=list)
    image_conflicts: list[dict[str, object]] = field(default_factory=list)

    def skip(self, source: str, line: int, reason: str, detail: str = "") -> None:
        self.skipped.append(Skip(source, line, reason, detail))

    def as_dict(self) -> dict:
        return {
            "scannedFiles": self.scanned_files,
            "candidateCount": self.candidates,
            "importedCount": self.imported,
            "skippedCount": len(self.skipped),
            "skipped": [s.__dict__ for s in self.skipped],
            "keptExisting": self.kept_existing,
            "replacedExisting": self.replaced_existing,
            "updatedExisting": self.updated_existing,
            "yamlFallbacks": self.yaml_fallbacks,
            "unknownSpecialtyTags": self.unknown_specialty_tags,
            "perYear": dict(sorted(report_key_items(self.per_year))),
            "perSubspecialty": dict(sorted(report_key_items(self.per_subspecialty))),
            "writtenFiles": self.written_files,
            "pendingImageCopies": getattr(self, "pending_image_copies", []),
            "copiedImages": self.copied_images,
            "missingImageEmbeds": self.missing_image_embeds,
            "ambiguousImageEmbeds": self.ambiguous_image_embeds,
            "unsupportedEmbeds": self.unsupported_embeds,
            "imageConflicts": self.image_conflicts,
        }


class ImageResolver:
    def __init__(self, vault: Path, target: Path, report: Report) -> None:
        self.vault = vault
        self.target = target
        self.report = report
        self.by_rel: dict[str, Path] = {}
        self.by_name: dict[str, list[Path]] = defaultdict(list)
        self.pending: dict[Path, str] = {}
        self._output_stems: dict[str, Path] = {}
        self._build_index()

    def _build_index(self) -> None:
        for path in sorted(p for p in self.vault.rglob("*") if p.is_file()):
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            rel = path.relative_to(self.vault).as_posix()
            self.by_rel[_norm_embed_target(rel).lower()] = path
            self.by_name[path.name.lower()].append(path)

    def convert_text(self, text: str, source: str, line: int) -> str:
        if not text:
            return text

        def replace(match: re.Match[str]) -> str:
            raw = match.group(1).strip()
            target_text, display = split_embed_target(raw)
            ext = Path(target_text).suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                self.report.unsupported_embeds.append({
                    "source": source,
                    "line": line,
                    "target": target_text,
                })
                return match.group(0)

            resolved = self.resolve(target_text, source, line)
            if resolved is None:
                return match.group(0)

            web_path = self.register_copy(resolved)
            alt = display or Path(target_text).stem
            return f"![{alt}]({web_path})"

        return OBSIDIAN_EMBED_RE.sub(replace, text)

    def resolve(self, target_text: str, source: str, line: int) -> Path | None:
        normalized = _norm_embed_target(target_text)
        rel_match = self.by_rel.get(normalized.lower())
        if rel_match:
            return rel_match

        matches = self.by_name.get(Path(normalized).name.lower(), [])
        if len(matches) == 1:
            return matches[0]
        if not matches:
            self.report.missing_image_embeds.append({
                "source": source,
                "line": line,
                "target": target_text,
            })
            return None

        self.report.ambiguous_image_embeds.append({
            "source": source,
            "line": line,
            "target": target_text,
            "candidates": [p.relative_to(self.vault).as_posix() for p in matches],
        })
        return None

    def register_copy(self, source_path: Path) -> str:
        if source_path in self.pending:
            return self.pending[source_path]

        rel = source_path.relative_to(self.vault).as_posix()
        digest = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]
        stem = safe_filename_stem(source_path.stem)
        ext = source_path.suffix.lower()
        filename = f"{stem}-{digest}{ext}"
        web_path = f"data/images/obsidian/{filename}"
        existing_for_stem = self._output_stems.get(stem)
        if existing_for_stem and existing_for_stem != source_path:
            self.report.image_conflicts.append({
                "stem": stem,
                "source": rel,
                "existingSource": existing_for_stem.relative_to(self.vault).as_posix(),
                "target": web_path,
            })
        self._output_stems[stem] = source_path
        self.pending[source_path] = web_path
        return web_path

    def copy_registered(self) -> None:
        out_dir = self.target / "data" / "images" / "obsidian"
        out_dir.mkdir(parents=True, exist_ok=True)
        for source_path, web_path in sorted(self.pending.items(), key=lambda item: item[1]):
            target_path = self.target / web_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)
            self.report.copied_images.append({
                "source": source_path.relative_to(self.vault).as_posix(),
                "target": web_path,
            })


def report_key_items(counter: Counter) -> list[tuple[str, int]]:
    return [(str(key), value) for key, value in counter.items()]


def _norm_embed_target(target: str) -> str:
    return str(target or "").strip().replace("\\", "/").lstrip("/")


def split_embed_target(raw: str) -> tuple[str, str]:
    target, _, display = raw.partition("|")
    return target.strip(), display.strip()


def safe_filename_stem(stem: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", stem.strip()).strip(".-").lower()
    return cleaned or "image"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Obsidian SR exchange questions.")
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help="Obsidian vault path")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="radiology-exam-review root")
    parser.add_argument(
        "--merge-mode",
        choices=["keep", "replace", "update"],
        default="keep",
        help="How to handle existing target question ids",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and report without writing JSON")
    parser.add_argument("--report", type=Path, help="Optional report JSON output path")
    return parser.parse_args(argv)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_markdown_files(vault: Path) -> list[Path]:
    return sorted(p for p in vault.rglob("*.md") if p.is_file())


def strip_blockquote(line: str) -> str:
    return QUOTE_RE.sub("", line)


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines

    fm: dict[str, str] = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        m = re.match(r"^([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*:\s*(.*)$", lines[i])
        if m:
            value = m.group(2).strip().strip('"').strip("'")
            fm[m.group(1)] = value

    if end is None:
        return fm, lines
    return fm, lines[end + 1 :]


def clean_content_lines(lines: Iterable[str]) -> list[str]:
    cleaned = []
    for line in lines:
        line = strip_blockquote(line).rstrip()
        if SR_COMMENT_RE.search(line):
            break
        cleaned.append(line)
    return cleaned


def find_candidates(path: Path, rel_path: str, body_lines: list[str], yaml_subspecialty: str | None) -> list[Candidate]:
    normalized = [strip_blockquote(line) for line in body_lines]
    starts = [i for i, line in enumerate(normalized) if YEAR_TAG_RE.search(line)]
    candidates: list[Candidate] = []
    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else len(normalized)
        candidates.append(Candidate(path, rel_path, start + 1, normalized[start:end], yaml_subspecialty))
    return candidates


def assign_subspecialty(lines: list[str], yaml_subspecialty: str | None, report: Report, source: str, line: int) -> tuple[str, str]:
    joined = "\n".join(lines[:5])
    for tag, subspecialty in SUBSPECIALTY_TAGS.items():
        if tag in joined:
            return subspecialty, "manual"

    for tag in sorted(set(UNKNOWN_SPECIALTY_TAG_RE.findall(joined))):
        if tag not in SUBSPECIALTY_TAGS:
            report.unknown_specialty_tags.append({"source": source, "line": line, "tag": tag})

    if yaml_subspecialty and yaml_subspecialty in VALID_SUBSPECIALTIES:
        return yaml_subspecialty, "manual"

    if yaml_subspecialty and yaml_subspecialty not in ("", "Unknown"):
        report.yaml_fallbacks.append({
            "source": source,
            "line": line,
            "yamlSubspecialty": yaml_subspecialty,
            "used": "Unknown",
        })
    return "Unknown", "auto"


def strip_leading_tags(text: str) -> str:
    prev = None
    out = text.strip()
    while prev != out:
        prev = out
        out = LIST_PREFIX_RE.sub("", out).strip()
        out = TAG_TOKEN_RE.sub("", out).strip()
    return out


def remove_noise(text: str) -> str:
    text = SR_COMMENT_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return strip_leading_tags(text)


def option_marker(line: str, kind: str) -> tuple[str | None, str | None]:
    stripped = line.strip()
    if kind == "letter":
        m = re.match(r"^(?:[-*]\s*)?(?:\(([A-Ea-e])\)|([A-Ea-e])[\.\)])\s+(.+)$", stripped)
        if not m:
            return None, None
        letter = (m.group(1) or m.group(2)).upper()
        return letter, m.group(3).strip()
    if kind == "numeric":
        m = re.match(r"^([1-5])[\.\)]\s+(.+)$", stripped)
        if not m:
            return None, None
        if YEAR_TAG_RE.search(m.group(2)):
            return None, None
        return OPTION_LETTERS[int(m.group(1)) - 1], m.group(2).strip()
    if kind == "bullet":
        m = re.match(r"^-\s+(.+)$", stripped)
        if not m:
            return None, None
        if YEAR_TAG_RE.search(m.group(1)):
            return None, None
        return "", m.group(1).strip()
    raise ValueError(kind)


def without_fences(lines: Iterable[str]) -> list[str]:
    return [line for line in lines if not CODE_FENCE_RE.match(line)]


def parse_options(question_lines: list[str], kind: str) -> tuple[str, list[dict[str, str]]]:
    lines = without_fences(question_lines)
    question_prefix: list[str] = []
    options: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    saw_option = False

    for line in lines:
        letter, text = option_marker(line, kind)
        if letter is not None:
            saw_option = True
            if kind == "bullet":
                letter = OPTION_LETTERS[len(options)] if len(options) < len(OPTION_LETTERS) else "?"
            current = {"letter": letter, "text": text or ""}
            options.append(current)
            continue

        if saw_option:
            if current and line.strip():
                current["text"] = (current["text"] + " " + line.strip()).strip()
        else:
            question_prefix.append(line)

    question_text = remove_noise("\n".join(question_prefix))
    options = [{"letter": o["letter"], "text": remove_noise(o["text"])} for o in options]
    return question_text, options


def parse_question_side(lines: list[str]) -> tuple[str, list[dict[str, str]]]:
    for kind in ("letter", "numeric", "bullet"):
        question_text, options = parse_options(lines, kind)
        if 3 <= len(options) <= 5:
            return question_text, options
    return remove_noise("\n".join(without_fences(lines))), []


def parse_candidate(candidate: Candidate, report: Report) -> ParsedQuestion | None:
    source = candidate.rel_path
    lines = clean_content_lines(candidate.lines)
    report.candidates += 1

    years = sorted({int(y) for y in YEAR_TAG_RE.findall("\n".join(lines))})
    if not years:
        report.skip(source, candidate.line_number, "missing_year_tag")
        return None

    sep_idx = next((i for i, line in enumerate(lines) if line.strip() == "??"), -1)
    if sep_idx == -1:
        report.skip(source, candidate.line_number, "missing_separator", "No ?? line")
        return None

    ans_idx = -1
    answer = ""
    for i in range(sep_idx + 1, len(lines)):
        m = ANS_RE.match(lines[i])
        if m:
            ans_idx = i
            answer = m.group(1).upper()
            break
    if ans_idx == -1:
        report.skip(source, candidate.line_number, "missing_answer", "No Ans: line after ??")
        return None

    question_text, options = parse_question_side(lines[:sep_idx])
    if not (3 <= len(options) <= 5):
        report.skip(source, candidate.line_number, "invalid_options", f"parsed {len(options)} options")
        return None

    letters = {opt["letter"] for opt in options}
    if answer not in letters:
        report.skip(source, candidate.line_number, "answer_mismatch", f"answer {answer} not in {sorted(letters)}")
        return None

    explanation_lines = []
    first_answer_line = ANS_RE.sub("", lines[ans_idx], count=1).strip()
    if first_answer_line:
        explanation_lines.append(first_answer_line)
    for line in lines[ans_idx + 1 :]:
        if SR_COMMENT_RE.search(line):
            break
        explanation_lines.append(line)
    explanation = "\n".join(explanation_lines).strip()

    subspecialty, confidence = assign_subspecialty(lines, candidate.yaml_subspecialty, report, source, candidate.line_number)
    canonical_year = min(years)
    return ParsedQuestion(
        source=source,
        line=candidate.line_number,
        years=years,
        canonical_year=canonical_year,
        subspecialty=subspecialty,
        subspecialty_confidence=confidence,
        question_text=question_text,
        options=options,
        correct_answer=answer,
        explanation=explanation,
    )


def convert_question_images(q: ParsedQuestion, resolver: ImageResolver) -> None:
    q.question_text = resolver.convert_text(q.question_text, q.source, q.line)
    q.reference = resolver.convert_text(q.reference, q.source, q.line)
    q.explanation = resolver.convert_text(q.explanation, q.source, q.line)
    for option in q.options:
        option["text"] = resolver.convert_text(option.get("text", ""), q.source, q.line)


def scan_vault(vault: Path, report: Report, resolver: ImageResolver | None = None) -> list[ParsedQuestion]:
    parsed: list[ParsedQuestion] = []
    md_files = iter_markdown_files(vault)
    report.scanned_files = len(md_files)
    for path in md_files:
        rel_path = path.relative_to(vault).as_posix()
        text = read_text(path)
        fm, body = parse_frontmatter(text)
        yaml_subspecialty = fm.get("subspecialty") or None
        for candidate in find_candidates(path, rel_path, body, yaml_subspecialty):
            q = parse_candidate(candidate, report)
            if q:
                if resolver:
                    convert_question_images(q, resolver)
                parsed.append(q)
    return parsed


def load_existing_year(target: Path, year: int) -> dict:
    path = target / "data" / f"{year}.json"
    if not path.exists():
        return {"year": year, "totalQuestions": 0, "questions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def question_to_json(q: ParsedQuestion, number: int) -> dict:
    return {
        "id": f"{q.canonical_year}-{number:03d}",
        "year": q.canonical_year,
        "number": number,
        "years": q.years,
        "subspecialty": q.subspecialty,
        "subspecialty_confidence": q.subspecialty_confidence,
        "questionText": q.question_text,
        "options": q.options,
        "correctAnswer": q.correct_answer,
        "reference": q.reference,
        "explanation": q.explanation,
        "images": [],
        "concepts": [],
        "checked": False,
    }


def build_outputs(parsed: list[ParsedQuestion], target: Path, merge_mode: str, report: Report) -> dict[int, dict]:
    grouped: dict[int, list[ParsedQuestion]] = defaultdict(list)
    for q in sorted(parsed, key=lambda item: (item.canonical_year, item.source.lower(), item.line)):
        grouped[q.canonical_year].append(q)

    outputs: dict[int, dict] = {}
    for year, questions in grouped.items():
        existing_data = load_existing_year(target, year)
        existing = {q.get("id"): q for q in existing_data.get("questions", [])}
        output_questions = list(existing_data.get("questions", [])) if merge_mode in ("keep", "update") else []

        for idx, parsed_question in enumerate(questions, start=1):
            question_json = question_to_json(parsed_question, idx)
            qid = question_json["id"]
            if qid in existing:
                if merge_mode == "keep":
                    report.kept_existing += 1
                    continue
                if merge_mode == "update":
                    for idx, current in enumerate(output_questions):
                        if current.get("id") == qid:
                            merged = dict(current)
                            merged.update(question_json)
                            output_questions[idx] = merged
                            report.updated_existing += 1
                            break
                    continue
                if merge_mode == "replace":
                    output_questions = [q for q in output_questions if q.get("id") != qid]
                    report.replaced_existing += 1

            output_questions.append(question_json)
            report.imported += 1
            for y in question_json["years"]:
                report.per_year[str(y)] += 1
            report.per_subspecialty[question_json["subspecialty"]] += 1

        output_questions.sort(key=lambda q: (int(q.get("year", year)), int(q.get("number", 0)), q.get("id", "")))
        outputs[year] = {
            "year": year,
            "totalQuestions": len(output_questions),
            "questions": output_questions,
        }
    return outputs


def build_index(outputs: dict[int, dict], target: Path) -> dict:
    years = {}
    index_path = target / "data" / "index.json"
    if index_path.exists():
        try:
            existing = json.loads(index_path.read_text(encoding="utf-8"))
            for entry in existing.get("years", []):
                years[int(entry["year"])] = entry
        except Exception:
            years = {}

    for year, data in outputs.items():
        subs = sorted({q.get("subspecialty", "Unknown") for q in data.get("questions", []) if q.get("subspecialty")})
        years[year] = {
            "year": year,
            "totalQuestions": len(data.get("questions", [])),
            "subspecialties": subs,
        }
    return {"years": [years[y] for y in sorted(years, reverse=True)]}


def write_outputs(outputs: dict[int, dict], index: dict, target: Path, report: Report, resolver: ImageResolver | None = None) -> None:
    data_dir = target / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    if resolver:
        resolver.copy_registered()
    for year, data in sorted(outputs.items()):
        path = data_dir / f"{year}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report.written_files.append(path.as_posix())
    index_path = data_dir / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report.written_files.append(index_path.as_posix())


def print_report(report: Report) -> None:
    data = report.as_dict()
    print("Import report")
    print(f"  Scanned files: {data['scannedFiles']}")
    print(f"  Candidates: {data['candidateCount']}")
    print(f"  Imported: {data['importedCount']}")
    print(f"  Skipped: {data['skippedCount']}")
    print(f"  Existing kept/replaced/updated: {data['keptExisting']}/{data['replacedExisting']}/{data['updatedExisting']}")
    print(f"  Per year: {data['perYear']}")
    print(f"  Per subspecialty: {data['perSubspecialty']}")
    if data["writtenFiles"]:
        print("  Written files:")
        for path in data["writtenFiles"]:
            print(f"    - {path}")
    pending = getattr(report, "pending_image_copies", [])
    print(f"  Images pending-copy/copied/missing/ambiguous/unsupported: {len(pending)}/{len(report.copied_images)}/{len(report.missing_image_embeds)}/{len(report.ambiguous_image_embeds)}/{len(report.unsupported_embeds)}")
    if report.skipped:
        print("  First skipped blocks:")
        for skip in report.skipped[:10]:
            detail = f" ({skip.detail})" if skip.detail else ""
            print(f"    - {skip.source}:{skip.line} {skip.reason}{detail}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    vault = args.vault.resolve()
    target = args.target.resolve()
    if not vault.exists():
        print(f"ERROR: vault not found: {vault}", file=sys.stderr)
        return 2
    if not target.exists():
        print(f"ERROR: target not found: {target}", file=sys.stderr)
        return 2

    source_hashes = {path: file_hash(path) for path in iter_markdown_files(vault)}
    report = Report()
    resolver = ImageResolver(vault, target, report)
    parsed = scan_vault(vault, report, resolver)
    report.pending_image_copies = [
        {"source": source.relative_to(vault).as_posix(), "target": web_path}
        for source, web_path in sorted(resolver.pending.items(), key=lambda item: item[1])
    ]
    outputs = build_outputs(parsed, target, args.merge_mode, report)
    index = build_index(outputs, target)

    if not args.dry_run:
        write_outputs(outputs, index, target, report, resolver)

    after_hashes = {path: file_hash(path) for path in source_hashes}
    changed_sources = [str(path) for path, before in source_hashes.items() if after_hashes.get(path) != before]
    if changed_sources:
        print("ERROR: source markdown changed during import", file=sys.stderr)
        for path in changed_sources[:10]:
            print(f"  {path}", file=sys.stderr)
        return 3

    print_report(report)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
