"""Deterministic structural checks for NR concept-note Summary sections.

This module intentionally audits Markdown and evidence metadata only.  It does
not synthesize or rewrite medical content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Sequence


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SUMMARY_HEADING_RE = re.compile(r"^##\s+Summary(?:\s+\u2014\s+\S.*)?\s*$")
LEVEL_TWO_HEADING_RE = re.compile(r"^##(?:\s|$)")
FOOTNOTE_DEFINITION_RE = re.compile(r"^\[\^(?P<id>[^\]\r\n]+)\]:", re.MULTILINE)
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^(?P<id>[^\]\r\n]+)\]")
VALID_BULLET_RE = re.compile(r"^- \*\*[^*]+\*\*[:\uFF1A]")
TOP_LEVEL_BULLET_RE = re.compile(r"^-\s*(?P<content>.*)$")
NESTED_BULLET_RE = re.compile(r"^\s{2,}[-*+]\s+")
CALLOUT_RE = re.compile(r"^\s*>\s*\[![^\]]+\]", re.IGNORECASE)
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*:?-{3,}:?(?:\s*\|\s*:?-{3,}:?)+\s*$")
TABLE_ROW_RE = re.compile(r"^\s*(?!\|)[^|\r\n]+\|[^|\r\n]+(?:\|[^|\r\n]+)*\s*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NOTE_TYPES = {"disease", "pattern-ddx", "anatomy-measurement-management"}
NOTE_STATUSES = {
    "pending",
    "rewritten",
    "unchanged",
    "research-needed",
    "manual-review",
    "build-failed",
    "verified",
}
SOURCE_STATUSES = {
    "existing-sufficient",
    "research-needed",
    "researched",
    "conflict",
}
FACT_DISPOSITIONS = {
    "pending",
    "covered",
    "research-needed",
    "manual-review",
}
PHASE_1_BATCHES = {"batch-00", "unassigned"}
PILOT_SLUGS = frozenset(
    {
        "clippers",
        "cerebral-amyloid-angiopathy",
        "craniopharyngioma",
        "basal-ganglia-t1-shortening",
        "cpa-masses",
        "bilateral-subcortical-dwi-hyperintensity-ddx",
        "artery-of-adamkiewicz",
        "aspects-score",
        "acute-stroke-management",
        "dementia-neuroimaging-overview",
    }
)

# Every value in this map was assigned by reviewing the corresponding note.
# Inventory generation performs a direct lookup only; it deliberately contains
# no filename, heading, or medical-keyword inference fallback.
NOTE_TYPE_OVERRIDES = {
    "2-hydroxyglutarate-idh-mutant-glioma": "disease",
    "acute-stroke-management": "anatomy-measurement-management",
    "adrenoleukodystrophy": "disease",
    "aicardi-syndrome": "disease",
    "ajcc-8th-head-neck-n-staging": "anatomy-measurement-management",
    "als-imaging": "disease",
    "aneurysm-coiling-recurrence": "anatomy-measurement-management",
    "angioinvasive-aspergillosis": "disease",
    "anti-nmda-encephalitis": "disease",
    "arterial-dissection-mri": "disease",
    "artery-of-adamkiewicz": "anatomy-measurement-management",
    "aspects-score": "anatomy-measurement-management",
    "atlantodental-interval": "anatomy-measurement-management",
    "atypical-teratoid-rhabdoid-tumor": "disease",
    "autoimmune-encephalitis": "disease",
    "basal-ganglia-t1-shortening": "pattern-ddx",
    "basilar-artery-occlusion": "disease",
    "behcet-disease-neuro": "disease",
    "bilateral-subcortical-dwi-hyperintensity-ddx": "pattern-ddx",
    "brachial-plexus-anatomy": "anatomy-measurement-management",
    "brain-abscess": "disease",
    "brain-herniation-syndromes": "anatomy-measurement-management",
    "brain-metastasis-mri": "disease",
    "brain-tumor-imaging": "pattern-ddx",
    "capillary-telangiectasia": "disease",
    "cardioembolic-stroke": "disease",
    "carotid-cavernous-fistula": "disease",
    "carotid-vertebrobasilar-anastomoses": "anatomy-measurement-management",
    "cavernous-sinus-schwannoma": "disease",
    "central-neurocytoma": "disease",
    "cerebral-amyloid-angiopathy": "disease",
    "cerebral-border-zone-infarct-arteries": "anatomy-measurement-management",
    "cerebral-cavernous-malformation": "disease",
    "cerebral-deep-venous-cortex": "anatomy-measurement-management",
    "cerebral-herniation-types": "anatomy-measurement-management",
    "cerebral-infarction-evolution": "anatomy-measurement-management",
    "cerebral-infarction-fogging": "pattern-ddx",
    "cerebral-microbleeds": "pattern-ddx",
    "cerebral-proliferative-angiopathy": "disease",
    "cerebral-pseudoaneurysm": "disease",
    "cerebral-venous-system": "anatomy-measurement-management",
    "cerebral-venous-thrombosis-mri": "disease",
    "cerebrovascular-malformations": "pattern-ddx",
    "cervical-nerve-root-dermatome": "anatomy-measurement-management",
    "cervical-radiculopathy": "disease",
    "chemical-shift-artifact": "pattern-ddx",
    "chiari-malformation": "disease",
    "cholesterol-granuloma-petrous-apex": "disease",
    "clippers": "disease",
    "cns-germinoma": "disease",
    "cns-opportunistic-infection": "pattern-ddx",
    "colloid-cyst": "disease",
    "congenital-aural-atresia": "disease",
    "corpus-callosum-agenesis-signs": "disease",
    "corpus-callosum-dysgenesis": "disease",
    "covid-19-brain-mri": "disease",
    "cpa-masses": "pattern-ddx",
    "cranial-nerve-muscle-atrophy": "pattern-ddx",
    "craniopharyngioma": "disease",
    "craniosynostosis-suture-fusion": "disease",
    "cri-du-chat-syndrome": "disease",
    "ct-venography": "anatomy-measurement-management",
    "dandy-walker-malformation": "disease",
    "dementia-neuroimaging-overview": "pattern-ddx",
    "dural-av-fistula": "disease",
    "dural-avf": "disease",
    "dural-based-masses-aids": "pattern-ddx",
    "dural-venous-sinus-thrombosis": "disease",
    "eac-exostoses": "disease",
    "empty-sella": "disease",
    "ependymoma": "disease",
    "ev71-cns-complications": "disease",
    "fabry-disease-pulvinar": "disease",
    "facial-fracture-complications": "pattern-ddx",
    "facial-nerve-schwannoma": "disease",
    "fahr-disease": "disease",
    "fibromuscular-dysplasia": "disease",
    "gbm": "disease",
    "gbm-vs-pcnsl": "pattern-ddx",
    "glomus-jugulare": "disease",
    "glutaric-aciduria-type1": "disease",
    "gre-hemorrhage-detection": "anatomy-measurement-management",
    "guillain-mollaret-triangle": "anatomy-measurement-management",
    "hair-on-end-skull": "pattern-ddx",
    "head-melanoma-mri-signal": "disease",
    "hemangioblastoma": "disease",
    "hemichorea-hemiballism": "disease",
    "hemimegalencephaly": "disease",
    "hepatic-encephalopathy-manganese-deposition": "disease",
    "herpes-simplex-encephalitis": "disease",
    "hypertensive-hemorrhage": "disease",
    "hypothalamic-anatomy": "anatomy-measurement-management",
    "hypothalamic-hamartoma": "disease",
    "hypoxic-ischemic-encephalopathy": "disease",
    "ia-thrombectomy-stroke-window": "anatomy-measurement-management",
    "iatrogenic-femoral-pseudoaneurysm": "disease",
    "ica-dissection-sites": "anatomy-measurement-management",
    "ich-score": "anatomy-measurement-management",
    "idiopathic-intracranial-hypertension": "disease",
    "incomplete-spinal-cord-syndrome": "disease",
    "inferolateral-trunk-branches": "anatomy-measurement-management",
    "intra-arterial-thrombectomy": "anatomy-measurement-management",
    "intracranial-cystic-lesions": "pattern-ddx",
    "intracranial-germ-cell-tumors": "pattern-ddx",
    "intracranial-lipoma": "disease",
    "intramedullary-spinal-tumors": "pattern-ddx",
    "intraventricular-tumors": "pattern-ddx",
    "ischemic-stroke-imaging-timeline": "anatomy-measurement-management",
    "joubert-syndrome": "disease",
    "lacunar-infarction": "disease",
    "large-vestibular-aqueduct": "disease",
    "larynx-hypopharynx-subsite-anatomy": "anatomy-measurement-management",
    "lemierre-syndrome": "disease",
    "lenticulostriate-arteries": "anatomy-measurement-management",
    "lipomyelomeningocele": "disease",
    "lysosomal-storage-disorders-cns": "pattern-ddx",
    "machine-learning-radiomics-basics": "anatomy-measurement-management",
    "masticator-space": "anatomy-measurement-management",
    "mcdonald-ms-criteria": "anatomy-measurement-management",
    "medulloblastoma-molecular-subgroups": "pattern-ddx",
    "men1": "disease",
    "meninges-anatomy": "anatomy-measurement-management",
    "meningioma-recurrence": "anatomy-measurement-management",
    "metachromatic-leukodystrophy": "disease",
    "methanol-toxicity": "disease",
    "moyamoya": "disease",
    "moyamoya-disease": "disease",
    "mr-elastography-brain": "anatomy-measurement-management",
    "mri-vessel-wall-imaging": "anatomy-measurement-management",
    "mr-spectroscopy-brain": "anatomy-measurement-management",
    "mucopolysaccharidosis-imaging": "pattern-ddx",
    "mucormycosis": "disease",
    "multinodular-vacuolating-neuronal-tumor": "disease",
    "multiple-hypodense-brain-lesions": "pattern-ddx",
    "multiple-sclerosis-imaging": "disease",
    "neurocutaneous-melanosis": "disease",
    "neurofibromatosis-type-1": "disease",
    "neuromyelitis-optica": "disease",
    "neuropsychiatric-sle": "disease",
    "non-sah-vasospasm": "pattern-ddx",
    "normal-myelination-pattern": "anatomy-measurement-management",
    "normal-pressure-hydrocephalus": "disease",
    "npsle-imaging": "disease",
    "odontoid-fracture": "disease",
    "opscc-hpv": "disease",
    "optic-nerve-meningioma": "disease",
    "optic-nerve-sheath-meningioma": "disease",
    "oral-cavity-cancer-ajcc-staging": "anatomy-measurement-management",
    "otosclerosis": "disease",
    "paraneoplastic-syndromes-brain": "pattern-ddx",
    "parathyroid-adenoma": "disease",
    "pca-branches": "anatomy-measurement-management",
    "pediatric-head-neck-infections": "pattern-ddx",
    "pediatric-lgg-genetics": "disease",
    "pediatric-meningitis": "disease",
    "pelizaeus-merzbacher-disease": "disease",
    "perimesencephalic-sah": "disease",
    "persistent-stapedial-artery": "anatomy-measurement-management",
    "pilocytic-astrocytoma": "disease",
    "pituicytoma": "disease",
    "pituitary-macroadenoma": "disease",
    "posterior-cerebral-artery-branches": "anatomy-measurement-management",
    "posterior-fossa-malformations": "pattern-ddx",
    "posterior-fossa-neoplasm-by-age": "pattern-ddx",
    "pres": "disease",
    "psp-imaging-signs": "disease",
    "pterygopalatine-fossa": "anatomy-measurement-management",
    "ra-cervical-spine": "disease",
    "radiation-induced-changes": "pattern-ddx",
    "radiation-induced-hypopituitarism": "disease",
    "radiation-necrosis-vs-tumor-recurrence": "pattern-ddx",
    "rapidly-progressive-dementia": "pattern-ddx",
    "relapsing-remitting-cns": "pattern-ddx",
    "remote-cerebellar-hemorrhage": "disease",
    "retinoblastoma": "disease",
    "retropharyngeal-space": "anatomy-measurement-management",
    "rhombencephalosynapsis": "disease",
    "schwannomatosis": "disease",
    "sciwora": "disease",
    "second-impact-syndrome": "disease",
    "sellar-parasellar-lesions": "pattern-ddx",
    "skull-base-osteomyelitis": "disease",
    "solitary-fibrous-tumor-hemangiopericytoma": "disease",
    "spetzler-martin-avm": "anatomy-measurement-management",
    "sphenoparietal-sinus": "anatomy-measurement-management",
    "spinal-avm": "pattern-ddx",
    "spinal-cord-astrocytoma": "disease",
    "spinal-ewing-sarcoma": "disease",
    "spinal-intramedullary-tumors": "pattern-ddx",
    "spinal-metastasis-pathways": "anatomy-measurement-management",
    "spondylodiscitis": "disease",
    "spontaneous-ich-young-adults": "pattern-ddx",
    "spontaneous-intracranial-hypotension": "disease",
    "spontaneous-skull-base-cephalocele": "disease",
    "sturge-weber-syndrome": "disease",
    "subacute-combined-degeneration": "disease",
    "subdural-empyema": "disease",
    "subependymoma": "disease",
    "superficial-siderosis": "disease",
    "superior-orbital-fissure": "anatomy-measurement-management",
    "takayasu-arteritis": "disease",
    "temporal-bone-fracture": "disease",
    "temporal-bone-inflammatory": "pattern-ddx",
    "temporal-bone-trauma-ossicular": "anatomy-measurement-management",
    "temporomandibular-joint-disorder-mri": "anatomy-measurement-management",
    "thyroid-cancer-tnm-staging": "anatomy-measurement-management",
    "thyroid-rfa": "anatomy-measurement-management",
    "toxic-metabolic-brain-imaging": "pattern-ddx",
    "toxic-metabolic-leukoencephalopathy": "pattern-ddx",
    "trigeminal-neuralgia-neurovascular-compression": "disease",
    "tuberous-sclerosis": "disease",
    "tumefactive-demyelinating-lesion": "disease",
    "vertebrobasilar-dolichoectasia": "disease",
    "who-cns-tumor-grading": "anatomy-measurement-management",
    "wyburn-mason-syndrome": "disease",
    "xenon-ct-perfusion": "anatomy-measurement-management",
}


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
    original_summary: str
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
                    content="\n".join(lines[start_index + 1 : index]),
                    start_line=start_index + 1,
                    end_line=index,
                )
            )
            start_index = index if SUMMARY_HEADING_RE.match(line) else None

    if start_index is not None:
        sections.append(
            SummarySection(
                heading=lines[start_index].strip()[3:].strip(),
                content="\n".join(lines[start_index + 1 :]),
                start_line=start_index + 1,
                end_line=len(lines),
            )
        )
    return sections


def _extract_original_summary(body: str) -> str:
    """Return exact source spans for every accepted level-two Summary."""
    spans: list[str] = []
    start_offset: int | None = None
    offset = 0
    for line in body.splitlines(keepends=True):
        heading_line = line.rstrip("\r\n")
        if LEVEL_TWO_HEADING_RE.match(heading_line):
            if start_offset is not None:
                spans.append(body[start_offset:offset])
            start_offset = offset if SUMMARY_HEADING_RE.match(heading_line) else None
        offset += len(line)
    if start_offset is not None:
        spans.append(body[start_offset:])
    return "".join(spans)


def parse_note_text(path: Path, text: str) -> NoteRecord:
    """Parse a UTF-8 Obsidian concept note supplied as text."""
    frontmatter_match = FRONTMATTER_RE.match(text)
    frontmatter = frontmatter_match.group("frontmatter") if frontmatter_match else ""
    body_start = frontmatter_match.end() if frontmatter_match else 0
    body = text[body_start:]
    body_line_offset = text[:body_start].count("\n")
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
        summaries=tuple(
            SummarySection(
                heading=section.heading,
                content=section.content,
                start_line=section.start_line + body_line_offset,
                end_line=section.end_line + body_line_offset,
            )
            for section in extract_summary_sections(body)
        ),
        original_summary=_extract_original_summary(body),
        footnote_refs=frozenset(references),
        footnote_defs=definitions,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def parse_note(path: Path) -> NoteRecord:
    """Read and parse one UTF-8 concept Markdown file."""
    payload = path.read_bytes()
    note = parse_note_text(path, payload.decode("utf-8"))
    return replace(note, sha256=hashlib.sha256(payload).hexdigest())


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
        section_lines = section.content.splitlines()
        for relative_line, line in enumerate(section_lines, start=1):
            line_number = section.start_line + relative_line
            if NESTED_BULLET_RE.match(line):
                findings.append(_finding("summary-nested-bullet", note, f"Nested bullet at line {line_number}."))
            if CALLOUT_RE.match(line):
                findings.append(_finding("summary-callout", note, f"Callout at line {line_number}."))
            if TABLE_RE.match(line):
                findings.append(_finding("summary-table", note, f"Table row at line {line_number}."))
            elif (
                relative_line > 1
                and TABLE_SEPARATOR_RE.match(line)
                and TABLE_ROW_RE.match(section_lines[relative_line - 2])
            ):
                findings.append(_finding("summary-table", note, f"Table separator at line {line_number}."))

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
    """Validate the lossless, source-mapped batch evidence contract."""
    findings: list[Finding] = []
    batch_path = "docs/reports/nr-summary-rewrite/batch-00.json"
    if not isinstance(report, dict):
        return [
            Finding("error", "evidence-schema", batch_path, "Batch evidence root must be an object.")
        ]

    root_contract = (
        ("schemaVersion", 1, "evidence-schema-version"),
        ("batch", "batch-00", "evidence-batch"),
        ("scope", "NR", "evidence-scope"),
        ("status", "baseline", "evidence-status"),
    )
    for field, expected, code in root_contract:
        if report.get(field) != expected:
            findings.append(
                Finding(
                    "error",
                    code,
                    batch_path,
                    f"Batch field {field!r} must equal {expected!r}.",
                )
            )

    report_notes = report.get("notes")
    if not isinstance(report_notes, list):
        findings.append(
            Finding("error", "evidence-notes", batch_path, "Batch notes must be an array.")
        )
        return findings

    slugs = [
        entry.get("slug")
        for entry in report_notes
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    ]
    if len(report_notes) != len(PILOT_SLUGS) or set(slugs) != PILOT_SLUGS:
        findings.append(
            Finding(
                "error",
                "evidence-batch-membership",
                batch_path,
                "Batch evidence must contain exactly the fixed 10 pilot slugs.",
            )
        )

    seen_slugs: set[str] = set()
    required_note_fields = {
        "slug",
        "type",
        "originalSha256",
        "originalSummary",
        "factUnits",
        "sourceStatus",
        "status",
        "rewrittenSummary",
        "validation",
    }

    for entry in report_notes:
        if not isinstance(entry, dict):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    batch_path,
                    "Every batch note entry must be an object.",
                )
            )
            continue
        slug = entry.get("slug")
        if not isinstance(slug, str) or not slug:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    batch_path,
                    "Every batch note requires a non-empty string slug.",
                )
            )
            continue
        if slug in seen_slugs:
            findings.append(
                Finding(
                    "error",
                    "evidence-duplicate-slug",
                    batch_path,
                    f"Duplicate batch note slug {slug!r}.",
                )
            )
        seen_slugs.add(slug)

        note = notes.get(slug)
        path = note.path.as_posix() if note is not None else str(slug or "<batch>")
        missing_fields = sorted(required_note_fields - entry.keys())
        if missing_fields:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    path,
                    f"Batch note is missing required fields: {', '.join(missing_fields)}.",
                )
            )

        note_type = entry.get("type")
        if note_type not in NOTE_TYPES:
            findings.append(
                Finding("error", "evidence-note-type", path, f"Unsupported note type {note_type!r}.")
            )
        expected_type = NOTE_TYPE_OVERRIDES.get(slug)
        if expected_type is not None and note_type != expected_type:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-type",
                    path,
                    f"Note type must be {expected_type!r}.",
                )
            )
        source_status = entry.get("sourceStatus")
        if source_status not in SOURCE_STATUSES:
            findings.append(
                Finding(
                    "error",
                    "evidence-source-status",
                    path,
                    f"Unsupported source status {source_status!r}.",
                )
            )
        note_status = entry.get("status")
        if note_status not in NOTE_STATUSES:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-status",
                    path,
                    f"Unsupported note status {note_status!r}.",
                )
            )
        if not isinstance(entry.get("rewrittenSummary"), str):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    path,
                    "rewrittenSummary must be a string.",
                )
            )
        if not isinstance(entry.get("validation"), dict):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    path,
                    "validation must be an object.",
                )
            )

        original_hash = entry.get("originalSha256")
        if not isinstance(original_hash, str) or not SHA256_RE.fullmatch(original_hash):
            findings.append(
                Finding(
                    "error",
                    "evidence-sha256",
                    path,
                    "originalSha256 must be a lowercase SHA-256 digest.",
                )
            )
        if note is None:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-missing",
                    path,
                    f"No current note was supplied for slug {slug!r}.",
                )
            )
        else:
            if original_hash != note.sha256:
                findings.append(
                    Finding(
                        "error",
                        "evidence-hash-mismatch",
                        path,
                        "Current note SHA-256 differs from originalSha256.",
                    )
                )
            if entry.get("originalSummary") != note.original_summary:
                findings.append(
                    Finding(
                        "error",
                        "evidence-summary-mismatch",
                        path,
                        "originalSummary is not a lossless snapshot of the current note.",
                    )
                )

        fact_units = entry.get("factUnits")
        if not isinstance(fact_units, list):
            findings.append(
                Finding("error", "evidence-note-schema", path, "factUnits must be an array.")
            )
            continue
        if not fact_units:
            findings.append(
                Finding(
                    "error",
                    "evidence-facts-missing",
                    path,
                    "Every batch note requires at least one fact unit.",
                )
            )

        seen_fact_ids: set[str] = set()
        has_unresolved = False
        for fact_index, fact in enumerate(fact_units, start=1):
            if not isinstance(fact, dict):
                findings.append(
                    Finding("error", "fact-schema", path, "Every fact unit must be an object.")
                )
                continue
            fact_id = fact.get("id", "<unknown>")
            expected_id_re = re.compile(rf"^{re.escape(slug)}-f\d{{2,}}$")
            if not isinstance(fact_id, str) or not expected_id_re.fullmatch(fact_id):
                findings.append(
                    Finding(
                        "error",
                        "fact-id",
                        path,
                        f"Fact ID {fact_id!r} must use the note slug and fNN suffix.",
                    )
                )
            expected_fact_id = f"{slug}-f{fact_index:02d}"
            if fact_id != expected_fact_id:
                findings.append(
                    Finding(
                        "error",
                        "fact-id-sequence",
                        path,
                        f"Fact unit at position {fact_index} must be {expected_fact_id!r}.",
                    )
                )
            if isinstance(fact_id, str):
                if fact_id in seen_fact_ids:
                    findings.append(
                        Finding(
                            "error",
                            "fact-id-duplicate",
                            path,
                            f"Duplicate fact unit ID {fact_id!r}.",
                        )
                    )
                seen_fact_ids.add(fact_id)

            text = fact.get("text")
            if not isinstance(text, str) or not text.strip():
                findings.append(
                    Finding(
                        "error",
                        "fact-text",
                        path,
                        f"Fact unit {fact_id!r} requires non-empty text.",
                    )
                )
            disposition = fact.get("disposition")
            if disposition not in FACT_DISPOSITIONS:
                findings.append(
                    Finding(
                        "error",
                        "fact-disposition",
                        path,
                        f"Fact unit {fact_id!r} has unsupported disposition {disposition!r}.",
                    )
                )
            if disposition in {"research-needed", "manual-review"}:
                has_unresolved = True
            source_refs = fact.get("sourceRefs")
            refs_valid = (
                isinstance(source_refs, list)
                and all(isinstance(source_ref, str) and source_ref for source_ref in source_refs)
                and len(source_refs) == len(set(source_refs))
            )
            if not refs_valid:
                findings.append(
                    Finding(
                        "error",
                        "fact-source-refs",
                        path,
                        f"Fact unit {fact_id!r} sourceRefs must be unique non-empty strings.",
                    )
                )
            if disposition not in {"research-needed", "manual-review"} and (
                not isinstance(source_refs, list) or not source_refs
            ):
                findings.append(
                    Finding(
                        severity="error",
                        code="fact-source-missing",
                        path=path,
                        message=f"Fact unit {fact_id!r} has no mapped source reference.",
                    )
                )
            if note is not None and refs_valid:
                for source_ref in source_refs:
                    if source_ref not in note.footnote_defs:
                        findings.append(
                            Finding(
                                severity="error",
                                code="fact-source-undefined",
                                path=path,
                                message=(
                                    f"Fact unit {fact_id!r} maps to undefined "
                                    f"footnote [^{source_ref}]."
                                ),
                            )
                        )
        validation = entry.get("validation")
        if isinstance(validation, dict):
            valid_fact_units = [fact for fact in fact_units if isinstance(fact, dict)]
            expected_validation = {
                "hashMatches": note is not None and original_hash == note.sha256,
                "losslessSummaryMatches": (
                    note is not None and entry.get("originalSummary") == note.original_summary
                ),
                "allSourceRefsDefined": (
                    note is not None
                    and len(valid_fact_units) == len(fact_units)
                    and all(
                        isinstance(fact.get("sourceRefs"), list)
                        and all(
                            isinstance(source_ref, str)
                            and source_ref
                            and source_ref in note.footnote_defs
                            for source_ref in fact["sourceRefs"]
                        )
                        for fact in valid_fact_units
                    )
                ),
                "factCount": len(fact_units),
                "pendingFactCount": sum(
                    fact.get("disposition") == "pending" for fact in valid_fact_units
                ),
                "researchNeededFactIds": [
                    fact.get("id")
                    for fact in valid_fact_units
                    if fact.get("disposition") == "research-needed"
                ],
                "manualReviewFactIds": [
                    fact.get("id")
                    for fact in valid_fact_units
                    if fact.get("disposition") == "manual-review"
                ],
                "newUnsupportedFacts": 0,
            }
            mismatches = [
                field
                for field, expected in expected_validation.items()
                if validation.get(field) != expected
            ]
            if mismatches:
                findings.append(
                    Finding(
                        "error",
                        "evidence-validation",
                        path,
                        "Stale or invalid validation fields: " + ", ".join(mismatches) + ".",
                    )
                )
        if has_unresolved and source_status not in {"research-needed", "conflict"}:
            findings.append(
                Finding(
                    "error",
                    "evidence-source-status",
                    path,
                    "Unresolved facts require research-needed or conflict sourceStatus.",
                )
            )
        if has_unresolved and note_status not in {"research-needed", "manual-review"}:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-status",
                    path,
                    "Unresolved facts require research-needed or manual-review note status.",
                )
            )
    return findings


def _inventory_finding(code: str, path: str, message: str) -> Finding:
    return Finding(severity="error", code=code, path=path, message=message)


def validate_inventory(inventory: dict) -> list[Finding]:
    """Validate the closed Phase 1 inventory schema and enum values."""
    findings: list[Finding] = []
    if inventory.get("schemaVersion") != 1:
        findings.append(
            _inventory_finding("inventory-schema", "inventory.json", "schemaVersion must be 1.")
        )
    if inventory.get("scope") != "NR":
        findings.append(_inventory_finding("inventory-scope", "inventory.json", "scope must be NR."))
    if inventory.get("generatedFrom") != "vault/concepts":
        findings.append(
            _inventory_finding(
                "inventory-generated-from",
                "inventory.json",
                "generatedFrom must be vault/concepts.",
            )
        )

    entries = inventory.get("notes")
    if not isinstance(entries, list):
        findings.append(_inventory_finding("inventory-schema", "inventory.json", "notes must be a list."))
        return findings

    required = {
        "slug",
        "path",
        "type",
        "batch",
        "status",
        "sourceStatus",
        "originalSha256",
        "summaryHeadings",
    }
    for index, entry in enumerate(entries):
        path = f"inventory.json#notes/{index}"
        if not isinstance(entry, dict):
            findings.append(_inventory_finding("inventory-schema", path, "Inventory entry must be an object."))
            continue
        missing = sorted(required - entry.keys())
        if missing:
            findings.append(
                _inventory_finding(
                    "inventory-schema",
                    path,
                    f"Inventory entry is missing fields: {', '.join(missing)}.",
                )
            )
        if entry.get("type") not in NOTE_TYPES:
            findings.append(
                _inventory_finding(
                    "inventory-type",
                    path,
                    f"Unsupported note type: {entry.get('type')!r}.",
                )
            )
        if entry.get("status") not in NOTE_STATUSES:
            findings.append(
                _inventory_finding(
                    "inventory-status",
                    path,
                    f"Unsupported note status: {entry.get('status')!r}.",
                )
            )
        if entry.get("sourceStatus") not in SOURCE_STATUSES:
            findings.append(
                _inventory_finding(
                    "inventory-source-status",
                    path,
                    f"Unsupported source status: {entry.get('sourceStatus')!r}.",
                )
            )
        if entry.get("batch") not in PHASE_1_BATCHES:
            findings.append(
                _inventory_finding(
                    "inventory-batch",
                    path,
                    f"Unsupported Phase 1 batch: {entry.get('batch')!r}.",
                )
            )
        if not isinstance(entry.get("originalSha256"), str) or not SHA256_RE.fullmatch(
            entry["originalSha256"]
        ):
            findings.append(
                _inventory_finding(
                    "inventory-sha256",
                    path,
                    "originalSha256 must be 64 lowercase hexadecimal characters.",
                )
            )
        if not isinstance(entry.get("summaryHeadings"), list) or not all(
            isinstance(heading, str) for heading in entry.get("summaryHeadings", [])
        ):
            findings.append(
                _inventory_finding(
                    "inventory-summary-headings",
                    path,
                    "summaryHeadings must be a list of strings.",
                )
            )
    return findings


def validate_inventory_against_notes(
    inventory: dict, notes: dict[str, NoteRecord]
) -> list[Finding]:
    """Validate inventory uniqueness and exact coverage of current NR notes."""
    findings = validate_inventory(inventory)
    entries = inventory.get("notes")
    if not isinstance(entries, list):
        return findings

    seen: set[str] = set()
    duplicate_slugs: set[str] = set()
    inventory_slugs: set[str] = set()
    entries_by_slug: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("slug"), str):
            continue
        slug = entry["slug"]
        if slug in seen:
            duplicate_slugs.add(slug)
        seen.add(slug)
        inventory_slugs.add(slug)
        entries_by_slug.setdefault(slug, entry)

    for slug in sorted(duplicate_slugs):
        findings.append(
            _inventory_finding(
                "inventory-duplicate-slug",
                "inventory.json",
                f"Duplicate inventory slug: {slug}.",
            )
        )

    nr_notes = {slug: note for slug, note in notes.items() if note.in_scope}
    missing = sorted(set(nr_notes) - inventory_slugs)
    extra = sorted(inventory_slugs - set(nr_notes))
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing NR slugs: {', '.join(missing)}")
        if extra:
            details.append(f"non-NR or absent slugs: {', '.join(extra)}")
        findings.append(
            _inventory_finding(
                "inventory-scope-mismatch",
                "inventory.json",
                "; ".join(details) + ".",
            )
        )

    for slug in sorted(set(nr_notes) & inventory_slugs):
        entry = entries_by_slug[slug]
        note = nr_notes[slug]
        expected_path = note.path.as_posix()
        if entry.get("path") != expected_path:
            findings.append(
                _inventory_finding(
                    "inventory-path-mismatch",
                    expected_path,
                    f"Inventory path for {slug} does not match the note path.",
                )
            )
        if entry.get("originalSha256") != note.sha256:
            findings.append(
                _inventory_finding(
                    "inventory-hash-mismatch",
                    expected_path,
                    f"Inventory hash for {slug} does not match the current note.",
                )
            )
        expected_headings = [section.heading for section in note.summaries]
        if entry.get("summaryHeadings") != expected_headings:
            findings.append(
                _inventory_finding(
                    "inventory-summary-headings-mismatch",
                    expected_path,
                    f"Inventory Summary headings for {slug} do not match the note.",
                )
            )

    batch_00 = {
        entry.get("slug")
        for entry in entries
        if isinstance(entry, dict) and entry.get("batch") == "batch-00"
    }
    if batch_00 != PILOT_SLUGS:
        findings.append(
            _inventory_finding(
                "inventory-batch-membership",
                "inventory.json",
                "batch-00 membership does not match the fixed Phase 1 pilot.",
            )
        )
    return findings


def _findings_have_errors(findings: Iterable[Finding]) -> bool:
    return any(finding.severity == "error" for finding in findings)


def _print_findings(findings: Sequence[Finding]) -> None:
    print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))


def _inventory(root: Path) -> tuple[dict, dict[str, NoteRecord]]:
    records = [parse_note(path) for path in sorted(root.rglob("*.md"), key=lambda item: item.as_posix())]
    nr_records = [record for record in records if record.in_scope]
    report = {
        "schemaVersion": 1,
        "scope": "NR",
        "generatedFrom": "vault/concepts",
        "notes": [
            {
                "slug": record.slug,
                "path": (Path("vault/concepts") / record.path.name).as_posix(),
                "type": NOTE_TYPE_OVERRIDES.get(record.slug, "unknown"),
                "batch": "batch-00" if record.slug in PILOT_SLUGS else "unassigned",
                "status": "pending",
                "sourceStatus": "existing-sufficient",
                "originalSha256": record.sha256,
                "summaryHeadings": [section.heading for section in record.summaries],
            }
            for record in sorted(nr_records, key=lambda item: item.slug)
        ],
    }
    normalized_records = {
        record.slug: NoteRecord(
            path=Path("vault/concepts") / record.path.name,
            slug=record.slug,
            subspecialties=record.subspecialties,
            summaries=record.summaries,
            original_summary=record.original_summary,
            footnote_refs=record.footnote_refs,
            footnote_defs=record.footnote_defs,
            sha256=record.sha256,
        )
        for record in nr_records
    }
    return report, normalized_records


def _inventory_counts(report: dict) -> tuple[int, int, int, int, int]:
    entries = report.get("notes", [])
    slugs = [entry.get("slug") for entry in entries if isinstance(entry, dict)]
    duplicates = len(slugs) - len(set(slugs))
    unclassified = sum(
        1 for entry in entries if not isinstance(entry, dict) or entry.get("type") not in NOTE_TYPES
    )
    batch_00 = sum(
        1 for entry in entries if isinstance(entry, dict) and entry.get("batch") == "batch-00"
    )
    unassigned = sum(
        1 for entry in entries if isinstance(entry, dict) and entry.get("batch") == "unassigned"
    )
    return len(entries), duplicates, unclassified, batch_00, unassigned


def _print_inventory_counts(report: dict) -> None:
    total, duplicates, unclassified, batch_00, unassigned = _inventory_counts(report)
    print(f"NR notes: {total}")
    print(f"Duplicate slugs: {duplicates}")
    print(f"Unclassified: {unclassified}")
    print(f"Batch 00: {batch_00}")
    print(f"Unassigned: {unassigned}")


def _load_batch_notes(report_path: Path) -> tuple[dict[str, NoteRecord], list[Finding]]:
    """Load the fixed pilot notes through the checked-in sibling inventory."""
    inventory_path = report_path.with_name("inventory.json")
    batch_path = report_path.as_posix()
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return {}, [
            Finding(
                "error",
                "evidence-inventory-unreadable",
                batch_path,
                f"Cannot read batch inventory: {error}.",
            )
        ]

    entries = inventory.get("notes") if isinstance(inventory, dict) else None
    if not isinstance(entries, list):
        return {}, [
            Finding(
                "error",
                "evidence-inventory-schema",
                inventory_path.as_posix(),
                "Inventory notes must be an array.",
            )
        ]
    pilot_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("batch") == "batch-00"
        and entry.get("slug") in PILOT_SLUGS
        and isinstance(entry.get("path"), str)
    ]
    if {entry["slug"] for entry in pilot_entries} != PILOT_SLUGS:
        return {}, [
            Finding(
                "error",
                "evidence-inventory-membership",
                inventory_path.as_posix(),
                "Inventory does not define the exact fixed pilot membership.",
            )
        ]

    repo_root: Path | None = None
    for candidate in report_path.resolve().parents:
        if all((candidate / entry["path"]).is_file() for entry in pilot_entries):
            repo_root = candidate
            break
    if repo_root is None:
        return {}, [
            Finding(
                "error",
                "evidence-note-missing",
                batch_path,
                "Could not resolve every pilot note path from the inventory.",
            )
        ]

    notes: dict[str, NoteRecord] = {}
    findings: list[Finding] = []
    for entry in pilot_entries:
        note_path = repo_root / entry["path"]
        try:
            notes[entry["slug"]] = parse_note(note_path)
        except (OSError, UnicodeDecodeError) as error:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-unreadable",
                    note_path.as_posix(),
                    f"Cannot read pilot note: {error}.",
                )
            )
    return notes, findings


def _pending_fact_findings(report: dict) -> list[Finding]:
    """Reject pending facts unless the caller explicitly accepts a baseline."""
    findings: list[Finding] = []
    report_notes = report.get("notes", []) if isinstance(report, dict) else []
    if not isinstance(report_notes, list):
        return findings
    for entry in report_notes:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug", "<batch>")
        facts = entry.get("factUnits", [])
        if not isinstance(facts, list):
            continue
        for fact in facts:
            if isinstance(fact, dict) and fact.get("disposition") == "pending":
                findings.append(
                    Finding(
                        "error",
                        "fact-pending",
                        str(slug),
                        f"Fact unit {fact.get('id', '<unknown>')!r} is still pending.",
                    )
                )
    return findings


def _print_batch_counts(report: dict, findings: Sequence[Finding]) -> None:
    report_notes = report.get("notes", []) if isinstance(report, dict) else []
    note_count = len(report_notes) if isinstance(report_notes, list) else 0
    missing_sources = sum(
        finding.code in {"fact-source-missing", "fact-source-undefined"}
        for finding in findings
    )
    print(f"Batch notes: {note_count}")
    print(f"Missing sources: {missing_sources}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit NR concept Summary structure.")
    commands = parser.add_subparsers(dest="command", required=True)

    inventory = commands.add_parser("inventory", help="Write a deterministic NR concept inventory.")
    inventory.add_argument("--root", type=Path, required=True)
    inventory.add_argument("--output", type=Path, required=True)
    inventory.add_argument(
        "--check",
        action="store_true",
        help="Validate the existing output against a freshly generated inventory.",
    )

    validate_note = commands.add_parser("validate-note", help="Validate one concept note.")
    validate_note.add_argument("path", type=Path)

    validate_batch = commands.add_parser(
        "validate-batch", help="Validate a source-mapped batch evidence report."
    )
    validate_batch.add_argument("path", type=Path)
    validate_batch.add_argument(
        "--allow-pending",
        action="store_true",
        help="Permit pending fact dispositions in a pre-edit baseline.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inventory":
        expected, notes = _inventory(args.root)
        if args.check:
            if not args.output.is_file():
                print(f"Inventory output does not exist: {args.output}")
                return 1
            report = json.loads(args.output.read_text(encoding="utf-8"))
            findings = validate_inventory_against_notes(report, notes)
            if report != expected:
                findings.append(
                    _inventory_finding(
                        "inventory-not-deterministic",
                        args.output.as_posix(),
                        "Existing inventory differs from deterministic generation.",
                    )
                )
            _print_inventory_counts(report)
            if findings:
                _print_findings(findings)
            return 1 if _findings_have_errors(findings) else 0
        report = expected
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _print_inventory_counts(report)
        return 0
    if args.command == "validate-note":
        findings = validate_summary(parse_note(args.path))
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    if args.command == "validate-batch":
        try:
            report = json.loads(args.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            _print_findings(
                [
                    Finding(
                        "error",
                        "evidence-json-invalid",
                        args.path.as_posix(),
                        f"Cannot read batch evidence JSON: {error}.",
                    )
                ]
            )
            return 1
        notes, findings = _load_batch_notes(args.path)
        findings.extend(validate_evidence(report, notes))
        if not args.allow_pending:
            findings.extend(_pending_fact_findings(report))
        _print_batch_counts(report, findings)
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
