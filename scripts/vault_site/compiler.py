"""Compile physician-authored Obsidian Markdown into a static publication package.

The compiler deliberately keeps Markdown as the published content.  JSON records
contain only identity, navigation, source locations, links/assets and the small
question interaction projection required by the review UI.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA_VERSION = "vault-native-publication/v1"
COMPILER_VERSION = "1.0.0"
QUESTION_ROOT = "vault/questions"
CONCEPT_ROOT = "vault/concepts"
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
OPTION_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\(([A-Ea-e])\)|([A-Ea-e])[.)])\s+(.+?)\s*$")
ANSWER_RE = re.compile(r"^\s*(?:\*\*)?Ans\s*:\s*([A-Ea-e]{1,5}(?:\s*[,/&]\s*[A-Ea-e]{1,5})?)(?=\s*(?:\*\*|[.\s]|$))", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
WIKILINK_RE = re.compile(r"(?<!!)!?\[\[([^\]]+)\]\]")
EMBED_RE = re.compile(r"!\[\[([^\]]+)\]\]")
INLINE_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
FRONTMATTER_END = "---"
SUPPORTED_SYNTAX = {
    "heading", "paragraph", "unordered_list", "ordered_list", "table", "footnote",
    "callout", "blockquote", "wikilink", "image_embed", "math",
}
ANSWER_STATUSES = {"confirmed", "unresolved", "no_valid_answer"}
ANSWER_MODES = {"single", "any", "all", "none"}


class CompilerError(Exception):
    """A hard publication error that must block a strict build."""


@dataclass
class SourceNote:
    source_path: Path
    relative_path: str
    kind: str
    source_bytes: bytes
    text: str
    frontmatter: dict[str, Any]
    body_start_line: int
    excluded_reason: str | None = None

    @property
    def source_sha256(self) -> str:
        return hashlib.sha256(self.source_bytes).hexdigest()

    @property
    def note_id(self) -> str:
        value = self.frontmatter.get("id")
        if value is not None and str(value).strip():
            return str(value).strip()
        return PurePosixPath(self.relative_path).with_suffix("").name


@dataclass
class BuildResult:
    report: dict[str, Any]
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _json_value(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_json_value(item) for item in inner.split(",") if item.strip()]
    if value.startswith("{") and value.endswith("}"):
        result: dict[str, Any] = {}
        for item in value[1:-1].split(","):
            if ":" in item:
                key, val = item.split(":", 1)
                result[key.strip().strip("'\"")] = _json_value(val)
        return result
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _answer_values(value: Any) -> tuple[list[str], list[str]]:
    """Normalize legacy scalar/list answer values into unique A-E letters."""
    if value is None:
        return [], []
    raw_values = value if isinstance(value, list) else [value]
    letters: list[str] = []
    invalid: list[str] = []
    for raw in raw_values:
        text = str(raw).strip().upper().replace(" ", "")
        if not text:
            continue
        if re.fullmatch(r"[A-E]+", text):
            tokens = list(text)
        elif re.fullmatch(r"[A-E](?:[,/&][A-E])+", text):
            tokens = re.split(r"[,/&]", text)
        else:
            invalid.append(str(raw))
            continue
        for token in tokens:
            if token not in letters:
                letters.append(token)
    return sorted(letters), invalid


def parse_frontmatter(text: str) -> tuple[dict[str, Any], int]:
    """Parse the small YAML subset used by the vault and return body line start."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_END:
        return {}, 1

    result: dict[str, Any] = {}
    current_list: str | None = None
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == FRONTMATTER_END:
            return result, index + 2
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s+-\s+(.*)$", line)
        if list_match and current_list:
            if not isinstance(result.get(current_list), list):
                result[current_list] = []
            result[current_list].append(_json_value(list_match.group(1)))
            continue
        match = re.match(r"^([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*:\s*(.*)$", line)
        if not match or line.startswith((" ", "\t")):
            current_list = None
            continue
        key, raw_value = match.group(1), match.group(2)
        if raw_value.strip():
            result[key] = _json_value(raw_value)
            current_list = None
        else:
            result[key] = []
            current_list = key
    return result, 1


def _read_note(path: Path, vault_root: Path) -> SourceNote:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    relative = path.relative_to(vault_root).as_posix()
    kind = "question" if relative.startswith("questions/") else "concept"
    frontmatter, body_start = parse_frontmatter(text)
    reason = None
    if path.stem.startswith("_"):
        reason = "underscore_basename"
    elif frontmatter.get("publish") is False:
        reason = "publish_false"
    return SourceNote(path, relative, kind, raw, text, frontmatter, body_start, reason)


def discover_sources(vault_root: Path) -> list[SourceNote]:
    """Discover all question/concept Markdown and classify excluded notes."""
    vault_root = Path(vault_root).resolve()
    notes: list[SourceNote] = []
    for root_name in ("questions", "concepts"):
        root = vault_root / root_name
        if not root.exists():
            continue
        notes.extend(_read_note(path, vault_root) for path in root.rglob("*.md") if path.is_file())
    return sorted(notes, key=lambda note: note.relative_path.lower())


def _line_ranges(lines: list[str], matcher: Any) -> list[dict[str, int]]:
    return [{"startLine": index + 1, "endLine": index + 1} for index, line in enumerate(lines) if matcher(line)]


def _outline(note: SourceNote) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    lines = note.text.splitlines()
    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            result.append({
                "level": len(match.group(1)),
                "heading": match.group(2).strip(),
                "startLine": index,
            })
    return result


def _split_target(raw: str) -> tuple[str, str]:
    target, _, display = raw.partition("|")
    return target.strip(), display.strip()


def _links_and_embeds(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    embeds: list[dict[str, str]] = []
    for match in EMBED_RE.finditer(text):
        target, display = _split_target(match.group(1))
        embeds.append({"target": target, "display": display})

    links: list[dict[str, str]] = []
    for match in WIKILINK_RE.finditer(text):
        if match.group(0).startswith("![["):
            continue
        target, display = _split_target(match.group(1))
        links.append({"target": target, "display": display})
    for match in INLINE_LINK_RE.finditer(text):
        links.append({"target": match.group(2).strip(), "display": match.group(1).strip()})
    return links, embeds


def _syntax_inventory(note: SourceNote, links: list[dict[str, str]], embeds: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Classify source constructs without transforming or dropping their bytes."""
    entries: list[dict[str, Any]] = []
    lines = note.text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        syntax = "paragraph"
        if HEADING_RE.match(line):
            syntax = "heading"
        elif re.match(r"^\s*[-*+]\s+", line):
            syntax = "unordered_list"
        elif re.match(r"^\s*\d+[.)]\s+", line):
            syntax = "ordered_list"
        elif stripped.startswith("|"):
            syntax = "table"
        elif re.match(r"^\s*>\s*\[![^]]+\]", line):
            syntax = "callout"
        elif re.match(r"^\s*>\s?", line):
            syntax = "blockquote"
        elif re.match(r"^\s*```", line):
            syntax = "fenced_code"
        elif re.search(r"\(\?[^)]*\)|\^\[[^]]+\]", line) or re.search(r"\[\^[^]]+\]", line):
            syntax = "footnote"
        elif re.search(r"\$[^$]+\$|\$\$", line):
            syntax = "math"
        elif re.search(r"<[^>]+>", line):
            syntax = "unknown_safe_markdown"
        elif "==" in line or "%%" in line:
            syntax = "unknown_safe_markdown"
        entries.append({"sourcePath": note.relative_path, "line": line_number, "syntax": syntax, "supported": syntax in SUPPORTED_SYNTAX})

    for match in WIKILINK_RE.finditer(note.text):
        if match.group(0).startswith("![["):
            continue
        entries.append({"sourcePath": note.relative_path, "line": _find_line(note.text, match.group(0)), "syntax": "wikilink", "supported": True})
    for item in embeds:
        target = item["target"]
        syntax = "image_embed" if Path(target).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS else "embed"
        entries.append({"sourcePath": note.relative_path, "line": _find_line(note.text, f"![[{target}"), "syntax": syntax, "supported": syntax in SUPPORTED_SYNTAX})
    return entries


def _safe_path(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    return cleaned or "asset"


def _source_candidates(vault_root: Path) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    by_relative: dict[str, Path] = {}
    by_name: dict[str, list[Path]] = {}
    for path in sorted(vault_root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            continue
        relative = path.relative_to(vault_root).as_posix().lstrip("/")
        by_relative[relative.lower()] = path
        by_name.setdefault(path.name.lower(), []).append(path)
    return by_relative, by_name


def _resolve_asset(target: str, vault_root: Path, by_relative: dict[str, Path], by_name: dict[str, list[Path]]) -> tuple[Path | None, list[Path]]:
    normalized = target.replace("\\", "/").lstrip("/").lower()
    direct = by_relative.get(normalized)
    if direct:
        return direct, [direct]
    candidates = by_name.get(Path(normalized).name.lower(), [])
    if len(candidates) == 1:
        return candidates[0], candidates
    return None, candidates


def _question_projection(note: SourceNote) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    lines = note.text.splitlines()
    errors: list[dict[str, Any]] = []
    separator_indexes = [index for index, line in enumerate(lines) if line.strip() == "??"]
    answer_status = str(note.frontmatter.get("answerStatus") or "confirmed").strip().lower()
    answer_mode_value = note.frontmatter.get("answerMode")
    answer_mode = str(answer_mode_value).strip().lower() if answer_mode_value not in (None, "") else ""
    explicit_review_state = answer_status in {"unresolved", "no_valid_answer"}
    answer_matches: list[tuple[int, list[str], list[str]]] = []
    for index, line in enumerate(lines):
        match = ANSWER_RE.match(line)
        if match:
            values, invalid = _answer_values(match.group(1))
            answer_matches.append((index, values, invalid))

    if answer_status not in ANSWER_STATUSES:
        errors.append({"code": "question_answer_status", "sourcePath": note.relative_path, "line": note.body_start_line, "message": f"answerStatus must be one of {sorted(ANSWER_STATUSES)}"})
        answer_status = "confirmed"
    if answer_mode and answer_mode not in ANSWER_MODES:
        errors.append({"code": "question_answer_mode", "sourcePath": note.relative_path, "line": note.body_start_line, "message": f"answerMode must be one of {sorted(ANSWER_MODES)}"})
        answer_mode = ""

    if len(separator_indexes) != 1:
        errors.append({"code": "question_sr_boundary", "sourcePath": note.relative_path, "line": separator_indexes[0] + 1 if separator_indexes else note.body_start_line, "message": "published question must contain exactly one ?? boundary"})
    if not answer_matches and not explicit_review_state:
        errors.append({"code": "question_missing_answer", "sourcePath": note.relative_path, "line": note.body_start_line, "message": "published question must contain one Ans: A-E value or an explicit unresolved answerStatus"})
    if len(separator_indexes) != 1:
        return None, errors

    separator = separator_indexes[0]
    option_matches: list[tuple[int, str]] = []
    for index, line in enumerate(lines[:separator]):
        match = OPTION_RE.match(line)
        if match:
            option_matches.append((index, (match.group(1) or match.group(2)).upper()))
    options: list[dict[str, Any]] = []
    for position, (start, letter) in enumerate(option_matches):
        end = option_matches[position + 1][0] if position + 1 < len(option_matches) else separator
        options.append({"letter": letter, "startLine": start + 1, "endLine": end})
    option_letters = {item["letter"] for item in options}
    invalid_option_count = not 3 <= len(options) <= 5
    invalid_five_option_set = len(options) == 5 and option_letters != set("ABCDE")
    if invalid_option_count or invalid_five_option_set:
        errors.append({"code": "question_options", "sourcePath": note.relative_path, "line": separator + 1, "message": f"published question must contain 3-5 options; parsed {len(options)}"})

    answer_sources: list[tuple[str, list[str]]] = []
    for _, values, invalid in answer_matches:
        if invalid and not explicit_review_state:
            errors.append({"code": "question_answer_range", "sourcePath": note.relative_path, "line": separator + 1, "message": f"correct answer must be A-E: {invalid}"})
        if values:
            answer_sources.append(("Ans", values))
    frontmatter_values, frontmatter_invalid = _answer_values(note.frontmatter.get("correctAnswer"))
    if frontmatter_invalid and not explicit_review_state:
        errors.append({"code": "question_answer_range", "sourcePath": note.relative_path, "line": separator + 1, "message": f"correct answer must be A-E: {frontmatter_invalid}"})
    if frontmatter_values:
        answer_sources.append(("correctAnswer", frontmatter_values))
    accepted_values, accepted_invalid = _answer_values(note.frontmatter.get("acceptedAnswers"))
    if accepted_invalid:
        errors.append({"code": "question_accepted_answers", "sourcePath": note.relative_path, "line": separator + 1, "message": f"acceptedAnswers must contain only A-E: {accepted_invalid}"})
    if accepted_values:
        answer_sources.append(("acceptedAnswers", accepted_values))

    unique_sets = {tuple(values) for _, values in answer_sources}
    if explicit_review_state:
        accepted = []
        answer_mode = "none"
    else:
        if len(unique_sets) > 1:
            errors.append({"code": "question_conflicting_answer", "sourcePath": note.relative_path, "line": separator + 1, "message": f"conflicting parsed answer values: {sorted(unique_sets)}"})
        accepted = list(next(iter(unique_sets))) if unique_sets else []
        if not answer_mode:
            answer_mode = "single" if len(accepted) <= 1 else ""
            if len(accepted) > 1:
                errors.append({"code": "question_answer_mode_required", "sourcePath": note.relative_path, "line": separator + 1, "message": "multi-answer questions must declare answerMode: any or all"})
        if answer_mode == "none":
            errors.append({"code": "question_answer_mode", "sourcePath": note.relative_path, "line": separator + 1, "message": "confirmed question cannot use answerMode: none"})
        if answer_mode == "single" and len(accepted) != 1:
            errors.append({"code": "question_answer_mode", "sourcePath": note.relative_path, "line": separator + 1, "message": "answerMode: single requires exactly one accepted answer"})
        if not accepted:
            errors.append({"code": "question_missing_answer", "sourcePath": note.relative_path, "line": note.body_start_line, "message": "confirmed question must declare at least one accepted answer"})

    correct = accepted[0] if len(accepted) == 1 else None
    concepts = note.frontmatter.get("concepts", [])
    if isinstance(concepts, str):
        concepts = [concepts]
    if not isinstance(concepts, list):
        concepts = []
    for match in WIKILINK_RE.finditer(note.text):
        if match.group(0).startswith("![["):
            continue
        target, _ = _split_target(match.group(1))
        if target and target not in concepts:
            concepts.append(target)
    projection = {
        "front": {"startLine": note.body_start_line, "endLine": separator + 1},
        "back": {"startLine": separator + 2, "endLine": len(lines)},
        "options": options,
        "correctAnswer": correct,
        "acceptedAnswers": accepted,
        "answerStatus": answer_status,
        "answerMode": answer_mode or "none",
        "scorable": answer_status == "confirmed" and bool(accepted) and answer_mode != "none" and not errors,
        "reviewStatus": str(note.frontmatter.get("reviewStatus") or ""),
        "conceptIds": sorted({str(item) for item in concepts if str(item).strip()}),
    }
    return projection, errors


def _syntax_diagnostics(note: SourceNote, syntax_inventory: list[dict[str, Any]], embeds: list[dict[str, str]]) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for entry in syntax_inventory:
        if not entry["supported"]:
            diagnostics.append({"severity": "warning", "code": "unknown_safe_markdown", "line": entry["line"], "message": f"{entry['syntax']} is preserved as raw source and rendered as degraded content"})
    for item in embeds:
        if Path(_split_target(item["target"])[0]).suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            diagnostics.append({"severity": "warning", "code": "unsupported_embed", "line": _find_line(note.text, f"![[{item['target']}"), "message": f"unsupported embed preserved: {item['target']}"})
    return diagnostics


def _find_line(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    return 1


def _record(note: SourceNote, raw_path: str, links: list[dict[str, str]], embeds: list[dict[str, str]], diagnostics: list[dict[str, Any]], question: dict[str, Any] | None, asset_map: dict[str, str]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "id": note.note_id,
        "kind": note.kind,
        "sourcePath": note.relative_path,
        "sourceSha256": note.source_sha256,
        "rawPath": raw_path,
        "frontmatter": note.frontmatter,
        "outline": _outline(note),
        "links": links,
        "embeds": [dict(item, resolvedPath=asset_map.get(item["target"])) for item in embeds],
        "diagnostics": diagnostics,
    }
    if question is not None:
        record["sr"] = question
    return record


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _record_path(note: SourceNote) -> str:
    return f"records/{note.kind}/{_safe_path(note.note_id)}.json"


def _inventory_entry(note: SourceNote, status: str, **extra: Any) -> dict[str, Any]:
    return {"sourcePath": note.relative_path, "kind": note.kind, "id": note.note_id, "status": status, **extra}


def build_package(vault_root: Path, output_root: Path, *, strict: bool = True, write: bool = True) -> BuildResult:
    """Compile a vault into ``output_root`` and return a machine-readable result."""
    vault_root = Path(vault_root).resolve()
    output_root = Path(output_root).resolve()
    if output_root == vault_root or vault_root in output_root.parents:
        raise CompilerError("output root must not be inside the vault")

    notes = discover_sources(vault_root)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    syntax_inventory: list[dict[str, Any]] = []
    published: list[SourceNote] = []
    seen_ids: dict[str, SourceNote] = {}
    by_relative, by_name = _source_candidates(vault_root)
    asset_sources: dict[Path, str] = {}
    asset_map_by_note: dict[str, dict[str, str]] = {}

    for note in notes:
        if note.excluded_reason:
            inventory.append(_inventory_entry(note, "excluded", reason=note.excluded_reason))
            continue
        published.append(note)
        if note.note_id in seen_ids:
            errors.append({"code": "duplicate_id", "sourcePath": note.relative_path, "message": f"duplicate published id {note.note_id!r}; first source is {seen_ids[note.note_id].relative_path}"})
        else:
            seen_ids[note.note_id] = note

    for note in published:
        links, embeds = _links_and_embeds(note.text)
        note_syntax = _syntax_inventory(note, links, embeds)
        syntax_inventory.extend(note_syntax)
        diagnostics = _syntax_diagnostics(note, note_syntax, embeds)
        warnings.extend(dict(item, sourcePath=note.relative_path) for item in diagnostics if item.get("severity") == "warning")
        asset_map: dict[str, str] = {}
        for embed in embeds:
            target = embed["target"]
            ext = Path(target).suffix.lower()
            if ext not in SUPPORTED_IMAGE_EXTENSIONS:
                continue
            resolved, candidates = _resolve_asset(target, vault_root, by_relative, by_name)
            line = _find_line(note.text, f"![[{target}")
            if resolved is None and not candidates:
                errors.append({"code": "missing_required_asset", "sourcePath": note.relative_path, "line": line, "target": target, "message": f"required embed not found: {target}"})
                continue
            if resolved is None:
                errors.append({"code": "ambiguous_required_asset", "sourcePath": note.relative_path, "line": line, "target": target, "candidates": [path.relative_to(vault_root).as_posix() for path in candidates], "message": f"required embed has multiple candidates: {target}"})
                continue
            digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            asset_name = f"{digest[:16]}-{_safe_path(resolved.stem)}{resolved.suffix.lower()}"
            asset_path = f"assets/{asset_name}"
            asset_map[target] = asset_path
            asset_sources[resolved] = asset_path
        asset_map_by_note[note.relative_path] = asset_map
        question, question_errors = _question_projection(note) if note.kind == "question" else (None, [])
        errors.extend(question_errors)
        raw_path = f"notes/{note.relative_path}"
        record = _record(note, raw_path, links, embeds, diagnostics, question, asset_map)
        records.append(record)
        inventory.append(_inventory_entry(note, "published", rawPath=raw_path, recordPath=_record_path(note), sourceSha256=note.source_sha256))

    record_paths: dict[str, str] = {}
    for record in records:
        record_path = _record_path(seen_ids[record["id"]])
        previous = record_paths.get(record_path)
        if previous and previous != record["sourcePath"]:
            errors.append({"code": "duplicate_output_path", "sourcePath": record["sourcePath"], "message": f"duplicate record output path {record_path!r}; first source is {previous}"})
        record_paths[record_path] = record["sourcePath"]

    manifest_entries = []
    for record in sorted(records, key=lambda item: (item["kind"], item["id"], item["sourcePath"])):
        manifest_entries.append({
            "id": record["id"],
            "kind": record["kind"],
            "sourcePath": record["sourcePath"],
            "sourceSha256": record["sourceSha256"],
            "rawPath": record["rawPath"],
            "recordPath": _record_path(seen_ids[record["id"]]),
        })

    concepts = []
    questions = []
    for record in records:
        entry = next(item for item in manifest_entries if item["id"] == record["id"] and item["kind"] == record["kind"])
        frontmatter = record.get("frontmatter", {})
        if record["kind"] == "concept":
            concepts.append(dict(entry, name=frontmatter.get("name") or record["id"], subspecialty=frontmatter.get("subspecialty", []), aliases=frontmatter.get("aliases", [])))
        else:
            years = frontmatter.get("year", [])
            if not isinstance(years, list):
                years = [years] if years not in (None, "") else []
            sr = record.get("sr") or {}
            concept_ids = sr.get("conceptIds", [])
            questions.append(dict(
                entry,
                years=years,
                subspecialty=frontmatter.get("subspecialty", ""),
                conceptIds=concept_ids,
                checked=frontmatter.get("checked", False),
                reviewStatus=sr.get("reviewStatus", ""),
                answerStatus=sr.get("answerStatus", "confirmed"),
                answerMode=sr.get("answerMode", "single"),
                acceptedAnswers=sr.get("acceptedAnswers", []),
                scorable=sr.get("scorable", False),
            ))
    relation_map: dict[str, list[str]] = {}
    search_entries: list[dict[str, Any]] = []
    for record in records:
        if record["kind"] == "question" and record.get("sr"):
            for concept_id in record["sr"].get("conceptIds", []):
                relation_map.setdefault(concept_id, []).append(record["id"])
        search_entries.append({"id": record["id"], "kind": record["kind"], "sourcePath": record["sourcePath"], "title": record["frontmatter"].get("name") or record["id"]})
    relations = [{"conceptId": key, "questionIds": sorted(set(value))} for key, value in sorted(relation_map.items())]
    for entry in search_entries:
        entry["title"] = str(entry["title"])
    report: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "compilerVersion": COMPILER_VERSION,
        "status": "ok" if not errors else "failed",
        "counts": {
            "scanned": len(notes),
            "published": len(published),
            "excluded": len(notes) - len(published),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "inventory": sorted(inventory, key=lambda item: item["sourcePath"]),
        "errors": errors,
        "warnings": warnings,
        "syntaxInventory": sorted(syntax_inventory, key=lambda item: (item["sourcePath"], item["line"], item["syntax"])),
        "syntaxClasses": {key: sum(1 for item in syntax_inventory if item["syntax"] == key) for key in sorted({item["syntax"] for item in syntax_inventory})},
    }
    error_paths = {str(item.get("sourcePath")) for item in errors if item.get("sourcePath")}
    warning_paths = {str(item.get("sourcePath")) for item in warnings if item.get("sourcePath")}
    for item in inventory:
        if item["status"] != "published":
            continue
        if item["sourcePath"] in error_paths:
            item["status"] = "hard_error"
        elif item["sourcePath"] in warning_paths:
            item["status"] = "warning"

    if write and (not strict or not errors):
        if output_root.exists():
            for child in output_root.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        output_root.mkdir(parents=True, exist_ok=True)
        for note in published:
            raw_target = output_root / f"notes/{note.relative_path}"
            raw_target.parent.mkdir(parents=True, exist_ok=True)
            raw_target.write_bytes(note.source_bytes)
        for record in records:
            record_target = output_root / _record_path(seen_ids[record["id"]])
            _write_json(record_target, record)
        for source_path, asset_path in sorted(asset_sources.items(), key=lambda item: item[1]):
            target = output_root / asset_path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target)
        _write_json(output_root / "manifest.json", {"schemaVersion": SCHEMA_VERSION, "compilerVersion": COMPILER_VERSION, "entries": manifest_entries})
        _write_json(output_root / "indexes/concepts.json", {"schemaVersion": SCHEMA_VERSION, "entries": concepts})
        _write_json(output_root / "indexes/questions.json", {"schemaVersion": SCHEMA_VERSION, "entries": questions})
        _write_json(output_root / "indexes/relations.json", {"schemaVersion": SCHEMA_VERSION, "entries": relations})
        _write_json(output_root / "indexes/search.json", {"schemaVersion": SCHEMA_VERSION, "entries": sorted(search_entries, key=lambda item: (item["kind"], item["id"]))})
        _write_json(output_root / "build-report.json", report)
    elif write:
        output_root.mkdir(parents=True, exist_ok=True)
        _write_json(output_root / "build-report.json", report)

    if strict and errors:
        return BuildResult(report, errors, warnings)
    return BuildResult(report, errors, warnings)


def _is_safe_package_path(value: str) -> bool:
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_package(vault_root: Path, output_root: Path) -> BuildResult:
    """Validate an already-built package without rewriting it."""
    vault_root = Path(vault_root).resolve()
    output_root = Path(output_root).resolve()
    with tempfile.TemporaryDirectory(prefix="vault-site-validate-") as temp_dir:
        expected_root = Path(temp_dir) / "expected"
        compiled = build_package(vault_root, expected_root, strict=False, write=True)
        errors = list(compiled.errors)
        report = dict(compiled.report)
        actual_manifest_path = output_root / "manifest.json"
        if not actual_manifest_path.exists():
            errors.append({"code": "missing_manifest", "sourcePath": "", "message": "package is missing manifest.json"})
            return BuildResult(_validation_report(report, errors), errors, compiled.warnings)
        try:
            actual_manifest = json.loads(actual_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"code": "invalid_manifest", "sourcePath": "", "message": f"cannot read manifest.json: {exc}"})
            return BuildResult(_validation_report(report, errors), errors, compiled.warnings)

        expected_manifest = json.loads((expected_root / "manifest.json").read_text(encoding="utf-8"))
        expected_entries = {entry["sourcePath"]: entry for entry in expected_manifest.get("entries", [])}
        actual_entries = {entry.get("sourcePath"): entry for entry in actual_manifest.get("entries", []) if isinstance(entry, dict)}
        notes_by_path = {note.relative_path: note for note in discover_sources(vault_root)}
        for source_path, expected in expected_entries.items():
            actual = actual_entries.get(source_path)
            note = notes_by_path.get(source_path)
            if actual is None:
                errors.append({"code": "missing_manifest_entry", "sourcePath": source_path, "message": "eligible note has no manifest entry"})
                continue
            for field in ("id", "kind", "sourcePath", "sourceSha256", "rawPath", "recordPath"):
                if actual.get(field) != expected.get(field):
                    errors.append({"code": "manifest_mismatch", "sourcePath": source_path, "message": f"manifest field {field} does not match compiler output"})
            for field in ("rawPath", "recordPath"):
                path_value = str(actual.get(field, ""))
                if not _is_safe_package_path(path_value) or not (output_root / path_value).resolve().is_relative_to(output_root):
                    errors.append({"code": "unsafe_output_path", "sourcePath": source_path, "message": f"output path is outside configured output root: {path_value}"})
                elif not (output_root / path_value).is_file():
                    errors.append({"code": "missing_package_file", "sourcePath": source_path, "message": f"package is missing {field}: {path_value}"})
            raw_path = output_root / str(actual.get("rawPath", ""))
            if note and raw_path.is_file():
                actual_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
                if actual_hash != note.source_sha256:
                    errors.append({"code": "raw_source_hash_mismatch", "sourcePath": source_path, "message": f"raw asset hash {actual_hash} does not equal source hash {note.source_sha256}"})
            record_path = output_root / str(actual.get("recordPath", ""))
            if note and record_path.is_file():
                try:
                    actual_record = json.loads(record_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append({"code": "invalid_record", "sourcePath": source_path, "message": f"cannot read record: {exc}"})
                else:
                    required_keys = {"id", "kind", "sourcePath", "sourceSha256", "rawPath", "frontmatter", "outline", "links", "embeds", "diagnostics"}
                    missing_keys = sorted(required_keys - set(actual_record))
                    if missing_keys:
                        errors.append({"code": "record_schema_mismatch", "sourcePath": source_path, "message": f"record is missing keys: {missing_keys}"})
                    expected_headings = {(item["level"], item["heading"], item["startLine"]) for item in _outline(note)}
                    actual_headings = {(item.get("level"), item.get("heading"), item.get("startLine")) for item in actual_record.get("outline", []) if isinstance(item, dict)}
                    for heading in sorted(expected_headings - actual_headings):
                        errors.append({"code": "record_outline_missing", "sourcePath": source_path, "line": heading[2], "message": f"record outline is missing source heading {heading[1]!r}"})
        for source_path in sorted(set(actual_entries) - set(expected_entries)):
            errors.append({"code": "unexpected_manifest_entry", "sourcePath": source_path or "", "message": "manifest contains an entry not produced by the current eligible source inventory"})
        return BuildResult(_validation_report(report, errors), errors, compiled.warnings)


def _validation_report(report: dict[str, Any], errors: list[dict[str, Any]]) -> dict[str, Any]:
    result = dict(report)
    result["status"] = "ok" if not errors else "failed"
    result["errors"] = errors
    result["counts"] = dict(result.get("counts", {}), errors=len(errors))
    return result


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Compile Obsidian vault notes into a vault-native static package")
    parser.add_argument("--vault", type=Path, default=Path("vault"))
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--report", type=Path, help="also copy the machine-readable build report to this path")
    parser.add_argument("--allow-errors", action="store_true", help="write a report/package even when hard errors are found")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = build_package(args.vault, args.output, strict=not args.allow_errors, write=True)
    if args.report:
        _write_json(args.report, result.report)
    print(json.dumps({"status": result.report["status"], "counts": result.report["counts"], "output": str(args.output)}, ensure_ascii=False))
    if result.errors:
        for error in result.errors[:20]:
            print(f"ERROR {error.get('code')}: {error.get('sourcePath')} {error.get('message')}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
