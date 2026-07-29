"""Deterministic structural checks for NR concept-note Summary sections.

This module intentionally audits Markdown and evidence metadata only.  It does
not synthesize or rewrite medical content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from urllib.parse import urlparse


FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SUMMARY_HEADING_RE = re.compile(r"^##\s+Summary(?:\s+\u2014\s+\S.*)?\s*$")
LEVEL_TWO_HEADING_RE = re.compile(r"^##(?:\s|$)")
LEVEL_THREE_HEADING_RE = re.compile(r"^###\s+\S.*$")
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
SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PHASE2_RUN_ID_RE = re.compile(r"^/root(?:/[a-z0-9_]+)+$")

NOTE_TYPES = {"disease", "pattern-ddx", "anatomy-measurement-management"}
NOTE_STATUSES = {
    "pending",
    "scheduled-not-started",
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
BATCH_STATUSES = {"baseline", "needs-review", "verified"}
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
EXPECTED_NR_NOTE_COUNT = 216
EXPECTED_BATCH_00_COUNT = 10
EXPECTED_UNASSIGNED_COUNT = 206
EXPECTED_GENERATED_CONCEPT_COUNT = 978
EXPECTED_MANUAL_REVIEW_FACT_IDS = frozenset(
    {
        "acute-stroke-management-f09",
        "bilateral-subcortical-dwi-hyperintensity-ddx-f08",
        "bilateral-subcortical-dwi-hyperintensity-ddx-f09",
        "bilateral-subcortical-dwi-hyperintensity-ddx-f12",
    }
)
EXPECTED_LINT_ERRORS = (
    "[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義",
    "[json 殘留 ![[...]]] 2022-264",
)
EXPECTED_LINT_WARNING_COUNT = 124
REQUIRED_EXACT_DOI_URLS = (
    "https://doi.org/10.6705/j.jacme.202103_11(1).0002",
    "https://doi.org/10.1016/S0140-6736(00)02237-6",
)
GENERATED_INDEX_FIELDS = ("slug", "name", "nameZh", "subspecialty", "checked")
# Keep this explicit and empty unless a reviewed legacy index-only concept is
# intentionally supported. Every other index entry must have a detail JSON.
LEGACY_INDEX_DETAIL_FALLBACKS: dict[str, dict[str, object]] = {}

ACTIVE_PHASE2A_BATCHES = {
    "batch-01-anatomy": {
        "type": "anatomy-measurement-management",
        "slugs": (
            "ajcc-8th-head-neck-n-staging",
            "aneurysm-coiling-recurrence",
            "atlantodental-interval",
            "brachial-plexus-anatomy",
            "brain-herniation-syndromes",
            "carotid-vertebrobasilar-anastomoses",
            "cerebral-border-zone-infarct-arteries",
            "cerebral-deep-venous-cortex",
            "cerebral-herniation-types",
            "cerebral-infarction-evolution",
        ),
    },
    "batch-02-disease": {
        "type": "disease",
        "slugs": (
            "2-hydroxyglutarate-idh-mutant-glioma",
            "adrenoleukodystrophy",
            "aicardi-syndrome",
            "als-imaging",
            "angioinvasive-aspergillosis",
            "anti-nmda-encephalitis",
            "arterial-dissection-mri",
            "atypical-teratoid-rhabdoid-tumor",
            "autoimmune-encephalitis",
            "basilar-artery-occlusion",
        ),
    },
    "batch-03-pattern": {
        "type": "pattern-ddx",
        "slugs": (
            "brain-tumor-imaging",
            "cerebral-infarction-fogging",
            "cerebral-microbleeds",
            "cerebrovascular-malformations",
            "chemical-shift-artifact",
            "cns-opportunistic-infection",
            "cranial-nerve-muscle-atrophy",
            "dural-based-masses-aids",
            "facial-fracture-complications",
            "gbm-vs-pcnsl",
        ),
    },
}
PHASE2_TYPE_ORDER = (
    "anatomy-measurement-management",
    "disease",
    "pattern-ddx",
)
PHASE2_TYPE_SHORT = {
    "anatomy-measurement-management": "anatomy",
    "disease": "disease",
    "pattern-ddx": "pattern",
}
# Populated one reviewed batch at a time by Tasks 2.1, 3.1, and 4.1.  Absence
# is fail-closed: no mutable lock or evidence file may choose its own digest.
TRUSTED_PHASE2A_BATCH_LOCK_SHA256: Mapping[str, str] = {
    "batch-01-anatomy": (
        "1ba97cdc318b16deaf60cc768dc4b7424f01759287c91e43c85bd6c1601b0b64"
    ),
}
# Sealed one reviewed batch at a time after the gated two-run build workflow.
# Task 1.1 intentionally leaves this empty so generated observations cannot
# self-authorize before Tasks 2.3, 3.3, and 4.3 independently review them.
TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256: Mapping[str, str] = {}

# Reviewed trust roots are deliberately stored in code, outside mutable batch
# evidence.  Task 3 provenance: commit 8dca155, batch blob
# 650229dda33a31dfc816f54418db394356d47dc5.  Task 4 research added only the
# source references listed below; originalSummary, fact IDs, and fact texts
# remain byte-for-byte equivalent to that Task 3 baseline.
TRUSTED_TASK3_BASELINE_EVIDENCE_SHA256 = (
    "c4eee7a9869f944b7bb1481e018999eef30013c47deb023efaa3cfac055ba071"
)
TRUSTED_REVIEWED_BASELINE_EVIDENCE_SHA256 = (
    "b2cff4944bf07fa9eb99eaf0ba183bd79d397d528b4d9b7199f9ba576e20d1fe"
)
TRUSTED_FINAL_SUMMARY_BULLET_EVIDENCE_SHA256 = (
    "b632ffec59156e3b25c2d011daeb1a0c42dd09dd90449d058d5974e8de343412"
)
# Final-review trust root. Unlike the mutable self-digests, this reviewed seal
# covers the root/note statuses, every fact disposition, exact manual queue,
# complete rewritten Summary spans, validation counters, bullet evidence, and
# phase1Verification (including lint and generated manifest). Updating it is
# intentionally expensive: review all 10 Summary spans and fact mappings,
# reproduce lint/build outputs, regenerate the manifest, then update the
# regression fixtures and this digest in the same reviewed commit.
TRUSTED_FINAL_REVIEW_EVIDENCE_SHA256 = (
    "3b1d6be11cca13682cea9b2e7dcbd99ec8f838d51cb9dae46f66e48f1be968d3"
)
# Reviewed pre-edit pilot hashes from the accepted Phase 1 baseline.  This
# code-owned map is deliberately independent of inventory.json and
# batch-00.json: neither mutable evidence file may choose its expected value.
TRUSTED_PILOT_ORIGINAL_SHA256 = {
    "acute-stroke-management": "e12b6ea4ff0198ccd081f7089550a1242bcb9b6c3041eb7651a629444f3a981b",
    "artery-of-adamkiewicz": "e55ed8842ab70e3c442bc92a8d4f7608ab919a11aadf49684dae9e815008a811",
    "aspects-score": "f7cfdb3fe6ebdb0a07e5d2b42088e0fab0bde33d2b2391892a8c7de87d79f0d9",
    "basal-ganglia-t1-shortening": "df599c23d02c903b62e7233c63cd782f88f3fabba8f359852505f1f2391ab434",
    "bilateral-subcortical-dwi-hyperintensity-ddx": "3bcefabc671edaa9fa251662af8b52d464fc43448574c4fd7e0cb367d6cf4376",
    "cerebral-amyloid-angiopathy": "582f7b34b43571b22c33d8a99409c066abff8b6b0f6e5e85a014cdf38225ef3e",
    "clippers": "f35fe0aff8da041a9dd09e0dcdb7d6af59f2681e02c46c43377e98c01d6f773e",
    "cpa-masses": "ad70bfd0e00ce2c0ead8699dcbdc19f884a9d79c9cfe4bb7bb9eb3bba04da41e",
    "craniopharyngioma": "bfca1e1633b23dd8cf95e5d76f99ce9849090c7cab7045dd532cc0199ce83cd1",
    "dementia-neuroimaging-overview": "4119c8b7cfd2c770a1d7975e0f586a6f693d50b9171421e8c1d3652f6c08687a",
}
TRUSTED_TASK4_SOURCE_REF_ADDITIONS = {
    "artery-of-adamkiewicz-f05": frozenset({"8"}),
    "artery-of-adamkiewicz-f09": frozenset({"9"}),
    "aspects-score-f24": frozenset({"9"}),
    "aspects-score-f25": frozenset({"9"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f04": frozenset({"6", "10"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f05": frozenset({"6"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f06": frozenset({"6"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f07": frozenset({"7"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f08": frozenset({"7"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f09": frozenset({"8", "9"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f10": frozenset({"8"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f11": frozenset({"8"}),
    "bilateral-subcortical-dwi-hyperintensity-ddx-f12": frozenset({"8", "9"}),
    "cerebral-amyloid-angiopathy-f10": frozenset({"9"}),
    "cpa-masses-f01": frozenset({"6"}),
    "cpa-masses-f06": frozenset({"6"}),
    "cpa-masses-f12": frozenset({"6"}),
    "cpa-masses-f16": frozenset({"6"}),
}

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


def _is_string_member(value: object, allowed: set[str] | frozenset[str]) -> bool:
    """Return enum membership without hashing untrusted JSON containers."""
    return isinstance(value, str) and value in allowed


def _is_inventory_batch(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if value in PHASE_1_BATCHES or value in ACTIVE_PHASE2A_BATCHES:
        return True
    return re.fullmatch(
        r"scheduled-(?:anatomy|disease|pattern)-[0-9]{2}", value
    ) is not None


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


@dataclass(frozen=True)
class BatchContext:
    repo_root: Path
    inventory_path: Path
    assignment_path: Path
    assignment: dict
    batch: dict
    baseline_path: Path
    baseline: dict | None
    evidence_path: Path
    evidence: dict | None
    note_records: Mapping[str, NoteRecord]
    generated_root: Path


@dataclass(frozen=True)
class Phase2GeneratedState:
    manifest_path: str
    checked: dict
    historical_hashes: Mapping[str, str]
    current_hashes: Mapping[str, str]
    actual: dict


class Phase2LoadError(ValueError):
    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def finding(self) -> Finding:
        return Finding("error", self.code, self.path, self.message)


def _phase2_path_parts(value: object) -> tuple[str, ...] | None:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
    ):
        return None
    parts = tuple(value.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return parts


def _resolve_phase2_path(repo_root: Path, value: str, *, display_path: str) -> Path:
    parts = _phase2_path_parts(value)
    if parts is None:
        raise Phase2LoadError(
            "phase2-path-invalid",
            display_path,
            "Path must be a repo-relative POSIX path without dot components.",
        )
    root = repo_root.resolve()
    resolved = (root / Path(*parts)).resolve()
    if not resolved.is_relative_to(root):
        raise Phase2LoadError(
            "phase2-path-invalid",
            display_path,
            "Path resolves outside the repository root.",
        )
    return resolved


def _phase2_inventory_projection(inventory: dict) -> list[dict]:
    notes = inventory.get("notes")
    if not isinstance(notes, list):
        raise ValueError("Inventory notes must be an array.")
    slugs = [
        entry.get("slug")
        for entry in notes
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    ]
    pilot_slugs = [slug for slug in slugs if slug in PILOT_SLUGS]
    if (
        len(notes) != EXPECTED_NR_NOTE_COUNT
        or len(slugs) != EXPECTED_NR_NOTE_COUNT
        or len(set(slugs)) != EXPECTED_NR_NOTE_COUNT
        or len(pilot_slugs) != EXPECTED_BATCH_00_COUNT
        or set(pilot_slugs) != PILOT_SLUGS
    ):
        raise ValueError(
            "Inventory must contain exactly 216 globally unique slugs and "
            "each immutable pilot exactly once."
        )
    projection = []
    for entry in notes:
        if not isinstance(entry, dict) or entry.get("slug") in PILOT_SLUGS:
            continue
        projection.append(
            {
                "slug": entry.get("slug"),
                "path": entry.get("path"),
                "type": entry.get("type"),
                "originalSha256": entry.get("originalSha256"),
                "summaryHeadings": entry.get("summaryHeadings"),
            }
        )
    return sorted(projection, key=lambda entry: str(entry.get("slug")))


def build_phase2_assignment(inventory: dict) -> dict:
    """Deterministically assign all non-pilot NR notes without path inference."""
    projection = _phase2_inventory_projection(inventory)
    by_slug: dict[str, dict] = {}
    for entry in projection:
        slug = entry.get("slug")
        note_type = entry.get("type")
        if (
            not isinstance(slug, str)
            or not SAFE_SLUG_RE.fullmatch(slug)
            or slug in by_slug
            or note_type not in NOTE_TYPES
            or _phase2_path_parts(entry.get("path")) is None
        ):
            raise ValueError("Inventory cannot produce a deterministic Phase 2 assignment.")
        by_slug[slug] = entry
    if len(by_slug) != EXPECTED_UNASSIGNED_COUNT:
        raise ValueError("Phase 2 assignment requires exactly 206 non-pilot notes.")

    active_slugs: set[str] = set()
    batches = []
    ordinal = 1
    for batch_id, contract in ACTIVE_PHASE2A_BATCHES.items():
        slugs = list(contract["slugs"])
        if any(
            slug not in by_slug or by_slug[slug]["type"] != contract["type"]
            for slug in slugs
        ):
            raise ValueError(f"Inventory does not contain fixed active batch {batch_id}.")
        active_slugs.update(slugs)
        batches.append(
            {
                "id": batch_id,
                "ordinal": ordinal,
                "type": contract["type"],
                "state": "active",
                "slugs": slugs,
            }
        )
        ordinal += 1

    for note_type in PHASE2_TYPE_ORDER:
        remaining = sorted(
            slug
            for slug, entry in by_slug.items()
            if entry["type"] == note_type and slug not in active_slugs
        )
        for offset in range(0, len(remaining), 10):
            type_ordinal = offset // 10 + 1
            batches.append(
                {
                    "id": (
                        f"scheduled-{PHASE2_TYPE_SHORT[note_type]}-"
                        f"{type_ordinal:02d}"
                    ),
                    "ordinal": ordinal,
                    "type": note_type,
                    "state": "scheduled",
                    "slugs": remaining[offset : offset + 10],
                }
            )
            ordinal += 1
    return {
        "schemaVersion": 1,
        "scope": "NR",
        "phase": "2",
        "sourceInventorySha256": _canonical_sha256(projection),
        "batchSize": 10,
        "activeBatchIds": list(ACTIVE_PHASE2A_BATCHES),
        "batches": batches,
    }


def build_phase2_assignment_bytes(inventory: dict) -> bytes:
    """Return deterministic checked-file bytes for an inventory-derived assignment."""
    assignment = build_phase2_assignment(inventory)
    return (
        json.dumps(assignment, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def synchronize_phase2_inventory(inventory: dict, assignment: dict) -> dict:
    """Return an inventory copy synchronized to a deterministic assignment."""
    expected = build_phase2_assignment(inventory)
    if assignment != expected:
        raise ValueError("Assignment must equal deterministic inventory regeneration.")
    batch_by_slug = {
        slug: batch["id"]
        for batch in assignment["batches"]
        for slug in batch["slugs"]
    }
    synchronized = deepcopy(inventory)
    for entry in synchronized["notes"]:
        slug = entry["slug"]
        if slug in PILOT_SLUGS:
            continue
        entry["batch"] = batch_by_slug[slug]
        entry["status"] = "scheduled-not-started"
    return synchronized


def phase2_assignment_counts(assignment: dict, inventory: dict) -> dict[str, int]:
    """Summarize the checked assignment/inventory arithmetic."""
    inventory_notes = inventory.get("notes", []) if isinstance(inventory, dict) else []
    batches = assignment.get("batches", []) if isinstance(assignment, dict) else []
    pilot = sum(
        isinstance(entry, dict) and entry.get("slug") in PILOT_SLUGS
        for entry in inventory_notes
    )
    active = sum(
        len(batch.get("slugs", []))
        for batch in batches
        if isinstance(batch, dict) and batch.get("state") == "active"
    )
    scheduled = sum(
        len(batch.get("slugs", []))
        for batch in batches
        if isinstance(batch, dict) and batch.get("state") == "scheduled"
    )
    return {
        "total": len(inventory_notes),
        "pilot": pilot,
        "nonPilot": active + scheduled,
        "active": active,
        "scheduled": scheduled,
    }


def _print_phase2_assignment_counts(assignment: dict, inventory: dict) -> None:
    counts = phase2_assignment_counts(assignment, inventory)
    print(f"NR total: {counts['total']}")
    print(f"Phase 1 pilots: {counts['pilot']}")
    print(f"Phase 2 non-pilots: {counts['nonPilot']}")
    print(f"Phase 2A active: {counts['active']}")
    print(f"Scheduled: {counts['scheduled']}")


def validate_phase2_assignment(assignment: dict, inventory: dict) -> list[Finding]:
    """Return stable assignment findings without consulting cwd or checkout identity."""
    findings: list[Finding] = []
    assignment_path = "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    inventory_notes = inventory.get("notes") if isinstance(inventory, dict) else None
    if isinstance(inventory_notes, list):
        inventory_slugs = [
            entry.get("slug")
            for entry in inventory_notes
            if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
        ]
        pilot_occurrences = [
            slug for slug in inventory_slugs if slug in PILOT_SLUGS
        ]
        if (
            len(inventory_notes) != EXPECTED_NR_NOTE_COUNT
            or len(inventory_slugs) != EXPECTED_NR_NOTE_COUNT
            or len(set(inventory_slugs)) != EXPECTED_NR_NOTE_COUNT
            or len(pilot_occurrences) != EXPECTED_BATCH_00_COUNT
            or set(pilot_occurrences) != PILOT_SLUGS
        ):
            findings.append(
                Finding(
                    "error",
                    "phase2-assignment-membership",
                    "docs/reports/nr-summary-rewrite/inventory.json",
                    "Inventory must have 216 unique slugs and each pilot exactly once.",
                )
            )
        batch_00_slugs = {
            entry.get("slug")
            for entry in inventory_notes
            if isinstance(entry, dict) and entry.get("batch") == "batch-00"
        }
        if batch_00_slugs != PILOT_SLUGS:
            findings.append(
                Finding(
                    "error",
                    "phase2-assignment-membership",
                    "docs/reports/nr-summary-rewrite/inventory.json",
                    "Inventory batch-00 membership must equal immutable PILOT_SLUGS.",
                )
            )
        for index, entry in enumerate(inventory_notes):
            if (
                isinstance(entry, dict)
                and _phase2_path_parts(entry.get("path")) is None
            ):
                findings.append(
                    Finding(
                        "error",
                        "phase2-path-invalid",
                        f"docs/reports/nr-summary-rewrite/inventory.json#notes/{index}",
                        "Inventory note path must be repo-relative POSIX.",
                    )
                )
    try:
        expected = build_phase2_assignment(inventory)
    except (TypeError, ValueError) as error:
        findings.append(
            Finding(
                "error",
                "phase2-assignment-inventory-mismatch",
                "docs/reports/nr-summary-rewrite/inventory.json",
                str(error),
            )
        )
        return findings
    if not isinstance(assignment, dict):
        return findings + [
            Finding(
                "error",
                "phase2-assignment-membership",
                assignment_path,
                "Assignment root must be an object.",
            )
        ]
    if assignment.get("sourceInventorySha256") != expected["sourceInventorySha256"]:
        findings.append(
            Finding(
                "error",
                "phase2-assignment-inventory-mismatch",
                assignment_path,
                "Assignment inventory projection digest does not match inventory.",
            )
        )

    expected_batch_by_slug = {
        slug: batch["id"]
        for batch in expected["batches"]
        for slug in batch["slugs"]
    }
    if isinstance(inventory_notes, list):
        inventory_synchronized = all(
            not isinstance(entry, dict)
            or entry.get("slug") in PILOT_SLUGS
            or (
                entry.get("batch") == expected_batch_by_slug.get(entry.get("slug"))
                and entry.get("status") == "scheduled-not-started"
            )
            for entry in inventory_notes
        )
        if not inventory_synchronized:
            findings.append(
                Finding(
                    "error",
                    "phase2-assignment-inventory-mismatch",
                    "docs/reports/nr-summary-rewrite/inventory.json",
                    "Non-pilot inventory batch/status must match the checked assignment.",
                )
            )

    batches = assignment.get("batches")
    membership_ok = isinstance(batches, list)
    flattened: list[str] = []
    batch_by_id = {}
    inventory_type_by_slug = {
        entry["slug"]: entry["type"]
        for entry in _phase2_inventory_projection(inventory)
    }
    if isinstance(batches, list):
        for batch in batches:
            if not isinstance(batch, dict) or not isinstance(batch.get("id"), str):
                membership_ok = False
                continue
            batch_by_id[batch["id"]] = batch
            slugs = batch.get("slugs")
            if not isinstance(slugs, list) or not all(
                isinstance(slug, str) for slug in slugs
            ):
                membership_ok = False
                continue
            declared_type = batch.get("type")
            if not isinstance(declared_type, str) or any(
                inventory_type_by_slug.get(slug) != declared_type
                for slug in slugs
            ):
                membership_ok = False
            flattened.extend(slugs)
        expected_slugs = [
            entry["slug"] for entry in _phase2_inventory_projection(inventory)
        ]
        membership_ok = (
            membership_ok
            and len(flattened) == len(set(flattened)) == EXPECTED_UNASSIGNED_COUNT
            and set(flattened) == set(expected_slugs)
        )
        for batch_id, contract in ACTIVE_PHASE2A_BATCHES.items():
            actual = batch_by_id.get(batch_id)
            membership_ok = membership_ok and bool(
                isinstance(actual, dict)
                and actual.get("type") == contract["type"]
                and actual.get("state") == "active"
                and actual.get("slugs") == list(contract["slugs"])
            )
    if not membership_ok:
        findings.append(
            Finding(
                "error",
                "phase2-assignment-membership",
                assignment_path,
                "Assignment membership is incomplete, duplicated, or not the fixed tranche.",
            )
        )
    if assignment != expected:
        findings.append(
            Finding(
                "error",
                "phase2-assignment-nondeterministic",
                assignment_path,
                "Assignment differs from deterministic regeneration.",
            )
        )
    return findings


def _read_phase2_json(path: Path, display: Path, *, missing_ok: bool = False) -> dict | None:
    if missing_ok and not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise Phase2LoadError(
            "phase2-baseline-missing",
            display.as_posix(),
            "Required Phase 2 file is missing.",
        ) from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Phase2LoadError(
            "phase2-baseline-schema",
            display.as_posix(),
            f"Cannot read Phase 2 JSON: {error}.",
        ) from error
    if not isinstance(value, dict):
        raise Phase2LoadError(
            "phase2-baseline-schema",
            display.as_posix(),
            "Phase 2 JSON root must be an object.",
        )
    return value


def load_phase2_batch(
    repo_root: Path, assignment_path: Path, batch_id: str
) -> BatchContext:
    """Load one batch only through explicit, repo-relative paths."""
    root = repo_root.resolve()
    display_assignment = assignment_path.as_posix()
    if assignment_path.is_absolute():
        raise Phase2LoadError(
            "phase2-path-invalid",
            "phase2-assignment.json",
            "Assignment path must be repo-relative.",
        )
    assignment_file = _resolve_phase2_path(
        root, display_assignment, display_path="phase2-assignment.json"
    )
    inventory_path = assignment_path.with_name("inventory.json")
    inventory_file = _resolve_phase2_path(
        root, inventory_path.as_posix(), display_path=inventory_path.as_posix()
    )
    assignment = _read_phase2_json(assignment_file, assignment_path)
    inventory = _read_phase2_json(inventory_file, inventory_path)
    assert assignment is not None and inventory is not None
    assignment_findings = validate_phase2_assignment(assignment, inventory)
    if assignment_findings:
        first = assignment_findings[0]
        raise Phase2LoadError(first.code, first.path, first.message)
    if not isinstance(batch_id, str) or not SAFE_SLUG_RE.fullmatch(batch_id):
        raise Phase2LoadError(
            "phase2-assignment-membership",
            assignment_path.as_posix(),
            "Batch id is unsafe.",
        )
    batch = next(
        (
            candidate
            for candidate in assignment["batches"]
            if isinstance(candidate, dict) and candidate.get("id") == batch_id
        ),
        None,
    )
    if batch is None or batch.get("state") != "active":
        raise Phase2LoadError(
            "phase2-assignment-membership",
            assignment_path.as_posix(),
            f"Unknown or inactive batch {batch_id!r}.",
        )

    report_root = assignment_path.parent
    baseline_path = (
        report_root / "phase2a" / "baselines" / f"{batch_id}.json"
    )
    evidence_path = report_root / "phase2a" / "evidence" / f"{batch_id}.json"
    baseline_file = _resolve_phase2_path(
        root, baseline_path.as_posix(), display_path=baseline_path.as_posix()
    )
    evidence_file = _resolve_phase2_path(
        root, evidence_path.as_posix(), display_path=evidence_path.as_posix()
    )
    baseline = _read_phase2_json(baseline_file, baseline_path, missing_ok=True)
    evidence = _read_phase2_json(evidence_file, evidence_path, missing_ok=True)
    entries = {
        entry["slug"]: entry
        for entry in inventory["notes"]
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    note_records: dict[str, NoteRecord] = {}
    for slug in batch["slugs"]:
        entry = entries.get(slug)
        if not isinstance(entry, dict):
            raise Phase2LoadError(
                "phase2-baseline-inventory-mismatch",
                inventory_path.as_posix(),
                f"Inventory is missing selected slug {slug!r}.",
            )
        note_file = _resolve_phase2_path(
            root, entry.get("path"), display_path=inventory_path.as_posix()
        )
        try:
            note = parse_note(note_file)
        except (OSError, UnicodeDecodeError) as error:
            raise Phase2LoadError(
                "phase2-baseline-inventory-mismatch",
                entry["path"],
                f"Cannot read selected source note {slug!r}: {error}.",
            ) from error
        note_records[slug] = replace(note, path=Path(entry["path"]))
    return BatchContext(
        repo_root=root,
        inventory_path=inventory_path,
        assignment_path=assignment_path,
        assignment=assignment,
        batch=batch,
        baseline_path=baseline_path,
        baseline=baseline,
        evidence_path=evidence_path,
        evidence=evidence,
        note_records=note_records,
        generated_root=Path("data/concepts"),
    )


def _ordered_footnote_refs(text: str) -> list[str]:
    """Return unique Obsidian footnote ids in source order."""
    refs: list[str] = []
    for match in FOOTNOTE_REFERENCE_RE.finditer(text):
        ref = match.group("id")
        if ref not in refs:
            refs.append(ref)
    return refs


def _phase2_statement_body(source_statement: str) -> str:
    """Return source-language fact text without list/quote markup or footnotes."""
    value = source_statement.strip()
    value = re.sub(r"^>\s*", "", value)
    value = re.sub(r"^[-*+]\s+", "", value)
    value = FOOTNOTE_REFERENCE_RE.sub("", value)
    value = value.replace("**", "")
    return value.strip()


def _phase2_fact_segments(source_statement: str) -> list[str]:
    """Split exact source wording at top-level sentence/semicolon boundaries."""
    value = _phase2_statement_body(source_statement)
    segments: list[str] = []
    start = 0
    depth = 0
    opening = {"(": ")", "（": "）", "[": "]", "【": "】"}
    closing = set(opening.values())
    for index, character in enumerate(value):
        if character in opening:
            depth += 1
        elif character in closing and depth:
            depth -= 1
        elif depth == 0 and character in {";", "；", "。"}:
            segment = value[start : index + 1].strip()
            if segment:
                segments.append(segment)
            start = index + 1
    tail = value[start:].strip()
    if tail:
        segments.append(tail)
    return segments


def phase2_summary_source_statements(note: NoteRecord) -> list[dict]:
    """Extract exact factual Summary lines and their explicit/enclosing sources."""
    statements: list[dict] = []
    for section in note.summaries:
        enclosing_refs: list[str] = []
        for source_line in section.content.splitlines():
            stripped = source_line.strip()
            if (
                not stripped
                or LEVEL_THREE_HEADING_RE.match(stripped)
                or CALLOUT_RE.match(source_line)
            ):
                continue
            explicit_refs = _ordered_footnote_refs(source_line)
            is_top_level = TOP_LEVEL_BULLET_RE.match(source_line) is not None
            is_nested = NESTED_BULLET_RE.match(source_line) is not None
            if is_top_level:
                enclosing_refs = explicit_refs
            refs = explicit_refs or (enclosing_refs if is_nested else [])
            body_without_refs = FOOTNOTE_REFERENCE_RE.sub("", stripped).strip()
            if re.fullmatch(
                r"(?:>\s*)?(?:[-*+]\s+)?\*\*[^*]+\*\*[:\uFF1A]\s*",
                body_without_refs,
            ):
                continue
            if not _phase2_statement_body(source_line):
                continue
            statements.append(
                {
                    "text": source_line,
                    "sourceRefs": list(refs),
                }
            )
    return statements


def phase2_default_fact_templates(note: NoteRecord) -> list[dict]:
    """Derive conservative source-exact fact units from audited Summary lines."""
    facts: list[dict] = []
    for statement in phase2_summary_source_statements(note):
        for text in _phase2_fact_segments(statement["text"]):
            facts.append(
                {
                    "text": text,
                    "sourceStatement": statement["text"],
                    "sourceRefs": list(statement["sourceRefs"]),
                }
            )
    return facts


def build_phase2_baseline_lock(
    context: BatchContext,
    fact_templates_by_slug: Mapping[str, Sequence[Mapping[str, object]]] | None = None,
) -> dict:
    """Build deterministic pre-edit lock data from the loaded source checkout."""
    inventory_file = context.repo_root / context.inventory_path
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    inventory_by_slug = {
        entry["slug"]: entry
        for entry in inventory.get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    expected_slugs = list(context.batch["slugs"])
    if fact_templates_by_slug is not None and set(fact_templates_by_slug) != set(
        expected_slugs
    ):
        raise ValueError("Fact templates must exactly match selected batch membership.")

    notes = []
    for slug in expected_slugs:
        note = context.note_records.get(slug)
        inventory_entry = inventory_by_slug.get(slug)
        if note is None or not isinstance(inventory_entry, dict):
            raise ValueError(f"Missing selected source or inventory entry for {slug!r}.")
        headings = [section.heading for section in note.summaries]
        if any(
            (
                inventory_entry.get("path") != note.path.as_posix(),
                inventory_entry.get("type") != context.batch.get("type"),
                inventory_entry.get("originalSha256") != note.sha256,
                inventory_entry.get("summaryHeadings") != headings,
            )
        ):
            raise ValueError(
                f"Current source metadata for {slug!r} differs from inventory."
            )
        expected_templates = phase2_default_fact_templates(note)
        supplied_templates = (
            expected_templates
            if fact_templates_by_slug is None
            else [
                {
                    "text": item.get("text"),
                    "sourceStatement": item.get("sourceStatement"),
                    "sourceRefs": item.get("sourceRefs"),
                }
                for item in fact_templates_by_slug[slug]
                if isinstance(item, Mapping)
            ]
        )
        if supplied_templates != expected_templates or not supplied_templates:
            raise ValueError(
                f"Fact templates for {slug!r} are not the audited source projection."
            )
        fact_units = [
            {
                "id": f"{slug}-f{index:02d}",
                "text": item["text"],
                "sourceStatement": item["sourceStatement"],
                "sourceRefs": item["sourceRefs"],
            }
            for index, item in enumerate(supplied_templates, start=1)
        ]
        notes.append(
            {
                "slug": slug,
                "path": inventory_entry["path"],
                "type": inventory_entry["type"],
                "originalSha256": note.sha256,
                "summaryHeadings": headings,
                "originalSummary": note.original_summary,
                "factUnits": fact_units,
            }
        )
    return {
        "schemaVersion": 1,
        "kind": "phase2-baseline-lock",
        "batch": context.batch["id"],
        "scope": "NR",
        "assignmentSha256": _canonical_sha256(context.assignment),
        "notes": notes,
    }


def build_phase2_baseline_lock_bytes(
    context: BatchContext,
    fact_templates_by_slug: Mapping[str, Sequence[Mapping[str, object]]] | None = None,
) -> bytes:
    """Return deterministic pretty-printed checked baseline bytes."""
    baseline = build_phase2_baseline_lock(context, fact_templates_by_slug)
    return (json.dumps(baseline, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _rendered_footnote_definitions(path: Path) -> dict[str, str]:
    """Read exact existing footnote definition bodies, including continuations."""
    lines = path.read_text(encoding="utf-8").splitlines()
    definitions: dict[str, str] = {}
    index = 0
    while index < len(lines):
        match = re.match(r"^\[\^([^\]\r\n]+)\]:\s*(.*)$", lines[index])
        if match is None:
            index += 1
            continue
        ref = match.group(1)
        citation_lines = [match.group(2)]
        index += 1
        while index < len(lines) and (
            lines[index].startswith("    ") or lines[index].startswith("\t")
        ):
            citation_lines.append(lines[index].lstrip())
            index += 1
        citation = "\n".join(citation_lines).strip()
        if citation:
            definitions[ref] = citation
    return definitions


def build_phase2_pending_evidence_scaffold(
    context: BatchContext, *, implementer: str
) -> dict:
    """Build the honest nonterminal Task 2.1 evidence scaffold."""
    if (
        not isinstance(context.baseline, dict)
        or not isinstance(implementer, str)
        or PHASE2_RUN_ID_RE.fullmatch(implementer) is None
    ):
        raise ValueError("A loaded baseline and canonical implementer are required.")
    baseline_digest = _canonical_sha256(context.baseline)
    evidence_notes = []
    for locked in context.baseline["notes"]:
        slug = locked["slug"]
        note = context.note_records[slug]
        rendered = _rendered_footnote_definitions(
            context.repo_root / note.path
        )
        referenced: list[str] = []
        for fact in locked["factUnits"]:
            for ref in fact["sourceRefs"]:
                if ref not in referenced:
                    referenced.append(ref)
        if any(ref not in rendered for ref in referenced):
            raise ValueError(f"Referenced footnote is undefined for {slug!r}.")
        evidence_notes.append(
            {
                "slug": slug,
                "status": "pending",
                "rewrittenSummary": locked["originalSummary"],
                "facts": [
                    {
                        "id": fact["id"],
                        "sourceRefs": list(fact["sourceRefs"]),
                        "disposition": "pending",
                    }
                    for fact in locked["factUnits"]
                ],
                "sourceDefinitions": {
                    ref: {
                        "kind": "existing-footnote",
                        "locator": ref,
                        "citation": rendered[ref],
                    }
                    for ref in referenced
                },
            }
        )
    batch_ids = list(ACTIVE_PHASE2A_BATCHES)
    sequence = batch_ids.index(context.batch["id"]) + 1
    return {
        "schemaVersion": 1,
        "kind": "phase2-batch-evidence",
        "batch": context.batch["id"],
        "scope": "NR",
        "baselineLock": {
            "path": context.baseline_path.as_posix(),
            "sha256": baseline_digest,
        },
        "status": "baseline",
        "workflow": {
            "sequence": sequence,
            "predecessor": batch_ids[sequence - 2] if sequence > 1 else None,
            "implementer": implementer,
            "reviewer": None,
            "reviewStatus": "not-started",
            "reviewedBaselineSha256": None,
        },
        "notes": evidence_notes,
        "manualReviewFactIds": [],
        "generatedManifest": (
            context.baseline_path.parent.parent
            / "generated"
            / f"{context.batch['id']}.json"
        ).as_posix(),
    }


def build_phase2_pending_evidence_scaffold_bytes(
    context: BatchContext, *, implementer: str
) -> bytes:
    """Return deterministic pretty-printed pending scaffold bytes."""
    evidence = build_phase2_pending_evidence_scaffold(
        context, implementer=implementer
    )
    return (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )


def _phase2_trust_registry_is_valid(context: BatchContext) -> bool:
    """Reject missing/unknown/early registry entries independently of lock data."""
    registry = TRUSTED_PHASE2A_BATCH_LOCK_SHA256
    if not isinstance(registry, Mapping):
        return False
    registered = set(registry)
    active_ids = set(ACTIVE_PHASE2A_BATCHES)
    if not registered <= active_ids:
        return False
    present_active = {
        batch_id
        for batch_id in ACTIVE_PHASE2A_BATCHES
        if (
            context.repo_root
            / context.baseline_path.parent
            / f"{batch_id}.json"
        ).is_file()
    }
    if registered != present_active:
        return False
    return all(
        isinstance(value, str) and SHA256_RE.fullmatch(value)
        for value in registry.values()
    )


def validate_baseline_lock(context: BatchContext) -> list[Finding]:
    findings: list[Finding] = []
    path = context.baseline_path.as_posix()
    baseline = context.baseline
    if baseline is None:
        return [
            Finding("error", "phase2-baseline-missing", path, "Baseline lock is missing.")
        ]
    required = {
        "schemaVersion",
        "kind",
        "batch",
        "scope",
        "assignmentSha256",
        "notes",
    }
    if (
        required - baseline.keys()
        or baseline.get("schemaVersion") != 1
        or baseline.get("kind") != "phase2-baseline-lock"
        or baseline.get("batch") != context.batch.get("id")
        or baseline.get("scope") != "NR"
        or not isinstance(baseline.get("notes"), list)
    ):
        findings.append(
            Finding(
                "error",
                "phase2-baseline-schema",
                path,
                "Baseline lock shape or identity is invalid.",
            )
        )
        return findings
    digest = _canonical_sha256(baseline)
    trusted = TRUSTED_PHASE2A_BATCH_LOCK_SHA256.get(context.batch["id"])
    if (
        not _phase2_trust_registry_is_valid(context)
        or
        not isinstance(trusted, str)
        or not SHA256_RE.fullmatch(trusted)
        or digest != trusted
    ):
        findings.append(
            Finding(
                "error",
                "phase2-trusted-batch-lock-mismatch",
                path,
                "Baseline lock does not match the code-owned batch digest.",
            )
        )
    if baseline.get("assignmentSha256") != _canonical_sha256(context.assignment):
        findings.append(
            Finding(
                "error",
                "phase2-baseline-inventory-mismatch",
                path,
                "Baseline assignment digest does not match the loaded assignment.",
            )
        )
    inventory_file = context.repo_root / context.inventory_path
    inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    inventory_by_slug = {
        entry["slug"]: entry
        for entry in inventory.get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    baseline_notes = baseline["notes"]
    baseline_by_slug = {
        entry["slug"]: entry
        for entry in baseline_notes
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    if (
        len(baseline_notes) != len(context.batch["slugs"])
        or list(baseline_by_slug) != context.batch["slugs"]
    ):
        findings.append(
            Finding(
                "error",
                "phase2-baseline-inventory-mismatch",
                path,
                "Baseline membership/order does not match the selected batch.",
            )
        )
    for slug in context.batch["slugs"]:
        locked = baseline_by_slug.get(slug)
        inventory_entry = inventory_by_slug.get(slug)
        note = context.note_records.get(slug)
        if not all((isinstance(locked, dict), isinstance(inventory_entry, dict), note)):
            continue
        if _phase2_path_parts(locked.get("path")) is None:
            findings.append(
                Finding(
                    "error",
                    "phase2-path-invalid",
                    path,
                    f"Baseline path for {slug!r} is invalid.",
                )
            )
            continue
        if any(
            (
                locked.get("path") != inventory_entry.get("path"),
                locked.get("path") != note.path.as_posix(),
                locked.get("type") != inventory_entry.get("type"),
                locked.get("type") != context.batch.get("type"),
                locked.get("originalSha256") != inventory_entry.get("originalSha256"),
                locked.get("summaryHeadings") != inventory_entry.get("summaryHeadings"),
            )
        ):
            findings.append(
                Finding(
                    "error",
                    "phase2-baseline-inventory-mismatch",
                    locked.get("path", path),
                    f"Baseline metadata for {slug!r} differs from assignment/inventory.",
                )
            )
        facts = locked.get("factUnits")
        if not isinstance(facts, list) or not facts:
            findings.append(
                Finding(
                    "error",
                    "phase2-baseline-schema",
                    locked.get("path", path),
                    f"Baseline facts for {slug!r} must be a nonempty array.",
                )
            )
            continue
        expected_ids = [f"{slug}-f{index:02d}" for index in range(1, len(facts) + 1)]
        actual_ids = [
            fact.get("id") if isinstance(fact, dict) else None for fact in facts
        ]
        if actual_ids != expected_ids:
            findings.append(
                Finding(
                    "error",
                    "phase2-baseline-schema",
                    locked.get("path", path),
                    f"Baseline fact IDs for {slug!r} are not stable/sequential.",
                )
            )
        locked_summary = locked.get("originalSummary")
        if isinstance(locked_summary, str):
            locked_note = parse_note_text(
                note.path,
                "---\nsubspecialty: [NR]\n---\n" + locked_summary,
            )
            expected_templates = phase2_default_fact_templates(locked_note)
            locked_summary_headings = [
                section.heading for section in locked_note.summaries
            ]
        else:
            expected_templates = []
            locked_summary_headings = []
        actual_templates = []
        fact_shape_valid = (
            bool(expected_templates)
            and locked.get("summaryHeadings") == locked_summary_headings
        )
        for fact in facts:
            if not isinstance(fact, dict):
                fact_shape_valid = False
                continue
            text = fact.get("text")
            source_statement = fact.get("sourceStatement")
            source_refs = fact.get("sourceRefs")
            refs_valid = (
                isinstance(source_refs, list)
                and all(isinstance(ref, str) and ref for ref in source_refs)
                and len(source_refs) == len(set(source_refs))
                and all(ref in note.footnote_defs for ref in source_refs)
            )
            if (
                set(fact)
                != {"id", "text", "sourceStatement", "sourceRefs"}
                or not isinstance(text, str)
                or not text.strip()
                or not isinstance(source_statement, str)
                or not source_statement
                or not refs_valid
            ):
                fact_shape_valid = False
            actual_templates.append(
                {
                    "text": text,
                    "sourceStatement": source_statement,
                    "sourceRefs": source_refs,
                }
            )
        if not fact_shape_valid or actual_templates != expected_templates:
            findings.append(
                Finding(
                    "error",
                    "phase2-baseline-schema",
                    locked.get("path", path),
                    (
                        f"Baseline facts for {slug!r} are malformed, ungrounded, "
                        "out of source order, or do not cover every factual "
                        "Summary statement."
                    ),
                )
            )
    return findings


def _validate_phase2_source_state(
    context: BatchContext, *, pre_edit: bool
) -> list[Finding]:
    """Validate either the pre-edit lock or the current evidence rewrite."""
    findings: list[Finding] = []
    baseline_by_slug = {
        entry["slug"]: entry
        for entry in (context.baseline or {}).get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    evidence_by_slug = {
        entry["slug"]: entry
        for entry in (context.evidence or {}).get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    for slug in context.batch["slugs"]:
        note = context.note_records.get(slug)
        locked = baseline_by_slug.get(slug, {})
        evidence = evidence_by_slug.get(slug, {})
        display = locked.get("path", context.evidence_path.as_posix())
        if note is None:
            continue
        if pre_edit:
            if locked.get("originalSha256") != note.sha256:
                findings.append(
                    Finding(
                        "error",
                        "phase2-source-hash-mismatch",
                        display,
                        f"Current source hash for {slug!r} differs from the lock.",
                    )
                )
            if locked.get("originalSummary") != note.original_summary:
                findings.append(
                    Finding(
                        "error",
                        "phase2-lossless-summary-mismatch",
                        display,
                        f"Current Summary snapshot for {slug!r} differs from the lock.",
                    )
                )
        elif evidence.get("rewrittenSummary") != note.original_summary:
            findings.append(
                Finding(
                    "error",
                    "evidence-rewritten-summary-mismatch",
                    display,
                    f"Current Summary for {slug!r} differs from evidence.",
                )
            )
    return findings


def _nonselected_detail_hashes(context: BatchContext) -> dict[str, str]:
    selected = set(context.batch["slugs"])
    return {
        (context.generated_root / path.name).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(
            (context.repo_root / context.generated_root).glob("*.json"),
            key=lambda item: item.name,
        )
        if path.stem not in selected
    }


def build_phase2_generated_manifest(
    repo_root: Path,
    batch_id: str,
    *,
    nonselected_before: Mapping[str, str] | None = None,
    nonselected_after: Mapping[str, str] | None = None,
    first_run: Mapping[str, Sequence[str]] | None = None,
    second_run: Mapping[str, Sequence[str]] | None = None,
) -> dict:
    """Construct a manifest from current bytes and explicit build observations."""
    assignment_path = Path(
        "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    )
    context = load_phase2_batch(repo_root, assignment_path, batch_id)
    observation_path = (
        context.assignment_path.parent
        / "phase2a"
        / "generated"
        / f"{batch_id}.json"
    ).as_posix()
    if (
        nonselected_before is None
        or nonselected_after is None
        or first_run is None
        or second_run is None
    ):
        raise Phase2LoadError(
            "generated-observation-missing",
            observation_path,
            "Explicit pre-build, first-run, post-build, and second-run observations are required.",
        )
    selected = set(context.batch["slugs"])

    def valid_nonselected(observation: Mapping[str, str]) -> bool:
        return (
            isinstance(observation, dict)
            and all(
                isinstance(path, str)
                and _phase2_path_parts(path) is not None
                and path.startswith(context.generated_root.as_posix() + "/")
                and Path(path).suffix == ".json"
                and Path(path).stem not in selected
                and isinstance(digest, str)
                and SHA256_RE.fullmatch(digest) is not None
                for path, digest in observation.items()
            )
        )

    run_keys = {"changedPaths", "mtimeChangedPaths"}

    def valid_run(observation: Mapping[str, Sequence[str]]) -> bool:
        return (
            isinstance(observation, dict)
            and set(observation) == run_keys
            and all(
                isinstance(paths, list)
                and paths == sorted(set(paths))
                and all(
                    isinstance(path, str) and _phase2_path_parts(path) is not None
                    for path in paths
                )
                for paths in observation.values()
            )
        )

    if (
        not valid_nonselected(nonselected_before)
        or not valid_nonselected(nonselected_after)
        or dict(nonselected_after) != _nonselected_detail_hashes(context)
        or not valid_run(first_run)
        or not valid_run(second_run)
    ):
        raise Phase2LoadError(
            "generated-observation-invalid",
            observation_path,
            "Build observations must be complete canonical repo-relative snapshots.",
        )
    detail_root = context.repo_root / context.generated_root
    detail_files = sorted(detail_root.glob("*.json"), key=lambda item: item.name)
    tree_entries = []
    all_hashes = {}
    details_by_slug = {}
    for detail_path in detail_files:
        slug = detail_path.stem
        payload = detail_path.read_bytes()
        try:
            detail = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise Phase2LoadError(
                "generated-manifest-mismatch",
                (context.generated_root / detail_path.name).as_posix(),
                "Generated detail JSON is invalid.",
            ) from error
        if not isinstance(detail, dict) or detail.get("slug") != slug:
            raise Phase2LoadError(
                "generated-manifest-mismatch",
                (context.generated_root / detail_path.name).as_posix(),
                "Generated detail slug does not match its filename.",
            )
        digest = hashlib.sha256(payload).hexdigest()
        relative = (context.generated_root / detail_path.name).as_posix()
        all_hashes[slug] = digest
        details_by_slug[slug] = detail
        tree_entries.append({"path": relative, "sha256": digest})
    selected_detail_files = {}
    for slug in context.batch["slugs"]:
        if slug not in all_hashes:
            raise Phase2LoadError(
                "generated-manifest-mismatch",
                (context.generated_root / f"{slug}.json").as_posix(),
                "Selected generated detail is missing.",
            )
        selected_detail_files[
            (context.generated_root / f"{slug}.json").as_posix()
        ] = all_hashes[slug]
    index_path = Path("data/concepts-index.json")
    index_file = context.repo_root / index_path
    try:
        index = json.loads(index_file.read_text(encoding="utf-8"))
        concepts = index["concepts"]
        if not isinstance(concepts, list):
            raise TypeError
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise Phase2LoadError(
            "generated-manifest-mismatch",
            index_path.as_posix(),
            "Generated index is missing or invalid.",
        ) from error
    index_by_slug = {
        entry.get("slug"): entry
        for entry in concepts
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    if (
        len(index_by_slug) != len(concepts)
        or set(index_by_slug) != set(details_by_slug)
        or any(
            any(
                index_by_slug[slug].get(field) != detail.get(field)
                for field in GENERATED_INDEX_FIELDS
            )
            for slug, detail in details_by_slug.items()
        )
    ):
        raise Phase2LoadError(
            "generated-manifest-mismatch",
            index_path.as_posix(),
            "Generated index is not coherent with the complete detail tree.",
        )
    allowed_writes = sorted(
        [*selected_detail_files, index_path.as_posix()]
    )
    return {
        "schemaVersion": 1,
        "kind": "phase2-generated-manifest",
        "batch": batch_id,
        "selectedSlugs": list(context.batch["slugs"]),
        "detailFiles": selected_detail_files,
        "index": {
            "path": index_path.as_posix(),
            "sha256": hashlib.sha256(index_file.read_bytes()).hexdigest(),
            "entryCount": len(concepts),
        },
        "detailFileCount": len(detail_files),
        "detailTreeSha256": _canonical_sha256(tree_entries),
        "allowedWrites": allowed_writes,
        "nonselectedBefore": dict(nonselected_before),
        "nonselectedAfter": dict(nonselected_after),
        "firstRun": {
            key: list(first_run[key])
            for key in ("changedPaths", "mtimeChangedPaths")
        },
        "secondRun": {
            key: list(second_run[key])
            for key in ("changedPaths", "mtimeChangedPaths")
        },
    }


def _phase2_generated_observation_projection(manifest: dict) -> dict:
    return {
        "schemaVersion": 1,
        "kind": "phase2-generated-observation",
        "batch": manifest.get("batch"),
        "selectedSlugs": manifest.get("selectedSlugs"),
        "allowedWrites": manifest.get("allowedWrites"),
        "nonselectedBefore": manifest.get("nonselectedBefore"),
        "nonselectedAfter": manifest.get("nonselectedAfter"),
        "firstRun": manifest.get("firstRun"),
        "secondRun": manifest.get("secondRun"),
        "detailFiles": manifest.get("detailFiles"),
        "index": manifest.get("index"),
        "detailFileCount": manifest.get("detailFileCount"),
        "detailTreeSha256": manifest.get("detailTreeSha256"),
    }


def _phase2_historical_generated_detail_hashes(
    context: BatchContext,
    manifest: dict,
    display_path: str,
) -> dict[str, str]:
    selected_slugs = list(context.batch["slugs"])
    selected_paths = {
        (context.generated_root / f"{slug}.json").as_posix()
        for slug in selected_slugs
    }
    detail_files = manifest.get("detailFiles")
    nonselected_before = manifest.get("nonselectedBefore")
    nonselected_after = manifest.get("nonselectedAfter")

    def valid_hash_map(
        value: object,
        *,
        expected_paths: set[str] | None = None,
        exclude_selected: bool = False,
    ) -> bool:
        if not isinstance(value, dict):
            return False
        if expected_paths is not None and set(value) != expected_paths:
            return False
        return all(
            isinstance(path, str)
            and _phase2_path_parts(path) is not None
            and path.startswith(context.generated_root.as_posix() + "/")
            and Path(path).suffix == ".json"
            and (not exclude_selected or path not in selected_paths)
            and isinstance(digest, str)
            and SHA256_RE.fullmatch(digest) is not None
            for path, digest in value.items()
        )

    expected_allowed_writes = sorted(
        [*selected_paths, "data/concepts-index.json"]
    )
    if (
        manifest.get("schemaVersion") != 1
        or manifest.get("kind") != "phase2-generated-manifest"
        or manifest.get("batch") != context.batch["id"]
        or manifest.get("selectedSlugs") != selected_slugs
        or manifest.get("allowedWrites") != expected_allowed_writes
        or not valid_hash_map(detail_files, expected_paths=selected_paths)
        or not valid_hash_map(nonselected_before, exclude_selected=True)
        or not valid_hash_map(nonselected_after, exclude_selected=True)
        or set(detail_files).intersection(nonselected_after)
    ):
        raise Phase2LoadError(
            "generated-manifest-mismatch",
            display_path,
            "Historical generated observation shape is invalid.",
        )

    historical_hashes = dict(nonselected_after)
    historical_hashes.update(detail_files)
    tree_entries = [
        {"path": path, "sha256": historical_hashes[path]}
        for path in sorted(historical_hashes)
    ]
    index = manifest.get("index")
    detail_file_count = manifest.get("detailFileCount")
    if (
        not isinstance(index, dict)
        or set(index) != {"path", "sha256", "entryCount"}
        or index.get("path") != "data/concepts-index.json"
        or not isinstance(index.get("sha256"), str)
        or SHA256_RE.fullmatch(index["sha256"]) is None
        or type(index.get("entryCount")) is not int
        or type(detail_file_count) is not int
        or index["entryCount"] != detail_file_count
        or detail_file_count != len(historical_hashes)
        or manifest.get("detailTreeSha256") != _canonical_sha256(tree_entries)
    ):
        raise Phase2LoadError(
            "generated-manifest-mismatch",
            display_path,
            "Historical index and detail-tree observation are incoherent.",
        )
    return historical_hashes


def _validate_phase2_own_generated_result(
    context: BatchContext,
) -> tuple[list[Finding], Phase2GeneratedState | None]:
    """Validate one batch's sealed build result without historical authorization."""
    findings: list[Finding] = []
    evidence = context.evidence or {}
    evidence_path = context.evidence_path.as_posix()
    for slug, note in context.note_records.items():
        detail_path = context.generated_root / f"{slug}.json"
        try:
            detail = json.loads(
                (context.repo_root / detail_path).read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            detail = None
        if (
            not isinstance(detail, dict)
            or detail.get("keyPoints") != _generated_keypoints(note)
        ):
            findings.append(
                Finding(
                    "error",
                    "generated-keypoints-mismatch",
                    detail_path.as_posix(),
                    f"Generated keyPoints for {slug!r} differ from Summary bullets.",
                )
            )
    try:
        manifest_path = Path(str(evidence.get("generatedManifest", "")))
        expected_manifest_path = (
            Path("docs/reports/nr-summary-rewrite/phase2a/generated")
            / f"{context.batch['id']}.json"
        )
        if manifest_path.as_posix() != expected_manifest_path.as_posix():
            raise Phase2LoadError(
                "generated-manifest-mismatch",
                evidence_path,
                "Evidence generated manifest path is invalid.",
            )
        checked = _read_phase2_json(
            context.repo_root / manifest_path, manifest_path
        )
        observation_digest = _canonical_sha256(
            _phase2_generated_observation_projection(checked)
        )
        trusted_observation = TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256.get(
            context.batch["id"]
        )
        if (
            not isinstance(trusted_observation, str)
            or SHA256_RE.fullmatch(trusted_observation) is None
            or trusted_observation != observation_digest
        ):
            findings.append(
                Finding(
                    "error",
                    "generated-observation-untrusted",
                    manifest_path.as_posix(),
                    "Generated observations do not match the code-owned review seal.",
                )
            )
        historical_hashes = _phase2_historical_generated_detail_hashes(
            context,
            checked,
            manifest_path.as_posix(),
        )
        current_nonselected = _nonselected_detail_hashes(context)
        empty_run = {"changedPaths": [], "mtimeChangedPaths": []}
        actual = build_phase2_generated_manifest(
            context.repo_root,
            context.batch["id"],
            nonselected_before=current_nonselected,
            nonselected_after=current_nonselected,
            first_run=empty_run,
            second_run=empty_run,
        )
        if checked.get("nonselectedBefore") != checked.get("nonselectedAfter"):
            findings.append(
                Finding(
                    "error",
                    "generated-unrelated-write",
                    manifest_path.as_posix(),
                    "Nonselected detail observations changed across the scoped build.",
                )
            )
        first_run = checked.get("firstRun")
        allowed_writes = checked.get("allowedWrites")
        if (
            not isinstance(first_run, dict)
            or not isinstance(allowed_writes, list)
            or any(
                not isinstance(paths, list)
                or not set(paths).issubset(set(allowed_writes))
                for paths in (
                    first_run.get("changedPaths"),
                    first_run.get("mtimeChangedPaths"),
                )
            )
        ):
            findings.append(
                Finding(
                    "error",
                    "generated-manifest-mismatch",
                    manifest_path.as_posix(),
                    "First-run observations exceed the permitted write set.",
                )
            )
        second_run = checked.get("secondRun")
        if (
            not isinstance(second_run, dict)
            or second_run.get("changedPaths")
            or second_run.get("mtimeChangedPaths")
        ):
            findings.append(
                Finding(
                    "error",
                    "generated-non-idempotent",
                    manifest_path.as_posix(),
                    "Second-run bytes or mtimes changed.",
                )
            )
        current_hashes = dict(actual["nonselectedAfter"])
        current_hashes.update(actual["detailFiles"])
        return findings, Phase2GeneratedState(
            manifest_path=manifest_path.as_posix(),
            checked=checked,
            historical_hashes=historical_hashes,
            current_hashes=current_hashes,
            actual=actual,
        )
    except Phase2LoadError as error:
        findings.append(error.finding())
        return findings, None


def _phase2_historical_authorization_findings(
    state: Phase2GeneratedState,
    authorized_later_paths: set[str],
) -> list[Finding]:
    changed_paths = {
        detail_path
        for detail_path in set(state.historical_hashes) | set(state.current_hashes)
        if state.historical_hashes.get(detail_path)
        != state.current_hashes.get(detail_path)
    }
    selected_paths = set(state.checked["detailFiles"])
    unauthorized_paths = changed_paths.intersection(selected_paths) | (
        changed_paths - selected_paths - authorized_later_paths
    )
    findings = [
        Finding(
            "error",
            "generated-manifest-mismatch",
            unauthorized_path,
            "Current detail evolution is not authorized by a later independently trusted batch.",
        )
        for unauthorized_path in sorted(unauthorized_paths)
    ]
    if not changed_paths and any(
        state.checked.get(field) != state.actual.get(field)
        for field in ("index", "detailFileCount", "detailTreeSha256")
    ):
        findings.append(
            Finding(
                "error",
                "generated-manifest-mismatch",
                state.manifest_path,
                "Current index or tree metadata changed without detail evolution.",
            )
        )
    return findings


def _phase2_generated_chain_passes(
    context: BatchContext,
    own_findings: Sequence[Finding],
    own_state: Phase2GeneratedState,
    end_index: int,
) -> bool:
    """Require a contiguous sealed chain, then authorize history latest-first."""
    batch_ids = list(ACTIVE_PHASE2A_BATCHES)
    states: list[Phase2GeneratedState] = []
    for batch_id in batch_ids[: end_index + 1]:
        if batch_id == context.batch["id"]:
            batch_findings = list(own_findings)
            state = own_state
        else:
            try:
                batch_context = load_phase2_batch(
                    context.repo_root,
                    context.assignment_path,
                    batch_id,
                )
                batch_findings = validate_phase2_batch(
                    batch_context,
                    check_source_hashes=False,
                    check_generated=False,
                )
                generated_findings, state = _validate_phase2_own_generated_result(
                    batch_context
                )
                batch_findings.extend(generated_findings)
            except Phase2LoadError:
                return False
        if state is None or _findings_have_errors(batch_findings):
            return False
        states.append(state)

    authorized_later_paths: set[str] = set()
    for state in reversed(states):
        if _phase2_historical_authorization_findings(
            state,
            authorized_later_paths,
        ):
            return False
        authorized_later_paths.update(
            path
            for path, digest in state.checked["detailFiles"].items()
            if state.current_hashes.get(path) == digest
        )
    return True


def _phase2_generated_snapshot(
    context: BatchContext,
) -> tuple[dict[str, bytes], dict[str, int]]:
    paths = sorted(
        [
            *(context.repo_root / context.generated_root).glob("*.json"),
            context.repo_root / "data" / "concepts-index.json",
        ],
        key=lambda item: item.relative_to(context.repo_root).as_posix(),
    )
    paths = [path for path in paths if path.is_file()]
    return (
        {
            path.relative_to(context.repo_root).as_posix(): path.read_bytes()
            for path in paths
        },
        {
            path.relative_to(context.repo_root).as_posix(): path.stat().st_mtime_ns
            for path in paths
        },
    )


def _phase2_snapshot_delta(
    before: tuple[dict[str, bytes], dict[str, int]],
    after: tuple[dict[str, bytes], dict[str, int]],
) -> dict[str, list[str]]:
    before_bytes, before_mtimes = before
    after_bytes, after_mtimes = after
    return {
        "changedPaths": sorted(
            path
            for path in set(before_bytes) | set(after_bytes)
            if before_bytes.get(path) != after_bytes.get(path)
        ),
        "mtimeChangedPaths": sorted(
            path
            for path in set(before_mtimes) | set(after_mtimes)
            if before_mtimes.get(path) != after_mtimes.get(path)
        ),
    }


def run_phase2_generated_observation_workflow(
    repo_root: Path, batch_id: str
) -> dict:
    """Run the gated scoped build twice and return its sealable observation."""
    assignment_path = Path(
        "docs/reports/nr-summary-rewrite/phase2-assignment.json"
    )
    context = load_phase2_batch(repo_root, assignment_path, batch_id)
    preflight_findings = validate_phase2_batch(
        context,
        check_source_hashes=False,
        check_generated=False,
    )
    errors = [finding for finding in preflight_findings if finding.severity == "error"]
    if errors:
        first = errors[0]
        raise Phase2LoadError(first.code, first.path, first.message)

    import build_concepts as concept_builder

    pre_nonselected = _nonselected_detail_hashes(context)
    pre_snapshot = _phase2_generated_snapshot(context)
    concept_builder.build_selected_concepts(
        context.batch["slugs"],
        src_dir=context.repo_root / "vault" / "concepts",
        out_dir=context.repo_root / context.generated_root,
        index_path=context.repo_root / "data" / "concepts-index.json",
    )
    post_nonselected = _nonselected_detail_hashes(context)
    post_snapshot = _phase2_generated_snapshot(context)
    concept_builder.build_selected_concepts(
        context.batch["slugs"],
        src_dir=context.repo_root / "vault" / "concepts",
        out_dir=context.repo_root / context.generated_root,
        index_path=context.repo_root / "data" / "concepts-index.json",
    )
    second_snapshot = _phase2_generated_snapshot(context)
    first_run = _phase2_snapshot_delta(pre_snapshot, post_snapshot)
    second_run = _phase2_snapshot_delta(post_snapshot, second_snapshot)
    if pre_nonselected != post_nonselected:
        raise Phase2LoadError(
            "generated-unrelated-write",
            context.generated_root.as_posix(),
            "The scoped build changed a nonselected detail.",
        )
    if second_run["changedPaths"] or second_run["mtimeChangedPaths"]:
        raise Phase2LoadError(
            "generated-non-idempotent",
            "data",
            "The actual second scoped build changed bytes or mtimes.",
        )
    manifest = build_phase2_generated_manifest(
        context.repo_root,
        batch_id,
        nonselected_before=pre_nonselected,
        nonselected_after=post_nonselected,
        first_run=first_run,
        second_run=second_run,
    )
    return {
        "manifest": manifest,
        "observationSha256": _canonical_sha256(
            _phase2_generated_observation_projection(manifest)
        ),
    }


def validate_phase2_batch(
    context: BatchContext, check_source_hashes: bool, check_generated: bool
) -> list[Finding]:
    findings = validate_baseline_lock(context)
    findings.extend(
        _validate_phase2_source_state(context, pre_edit=check_source_hashes)
    )
    evidence = context.evidence
    path = context.evidence_path.as_posix()
    if not isinstance(evidence, dict):
        return findings + [
            Finding("error", "phase2-baseline-schema", path, "Batch evidence is missing.")
        ]
    evidence_notes = evidence.get("notes")
    if not isinstance(evidence_notes, list):
        return findings + [
            Finding("error", "phase2-baseline-schema", path, "Evidence notes must be an array.")
        ]
    required_root = {
        "schemaVersion",
        "kind",
        "batch",
        "scope",
        "baselineLock",
        "status",
        "workflow",
        "notes",
        "manualReviewFactIds",
        "generatedManifest",
    }
    if (
        required_root - evidence.keys()
        or evidence.get("schemaVersion") != 1
        or evidence.get("kind") != "phase2-batch-evidence"
        or evidence.get("batch") != context.batch["id"]
        or evidence.get("scope") != "NR"
    ):
        findings.append(
            Finding(
                "error",
                "phase2-evidence-schema",
                path,
                "Evidence root shape or identity is invalid.",
            )
        )
    evidence_slugs = [
        entry.get("slug") if isinstance(entry, dict) else None
        for entry in evidence_notes
    ]
    if evidence_slugs != context.batch["slugs"]:
        findings.append(
            Finding(
                "error",
                "phase2-evidence-schema",
                path,
                "Evidence notes must exactly match ordered batch membership.",
            )
        )
    baseline_digest = (
        _canonical_sha256(context.baseline) if isinstance(context.baseline, dict) else None
    )
    expected_lock_path = context.baseline_path.as_posix()
    lock_ref = evidence.get("baselineLock")
    if (
        not isinstance(lock_ref, dict)
        or lock_ref.get("path") != expected_lock_path
        or lock_ref.get("sha256") != baseline_digest
    ):
        findings.append(
            Finding(
                "error",
                "phase2-evidence-schema",
                path,
                "Evidence baseline reference does not match the loaded lock.",
            )
        )
    baseline_by_slug = {
        entry["slug"]: entry
        for entry in (context.baseline or {}).get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    unresolved = []
    for entry in evidence_notes:
        if not isinstance(entry, dict) or not isinstance(entry.get("slug"), str):
            findings.append(
                Finding("error", "evidence-fact-coverage", path, "Malformed evidence note.")
            )
            continue
        slug = entry["slug"]
        locked = baseline_by_slug.get(slug, {})
        note = context.note_records.get(slug)
        required_note = {
            "slug",
            "sourceStatus",
            "status",
            "rewrittenSummary",
            "facts",
            "sourceDefinitions",
            "newUnsupportedFacts",
            "validation",
            "summaryBulletEvidence",
            "coverageEvidenceSha256",
        }
        if required_note - entry.keys():
            findings.append(
                Finding(
                    "error",
                    "phase2-evidence-schema",
                    path,
                    f"Evidence note {slug!r} is missing required fields.",
                )
            )
        expected_ids = [
            fact.get("id")
            for fact in locked.get("factUnits", [])
            if isinstance(fact, dict)
        ]
        facts = entry.get("facts")
        actual_ids = [
            fact.get("id")
            for fact in facts
            if isinstance(fact, dict)
        ] if isinstance(facts, list) else []
        if actual_ids != expected_ids:
            findings.append(
                Finding(
                    "error",
                    "evidence-fact-coverage",
                    path,
                    f"Evidence fact IDs for {slug!r} differ from baseline.",
                )
            )
        definitions = entry.get("sourceDefinitions")
        definitions = definitions if isinstance(definitions, dict) else {}
        current_summary_findings = validate_summary(note) if note is not None else []
        findings.extend(current_summary_findings)
        local_dispositions = []
        for fact in facts if isinstance(facts, list) else []:
            if not isinstance(fact, dict):
                continue
            disposition = fact.get("disposition")
            local_dispositions.append(disposition)
            if disposition not in {"covered", "research-needed", "manual-review"}:
                findings.append(
                    Finding(
                        "error",
                        "evidence-fact-coverage",
                        path,
                        f"Unsupported disposition for {fact.get('id')!r}.",
                    )
                )
            if disposition in {"research-needed", "manual-review"}:
                unresolved.append(fact.get("id"))
            refs = fact.get("sourceRefs")
            if not isinstance(refs, list) or not refs or any(
                ref not in definitions for ref in refs
            ):
                findings.append(
                    Finding(
                        "error",
                        "evidence-source-definition",
                        path,
                        f"Evidence sources for {fact.get('id')!r} are incomplete.",
                    )
                )
            for ref in refs if isinstance(refs, list) else []:
                definition = definitions.get(ref)
                if (
                    not isinstance(definition, dict)
                    or definition.get("kind")
                    not in {"existing-footnote", "article", "chapter"}
                    or not isinstance(definition.get("locator"), str)
                    or not definition["locator"].strip()
                    or not isinstance(definition.get("citation"), str)
                    or not definition["citation"].strip()
                    or note is None
                    or ref not in note.footnote_defs
                ):
                    findings.append(
                        Finding(
                            "error",
                            "evidence-source-definition",
                            path,
                            f"Source definition {ref!r} is malformed or not rendered.",
                        )
                    )
        if entry.get("newUnsupportedFacts") != 0:
            findings.append(
                Finding(
                    "error",
                    "evidence-unsupported-fact",
                    path,
                    f"Evidence note {slug!r} has unsupported rewritten facts.",
                )
            )
        validation = entry.get("validation")
        covered = sum(item == "covered" for item in local_dispositions)
        research_needed = sum(item == "research-needed" for item in local_dispositions)
        manual_review = sum(item == "manual-review" for item in local_dispositions)
        referenced_definition_kinds = {
            definitions[ref].get("kind")
            for fact in (facts if isinstance(facts, list) else [])
            if isinstance(fact, dict)
            for ref in (
                fact.get("sourceRefs")
                if isinstance(fact.get("sourceRefs"), list)
                else []
            )
            if isinstance(definitions.get(ref), dict)
        }
        expected_note_status = (
            "manual-review"
            if manual_review
            else "research-needed"
            if research_needed
            else "verified"
        )
        expected_source_status = (
            "conflict"
            if manual_review
            else "research-needed"
            if research_needed
            else "researched"
            if referenced_definition_kinds & {"article", "chapter"}
            else "existing-sufficient"
        )
        fact_coverage = (
            validation.get("factCoverage") if isinstance(validation, dict) else None
        )
        actual_footnote_errors = sum(
            finding.code == "footnote-undefined"
            for finding in current_summary_findings
        )
        actual_structure_errors = len(current_summary_findings) - actual_footnote_errors
        if (
            not isinstance(validation, dict)
            or validation.get("hashMatches") is not True
            or validation.get("losslessSummaryMatches") is not True
            or validation.get("allSourceRefsDefined") is not True
            or not isinstance(validation.get("structure"), dict)
            or validation["structure"].get("errors") != actual_structure_errors
            or not isinstance(validation.get("footnotes"), dict)
            or validation["footnotes"].get("errors") != actual_footnote_errors
            or fact_coverage
            != {
                "total": len(local_dispositions),
                "covered": covered,
                "researchNeeded": research_needed,
                "manualReview": manual_review,
            }
        ):
            findings.append(
                Finding(
                    "error",
                    "phase2-evidence-schema",
                    path,
                    f"Evidence validation block for {slug!r} is not derived.",
                )
            )
        if (
            note is not None
            and entry.get("summaryBulletEvidence") != _generated_keypoints(note)
        ):
            findings.append(
                Finding(
                    "error",
                    "evidence-rewritten-summary-mismatch",
                    path,
                    f"Summary bullet evidence for {slug!r} differs from source.",
                )
            )
        if (
            not local_dispositions
            or any(
                item not in {"covered", "research-needed", "manual-review"}
                for item in local_dispositions
            )
            or entry.get("status") != expected_note_status
            or entry.get("sourceStatus") != expected_source_status
        ):
            findings.append(
                Finding(
                    "error",
                    "phase2-evidence-schema",
                    path,
                    f"Evidence note/source status for {slug!r} is not derived.",
                )
            )
    if evidence.get("manualReviewFactIds") != sorted(unresolved):
        findings.append(
            Finding(
                "error",
                "phase2-manual-queue-mismatch",
                path,
                "Manual queue is not the derived sorted unresolved fact IDs.",
            )
        )
    expected_root_status = "needs-review" if unresolved else "verified"
    if (
        not _is_string_member(evidence.get("status"), BATCH_STATUSES)
        or evidence.get("status") != expected_root_status
    ):
        findings.append(
            Finding(
                "error",
                "phase2-evidence-schema",
                path,
                "Evidence root status is not derived from note dispositions.",
            )
        )
    workflow = evidence.get("workflow")
    batch_ids = list(ACTIVE_PHASE2A_BATCHES)
    batch_index = batch_ids.index(context.batch["id"])
    expected_sequence = batch_index + 1
    expected_predecessor = batch_ids[batch_index - 1] if batch_index else None
    if (
        not isinstance(workflow, dict)
        or workflow.get("sequence") != expected_sequence
        or workflow.get("predecessor") != expected_predecessor
        or workflow.get("reviewStatus")
        not in {"not-started", "changes-requested", "approved"}
        or (
            workflow.get("reviewStatus") == "approved"
            and workflow.get("reviewedBaselineSha256") != baseline_digest
        )
    ):
        findings.append(
            Finding(
                "error",
                "phase2-review-sequence",
                path,
                "Workflow sequence, predecessor, review state, or snapshot is invalid.",
            )
        )
    if expected_root_status in {"verified", "needs-review"} and (
        not isinstance(workflow, dict)
        or workflow.get("reviewStatus") != "approved"
        or workflow.get("reviewedBaselineSha256") != baseline_digest
    ):
        findings.append(
            Finding(
                "error",
                "phase2-review-sequence",
                path,
                "Terminal batch status requires approved review of this baseline.",
            )
        )
    if batch_index:
        predecessor_id = batch_ids[batch_index - 1]
        try:
            predecessor_context = load_phase2_batch(
                context.repo_root,
                context.assignment_path,
                predecessor_id,
            )
            predecessor_findings = validate_phase2_batch(
                predecessor_context,
                check_source_hashes=False,
                check_generated=False,
            )
            predecessor_evidence = predecessor_context.evidence or {}
            predecessor_workflow = predecessor_evidence.get("workflow")
            predecessor_ok = (
                not _findings_have_errors(predecessor_findings)
                and predecessor_evidence.get("status") in {"verified", "needs-review"}
                and isinstance(predecessor_workflow, dict)
                and predecessor_workflow.get("reviewStatus") == "approved"
            )
        except Phase2LoadError:
            predecessor_ok = False
        if not predecessor_ok:
            findings.append(
                Finding(
                    "error",
                    "phase2-review-sequence",
                    path,
                    f"Approved terminal predecessor {predecessor_id!r} is required.",
                )
            )
    implementer = workflow.get("implementer") if isinstance(workflow, dict) else None
    reviewer = workflow.get("reviewer") if isinstance(workflow, dict) else None
    canonical_implementer = (
        implementer
        if isinstance(implementer, str)
        and implementer == implementer.strip()
        and PHASE2_RUN_ID_RE.fullmatch(implementer) is not None
        else None
    )
    canonical_reviewer = (
        reviewer
        if isinstance(reviewer, str)
        and reviewer == reviewer.strip()
        and PHASE2_RUN_ID_RE.fullmatch(reviewer) is not None
        else None
    )
    if (
        canonical_implementer is None
        or canonical_reviewer is None
        or canonical_implementer == canonical_reviewer
    ):
        findings.append(
            Finding(
                "error",
                "phase2-reviewer-conflict",
                path,
                "Implementer and reviewer must be canonical, traceable, distinct run IDs.",
            )
        )
    if check_generated:
        own_generated_findings, own_generated_state = (
            _validate_phase2_own_generated_result(context)
        )
        findings.extend(own_generated_findings)
        if own_generated_state is not None:
            batch_ids = list(ACTIVE_PHASE2A_BATCHES)
            end_index = batch_ids.index(context.batch["id"])
            changed_paths = {
                detail_path
                for detail_path in (
                    set(own_generated_state.historical_hashes)
                    | set(own_generated_state.current_hashes)
                )
                if own_generated_state.historical_hashes.get(detail_path)
                != own_generated_state.current_hashes.get(detail_path)
            }
            for later_index, later_batch_id in enumerate(batch_ids):
                if later_index <= end_index:
                    continue
                later_paths = {
                    (context.generated_root / f"{slug}.json").as_posix()
                    for slug in ACTIVE_PHASE2A_BATCHES[later_batch_id]["slugs"]
                }
                if changed_paths.intersection(later_paths):
                    end_index = later_index
            if not _phase2_generated_chain_passes(
                context,
                own_generated_findings,
                own_generated_state,
                end_index,
            ):
                findings.append(
                    Finding(
                        "error",
                        "generated-manifest-mismatch",
                        own_generated_state.manifest_path,
                        "Complete contiguous generated-observation chain is invalid.",
                    )
                )
    return findings


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
            if not line.strip():
                continue
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

            if LEVEL_THREE_HEADING_RE.fullmatch(line):
                continue
            bullet_match = TOP_LEVEL_BULLET_RE.match(line)
            if bullet_match:
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
                continue

            findings.append(
                _finding(
                    "summary-content-line",
                    note,
                    (
                        f"Summary content at line {line_number} must be a level-three "
                        "subsection heading or a valid labeled top-level bullet."
                    ),
                )
            )

        if valid_bullets == 0:
            findings.append(
                _finding("summary-bullet-label", note, f"{section.heading!r} has no valid top-level bullet.")
            )

    for reference in sorted(note.footnote_refs - note.footnote_defs):
        findings.append(_finding("footnote-undefined", note, f"Footnote reference [^{reference}] has no definition."))
    return findings


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _baseline_evidence_sha256(entry: dict) -> str:
    fact_units = entry.get("factUnits")
    stable_facts = []
    if isinstance(fact_units, list):
        for fact in fact_units:
            if not isinstance(fact, dict):
                stable_facts.append(None)
                continue
            stable_facts.append(
                {
                    "id": fact.get("id"),
                    "text": fact.get("text"),
                    "sourceRefs": fact.get("sourceRefs"),
                }
            )
    return _canonical_sha256(
        {
            "originalSummary": entry.get("originalSummary"),
            "factUnits": stable_facts,
        }
    )


def _coverage_evidence_sha256(entry: dict) -> str:
    fact_units = entry.get("factUnits")
    fact_dispositions = []
    if isinstance(fact_units, list):
        for fact in fact_units:
            if not isinstance(fact, dict):
                fact_dispositions.append(None)
                continue
            fact_dispositions.append(
                {
                    "id": fact.get("id"),
                    "disposition": fact.get("disposition"),
                }
            )
    return _canonical_sha256(
        {
            "rewrittenSummary": entry.get("rewrittenSummary"),
            "factDispositions": fact_dispositions,
            "summaryBulletEvidence": entry.get("summaryBulletEvidence"),
        }
    )


def _unique_batch_entry(report: dict, slug: str) -> dict | None:
    report_notes = report.get("notes")
    if not isinstance(report_notes, list):
        return None
    matches = [
        entry
        for entry in report_notes
        if isinstance(entry, dict) and entry.get("slug") == slug
    ]
    return matches[0] if len(matches) == 1 else None


def _reviewed_baseline_evidence_sha256(
    report: dict,
    *,
    task3_projection: bool,
) -> str:
    note_payloads = []
    for slug in sorted(PILOT_SLUGS):
        entry = _unique_batch_entry(report, slug)
        if entry is None:
            note_payloads.append({"slug": slug, "originalSummary": None, "factUnits": None})
            continue
        fact_units = entry.get("factUnits")
        stable_facts = []
        if isinstance(fact_units, list):
            for fact in fact_units:
                if not isinstance(fact, dict):
                    stable_facts.append(None)
                    continue
                source_refs = fact.get("sourceRefs")
                if task3_projection and isinstance(source_refs, list):
                    reviewed_additions = TRUSTED_TASK4_SOURCE_REF_ADDITIONS.get(
                        fact.get("id"),
                        frozenset(),
                    )
                    source_refs = [
                        source_ref
                        for source_ref in source_refs
                        if source_ref not in reviewed_additions
                    ]
                stable_facts.append(
                    {
                        "id": fact.get("id"),
                        "text": fact.get("text"),
                        "sourceRefs": source_refs,
                    }
                )
        else:
            stable_facts = None
        note_payloads.append(
            {
                "slug": slug,
                "originalSummary": entry.get("originalSummary"),
                "factUnits": stable_facts,
            }
        )
    return _canonical_sha256({"batch": "batch-00", "notes": note_payloads})


def _final_summary_bullet_evidence_sha256(
    report: dict,
    notes: dict[str, NoteRecord],
) -> str:
    note_payloads = []
    for slug in sorted(PILOT_SLUGS):
        entry = _unique_batch_entry(report, slug)
        note = notes.get(slug)
        evidence = entry.get("summaryBulletEvidence") if entry is not None else None
        bullet_payloads = []
        if note is not None:
            for index, bullet in enumerate(_summary_bullet_lines(note)):
                evidence_record = (
                    evidence[index]
                    if isinstance(evidence, list)
                    and index < len(evidence)
                    and isinstance(evidence[index], dict)
                    else None
                )
                bullet_payloads.append(
                    {
                        "text": bullet,
                        "factIds": (
                            evidence_record.get("factIds")
                            if evidence_record is not None
                            else None
                        ),
                    }
                )
        else:
            bullet_payloads = None
        note_payloads.append({"slug": slug, "summaryBullets": bullet_payloads})
    return _canonical_sha256({"batch": "batch-00", "notes": note_payloads})


def _derived_manual_review_fact_ids(report: dict) -> list[str]:
    report_notes = report.get("notes") if isinstance(report, dict) else None
    if not isinstance(report_notes, list):
        return []
    return sorted(
        fact.get("id")
        for entry in report_notes
        if isinstance(entry, dict) and isinstance(entry.get("factUnits"), list)
        for fact in entry["factUnits"]
        if isinstance(fact, dict)
        and fact.get("disposition") == "manual-review"
        and isinstance(fact.get("id"), str)
    )


def _final_review_evidence_sha256(
    report: dict,
    notes: dict[str, NoteRecord],
) -> str:
    """Seal all reviewed final-state fields outside mutable batch evidence."""
    note_payloads = []
    for slug in sorted(PILOT_SLUGS):
        entry = _unique_batch_entry(report, slug)
        note = notes.get(slug)
        if entry is None:
            note_payloads.append({"slug": slug, "entry": None})
            continue
        fact_units = entry.get("factUnits")
        reviewed_facts = (
            [
                {
                    "id": fact.get("id"),
                    "text": fact.get("text"),
                    "sourceRefs": fact.get("sourceRefs"),
                    "disposition": fact.get("disposition"),
                }
                if isinstance(fact, dict)
                else None
                for fact in fact_units
            ]
            if isinstance(fact_units, list)
            else None
        )
        note_payloads.append(
            {
                "slug": slug,
                "type": entry.get("type"),
                "sourceStatus": entry.get("sourceStatus"),
                "status": entry.get("status"),
                "currentSummary": note.original_summary if note is not None else None,
                "rewrittenSummary": entry.get("rewrittenSummary"),
                "factUnits": reviewed_facts,
                "summaryBulletEvidence": entry.get("summaryBulletEvidence"),
                "validation": entry.get("validation"),
                "baselineEvidenceSha256": entry.get("baselineEvidenceSha256"),
                "coverageEvidenceSha256": entry.get("coverageEvidenceSha256"),
            }
        )
    return _canonical_sha256(
        {
            "batch": "batch-00",
            "status": report.get("status"),
            "phase1Verification": report.get("phase1Verification"),
            "manualReviewFactIds": _derived_manual_review_fact_ids(report),
            "notes": note_payloads,
        }
    )


def _coherent_pilot_repo_root(
    notes: dict[str, NoteRecord],
) -> Path | None:
    """Return the checkout root for an exact, coherently rooted pilot set."""
    if set(notes) != PILOT_SLUGS:
        return None
    roots: set[Path] = set()
    for slug in PILOT_SLUGS:
        note = notes.get(slug)
        if note is None:
            return None
        note_path = note.path.resolve()
        if len(note_path.parents) < 3:
            return None
        root = note_path.parents[2]
        if note_path != (root / "vault" / "concepts" / f"{slug}.md").resolve():
            return None
        roots.add(root)
    return next(iter(roots)) if len(roots) == 1 else None


def _trusted_evidence_anchor_findings(
    report: dict,
    notes: dict[str, NoteRecord],
    batch_path: str,
) -> list[Finding]:
    if set(notes) != PILOT_SLUGS:
        return []
    if _coherent_pilot_repo_root(notes) is None:
        return [
            Finding(
                "error",
                "evidence-pilot-root",
                batch_path,
                "Fixed-pilot evidence does not resolve to one coherent checkout root.",
            )
        ]
    findings: list[Finding] = []
    task3_digest = _reviewed_baseline_evidence_sha256(
        report,
        task3_projection=True,
    )
    reviewed_digest = _reviewed_baseline_evidence_sha256(
        report,
        task3_projection=False,
    )
    if (
        task3_digest != TRUSTED_TASK3_BASELINE_EVIDENCE_SHA256
        or reviewed_digest != TRUSTED_REVIEWED_BASELINE_EVIDENCE_SHA256
    ):
        findings.append(
            Finding(
                "error",
                "evidence-trusted-baseline-mismatch",
                batch_path,
                (
                    "The recomputed immutable baseline evidence differs from the "
                    "reviewed code trust anchors."
                ),
            )
        )
    final_summary_digest = _final_summary_bullet_evidence_sha256(report, notes)
    if final_summary_digest != TRUSTED_FINAL_SUMMARY_BULLET_EVIDENCE_SHA256:
        findings.append(
            Finding(
                "error",
                "evidence-trusted-summary-bullet-mismatch",
                batch_path,
                (
                    "The recomputed current Summary bullets and fact mappings differ "
                    "from the reviewed code trust anchor."
                ),
            )
        )
    final_review_digest = _final_review_evidence_sha256(report, notes)
    if final_review_digest != TRUSTED_FINAL_REVIEW_EVIDENCE_SHA256:
        findings.append(
            Finding(
                "error",
                "evidence-trusted-final-mismatch",
                batch_path,
                (
                    "The complete reviewed final state differs from the code-owned "
                    "trust anchor."
                ),
            )
        )
    return findings


def _summary_bullet_lines(note: NoteRecord) -> list[str]:
    bullets: list[str] = []
    for section in note.summaries:
        for line in section.content.splitlines():
            if TOP_LEVEL_BULLET_RE.match(line):
                bullets.append(line.rstrip())
    return bullets


def _ordered_footnote_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in FOOTNOTE_REFERENCE_RE.finditer(text):
        source_ref = match.group("id")
        if source_ref not in refs:
            refs.append(source_ref)
    return refs


def _generated_keypoints(note: NoteRecord) -> list[str]:
    """Mirror build_concepts.py Summary bullet normalization."""
    if not note.summaries:
        return []

    keypoints: list[str] = []
    for section in note.summaries:
        for line in section.content.splitlines():
            match = TOP_LEVEL_BULLET_RE.match(line)
            if not match:
                continue
            normalized = FOOTNOTE_REFERENCE_RE.sub("", match.group("content")).strip()
            if normalized:
                keypoints.append(normalized)
    return keypoints


def _canonical_generated_root(
    report_path: Path,
    notes: dict[str, NoteRecord],
) -> tuple[Path | None, list[Finding]]:
    """Bind generated data to the one checkout root that supplied source notes."""
    roots: set[Path] = set()
    for slug, note in notes.items():
        note_path = note.path.resolve()
        if len(note_path.parents) < 3:
            return None, [
                Finding(
                    "error",
                    "generated-root-mismatch",
                    note.path.as_posix(),
                    f"Pilot source path for {slug!r} has no canonical checkout root.",
                )
            ]
        root = note_path.parents[2]
        expected = (root / "vault" / "concepts" / f"{slug}.md").resolve()
        if note_path != expected:
            return None, [
                Finding(
                    "error",
                    "generated-root-mismatch",
                    note.path.as_posix(),
                    f"Pilot source path for {slug!r} is not canonical for its checkout.",
                )
            ]
        roots.add(root)

    if len(roots) != 1:
        return None, [
            Finding(
                "error",
                "generated-root-mismatch",
                report_path.as_posix(),
                "Pilot source notes do not resolve to exactly one checkout root.",
            )
        ]

    repo_root = next(iter(roots))
    if not report_path.resolve().is_relative_to(repo_root):
        return None, [
            Finding(
                "error",
                "generated-root-mismatch",
                report_path.as_posix(),
                "Batch report and pilot source notes resolve to different checkouts.",
            )
        ]
    return repo_root, []


def validate_generated_keypoints(
    repo_root: Path,
    notes: dict[str, NoteRecord],
) -> list[Finding]:
    """Require each checked-in pilot JSON keyPoints list to mirror its Summary."""
    findings: list[Finding] = []
    for slug in sorted(PILOT_SLUGS):
        note = notes.get(slug)
        generated_path = repo_root / "data" / "concepts" / f"{slug}.json"
        if note is None:
            continue
        try:
            generated = json.loads(generated_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            findings.append(
                Finding(
                    "error",
                    "generated-keypoints-mismatch",
                    generated_path.as_posix(),
                    f"Cannot read generated pilot JSON: {error}.",
                )
            )
            continue

        actual = generated.get("keyPoints") if isinstance(generated, dict) else None
        expected = _generated_keypoints(note)
        if actual != expected:
            findings.append(
                Finding(
                    "error",
                    "generated-keypoints-mismatch",
                    generated_path.as_posix(),
                    (
                        f"Generated keyPoints for {slug!r} must exactly match "
                        "the normalized source Summary bullets in order."
                    ),
                )
            )
    return findings


def validate_generated_index(
    repo_root: Path,
    expected_count: int | None = None,
) -> list[Finding]:
    """Require a complete, non-dangling index consistent with detail metadata."""
    index_path = repo_root / "data" / "concepts-index.json"
    detail_root = repo_root / "data" / "concepts"
    try:
        report = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [
            Finding(
                "error",
                "generated-index-invalid",
                index_path.as_posix(),
                f"Cannot read generated concepts index: {error}.",
            )
        ]

    entries = report.get("concepts") if isinstance(report, dict) else None
    if not isinstance(entries, list):
        return [
            Finding(
                "error",
                "generated-index-invalid",
                index_path.as_posix(),
                "Generated concepts index must contain a concepts array.",
            )
        ]

    findings: list[Finding] = []
    if expected_count is not None and len(entries) != expected_count:
        findings.append(
            Finding(
                "error",
                "generated-index-count-mismatch",
                index_path.as_posix(),
                f"Generated index must contain exactly {expected_count} entries.",
            )
        )
    indexed_slugs: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("slug"), str):
            findings.append(
                Finding(
                    "error",
                    "generated-index-invalid",
                    index_path.as_posix(),
                    "Every generated index entry must be an object with a string slug.",
                )
            )
            continue
        slug = entry["slug"]
        if slug in indexed_slugs:
            findings.append(
                Finding(
                    "error",
                    "generated-index-invalid",
                    index_path.as_posix(),
                    f"Generated index contains duplicate slug {slug!r}.",
                )
            )
            continue
        indexed_slugs.add(slug)
        generated_path = detail_root / f"{slug}.json"
        try:
            detail = json.loads(generated_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            fallback = LEGACY_INDEX_DETAIL_FALLBACKS.get(slug)
            if fallback is None:
                findings.append(
                    Finding(
                        "error",
                        "generated-index-dangling",
                        index_path.as_posix(),
                        f"Generated index slug {slug!r} has no detail JSON.",
                    )
                )
                continue
            detail = fallback
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            findings.append(
                Finding(
                    "error",
                    "generated-index-detail-invalid",
                    generated_path.as_posix(),
                    f"Cannot read indexed detail JSON: {error}.",
                )
            )
            continue

        if not isinstance(detail, dict):
            findings.append(
                Finding(
                    "error",
                    "generated-index-detail-invalid",
                    generated_path.as_posix(),
                    "Indexed detail JSON must be an object.",
                )
            )
            continue
        expected = {field: detail.get(field) for field in GENERATED_INDEX_FIELDS}
        actual = {field: entry.get(field) for field in GENERATED_INDEX_FIELDS}
        if actual != expected:
            findings.append(
                Finding(
                    "error",
                    "generated-index-metadata-mismatch",
                    index_path.as_posix(),
                    f"Generated index metadata for {slug!r} differs from its detail JSON.",
                )
            )

    detail_slugs = {path.stem for path in detail_root.glob("*.json")}
    if expected_count is not None and len(detail_slugs) != expected_count:
        findings.append(
            Finding(
                "error",
                "generated-index-count-mismatch",
                detail_root.as_posix(),
                f"Generated detail directory must contain exactly {expected_count} JSON files.",
            )
        )
    unindexed = sorted(detail_slugs - indexed_slugs)
    for slug in unindexed:
        findings.append(
            Finding(
                "error",
                "generated-index-detail-unindexed",
                index_path.as_posix(),
                f"Detail JSON {slug!r} is absent from the generated index.",
            )
        )
    return findings


def _raw_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_generated_output_manifest(repo_root: Path) -> dict:
    """Return a timestamp-free seal of pilot outputs and the full detail tree."""
    detail_root = repo_root / "data" / "concepts"
    index_path = repo_root / "data" / "concepts-index.json"
    detail_paths = sorted(detail_root.glob("*.json"), key=lambda path: path.name)
    detail_records = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "sha256": _raw_file_sha256(path),
        }
        for path in detail_paths
    ]
    pilot_files = {
        (Path("data") / "concepts" / f"{slug}.json").as_posix(): (
            _raw_file_sha256(detail_root / f"{slug}.json")
            if (detail_root / f"{slug}.json").is_file()
            else None
        )
        for slug in sorted(PILOT_SLUGS)
    }
    index_report = json.loads(index_path.read_text(encoding="utf-8"))
    index_entries = index_report.get("concepts") if isinstance(index_report, dict) else None
    return {
        "schemaVersion": 1,
        "pilotFiles": pilot_files,
        "index": {
            "path": "data/concepts-index.json",
            "sha256": _raw_file_sha256(index_path),
            "entryCount": len(index_entries) if isinstance(index_entries, list) else None,
        },
        "detailFileCount": len(detail_records),
        "allDetailFilesSha256": _canonical_sha256(detail_records),
    }


def validate_generated_manifest(
    reviewed_manifest: object,
    repo_root: Path,
) -> list[Finding]:
    """Require current generated bytes to equal a reviewed deterministic manifest."""
    path = (repo_root / "data").as_posix()
    if not isinstance(reviewed_manifest, dict):
        return [
            Finding(
                "error",
                "generated-manifest-invalid",
                path,
                "Reviewed generated manifest must be an object.",
            )
        ]
    try:
        current_manifest = build_generated_output_manifest(repo_root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [
            Finding(
                "error",
                "generated-manifest-invalid",
                path,
                f"Cannot recompute generated output manifest: {error}.",
            )
        ]
    if reviewed_manifest != current_manifest:
        return [
            Finding(
                "error",
                "generated-manifest-mismatch",
                path,
                "Current generated output bytes differ from the reviewed manifest.",
            )
        ]
    return []


def parse_lint_result(output: str, exit_code: int) -> dict | None:
    """Parse lint_concepts.py --quiet output into a deterministic projection."""
    if not isinstance(output, str) or not isinstance(exit_code, int):
        return None
    error_match = re.search(r"(?m)^=== ERROR \((\d+)\) ===\s*$", output)
    warning_match = re.search(r"(?m)^=== WARN \((\d+)\) ===\s*$", output)
    summary_match = re.search(
        r"(?m)^小結：(\d+) errors, (\d+) warnings\s*$",
        output,
    )
    if error_match is None or warning_match is None or summary_match is None:
        return None
    errors = tuple(
        match.group("message").strip()
        for match in re.finditer(r"(?m)^\s*✗\s+(?P<message>.+?)\s*$", output)
    )
    error_count = int(error_match.group(1))
    warning_count = int(warning_match.group(1))
    if (
        error_count != int(summary_match.group(1))
        or warning_count != int(summary_match.group(2))
        or error_count != len(errors)
    ):
        return None
    pilot_errors = sorted(
        error
        for error in errors
        if any(
            f"{slug}.md" in error or f"data/concepts/{slug}.json" in error
            for slug in PILOT_SLUGS
        )
    )
    return {
        "exitCode": exit_code,
        "errorCount": error_count,
        "warningCount": warning_count,
        "errors": list(errors),
        "pilotErrors": pilot_errors,
    }


def validate_lint_baseline(
    output: str,
    exit_code: int,
    *,
    path: str = "scripts/lint_concepts.py",
) -> list[Finding]:
    """Accept only the exact reviewed non-NR 2-error/124-warning baseline."""
    parsed = parse_lint_result(output, exit_code)
    if (
        parsed is None
        or parsed["exitCode"] != 1
        or parsed["errorCount"] != len(EXPECTED_LINT_ERRORS)
        or parsed["warningCount"] != EXPECTED_LINT_WARNING_COUNT
        or parsed["errors"] != list(EXPECTED_LINT_ERRORS)
        or parsed["pilotErrors"]
    ):
        return [
            Finding(
                "error",
                "lint-baseline-mismatch",
                path,
                "Lint output must equal the exact two-error/124-warning non-NR baseline.",
            )
        ]
    return []


def _phase1_fact_coverage(report: dict) -> dict:
    facts = [
        fact
        for entry in report.get("notes", [])
        if isinstance(entry, dict) and isinstance(entry.get("factUnits"), list)
        for fact in entry["factUnits"]
        if isinstance(fact, dict)
    ]
    return {
        "total": len(facts),
        "covered": sum(fact.get("disposition") == "covered" for fact in facts),
        "manualReview": sum(
            fact.get("disposition") == "manual-review" for fact in facts
        ),
        "researchNeeded": sum(
            fact.get("disposition") == "research-needed" for fact in facts
        ),
        "pending": sum(fact.get("disposition") == "pending" for fact in facts),
    }


def _generated_keypoint_count_projection(repo_root: Path) -> dict:
    counts = {}
    for slug in sorted(PILOT_SLUGS):
        path = repo_root / "data" / "concepts" / f"{slug}.json"
        detail = json.loads(path.read_text(encoding="utf-8"))
        keypoints = detail.get("keyPoints") if isinstance(detail, dict) else None
        counts[slug] = len(keypoints) if isinstance(keypoints, list) else None
    return {"status": "pass", "checked": len(PILOT_SLUGS), "counts": counts}


def _generated_reference_url_projection(repo_root: Path) -> dict:
    urls: list[str] = []
    invalid = 0
    for slug in sorted(PILOT_SLUGS):
        path = repo_root / "data" / "concepts" / f"{slug}.json"
        detail = json.loads(path.read_text(encoding="utf-8"))
        links = detail.get("externalLinks") if isinstance(detail, dict) else None
        if not isinstance(links, list):
            invalid += 1
            continue
        for link in links:
            url = link.get("url") if isinstance(link, dict) else None
            if not isinstance(url, str):
                invalid += 1
                continue
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                invalid += 1
            urls.append(url)
    return {
        "checked": len(urls),
        "invalid": invalid,
        "requiredExactUrls": list(REQUIRED_EXACT_DOI_URLS),
        "requiredPresent": [
            required_url in urls for required_url in REQUIRED_EXACT_DOI_URLS
        ],
    }


def _phase1_verification_findings(
    report: dict,
    notes: dict[str, NoteRecord],
    batch_path: str,
) -> list[Finding]:
    """Validate/recompute final Phase 1 metadata for coherent pilot evidence."""
    if set(notes) != PILOT_SLUGS:
        return []
    repo_root = _coherent_pilot_repo_root(notes)
    if repo_root is None:
        return [
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "Fixed-pilot Phase 1 metadata has no coherent checkout root.",
            )
        ]
    findings: list[Finding] = []
    verification = report.get("phase1Verification")
    if not isinstance(verification, dict):
        return [
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "Checked-in final evidence requires phase1Verification metadata.",
            )
        ]

    derived_manual_queue = _derived_manual_review_fact_ids(report)
    if (
        derived_manual_queue != sorted(EXPECTED_MANUAL_REVIEW_FACT_IDS)
        or verification.get("manualQueue") != derived_manual_queue
    ):
        findings.append(
            Finding(
                "error",
                "evidence-manual-queue-mismatch",
                batch_path,
                "The reviewed Phase 1 manual queue must contain the exact four fact IDs.",
            )
        )

    expected_fact_coverage = _phase1_fact_coverage(report)
    if verification.get("factCoverage") != expected_fact_coverage:
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "phase1Verification factCoverage does not match fact dispositions.",
            )
        )

    report_notes = [
        entry for entry in report.get("notes", []) if isinstance(entry, dict)
    ]
    expected_review_gate = {
        "status": report.get("status"),
        "verifiedNotes": sum(
            entry.get("status") == "verified" for entry in report_notes
        ),
        "manualReviewNotes": sum(
            entry.get("status") == "manual-review" for entry in report_notes
        ),
        "phase2Started": False,
    }
    if verification.get("reviewGate") != expected_review_gate:
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "phase1Verification reviewGate does not match note/root status.",
            )
        )
    if verification.get("status") != report.get("status"):
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "phase1Verification status must match batch status.",
            )
        )
    if verification.get("loginQueue") != []:
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "Phase 1 loginQueue must remain empty.",
            )
        )

    lint = verification.get("lint")
    if not isinstance(lint, dict):
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                "phase1Verification lint result must be an object.",
            )
        )
    else:
        lint_output = lint.get("rawOutput")
        lint_exit_code = lint.get("exitCode")
        lint_findings = validate_lint_baseline(
            lint_output,
            lint_exit_code,
            path=batch_path,
        )
        findings.extend(lint_findings)
        parsed_lint = parse_lint_result(lint_output, lint_exit_code)
        stored_projection = {
            field: lint.get(field)
            for field in (
                "exitCode",
                "errorCount",
                "warningCount",
                "errors",
                "pilotErrors",
            )
        }
        if parsed_lint is None or stored_projection != parsed_lint:
            findings.append(
                Finding(
                    "error",
                    "evidence-phase1-verification",
                    batch_path,
                    "Stored lint counters/errors do not match parsed rawOutput.",
                )
            )

    findings.extend(
        validate_generated_manifest(
            verification.get("generatedManifest"),
            repo_root,
        )
    )
    try:
        expected_keypoints = _generated_keypoint_count_projection(repo_root)
        expected_urls = _generated_reference_url_projection(repo_root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        findings.append(
            Finding(
                "error",
                "evidence-phase1-verification",
                batch_path,
                f"Cannot recompute generated Phase 1 metadata: {error}.",
            )
        )
    else:
        if verification.get("generatedKeyPoints") != expected_keypoints:
            findings.append(
                Finding(
                    "error",
                    "evidence-phase1-verification",
                    batch_path,
                    "Stored generated keyPoint counts are stale.",
                )
            )
        if verification.get("referenceUrls") != expected_urls:
            findings.append(
                Finding(
                    "error",
                    "evidence-phase1-verification",
                    batch_path,
                    "Stored generated reference URL checks are stale.",
                )
            )
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

    batch_status = report.get("status")
    if not _is_string_member(batch_status, BATCH_STATUSES):
        findings.append(
            Finding(
                "error",
                "evidence-status",
                batch_path,
                f"Batch field 'status' must be one of {sorted(BATCH_STATUSES)!r}.",
            )
        )

    report_notes = report.get("notes")
    if not isinstance(report_notes, list):
        findings.append(
            Finding("error", "evidence-notes", batch_path, "Batch notes must be an array.")
        )
        return findings
    findings.extend(_trusted_report_pilot_hash_findings(report, batch_path))
    findings.extend(_trusted_evidence_anchor_findings(report, notes, batch_path))
    findings.extend(_phase1_verification_findings(report, notes, batch_path))
    if set(notes) == PILOT_SLUGS:
        allowed_root_fields = {
            "schemaVersion",
            "batch",
            "scope",
            "status",
            "phase1Verification",
            "notes",
        }
        extra_root_fields = sorted(set(report) - allowed_root_fields)
        if extra_root_fields:
            findings.append(
                Finding(
                    "error",
                    "evidence-phase1-verification",
                    batch_path,
                    "Unchecked batch root fields are not allowed: "
                    + ", ".join(extra_root_fields)
                    + ".",
                )
            )

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
        "baselineEvidenceSha256",
        "factUnits",
        "sourceStatus",
        "status",
        "rewrittenSummary",
        "summaryBulletEvidence",
        "coverageEvidenceSha256",
        "validation",
    }
    has_unsupported_batch_bullet = False

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
        if not _is_string_member(note_type, NOTE_TYPES):
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
        if not _is_string_member(source_status, SOURCE_STATUSES):
            findings.append(
                Finding(
                    "error",
                    "evidence-source-status",
                    path,
                    f"Unsupported source status {source_status!r}.",
                )
            )
        note_status = entry.get("status")
        if not _is_string_member(note_status, NOTE_STATUSES):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-status",
                    path,
                    f"Unsupported note status {note_status!r}.",
                )
            )
        rewritten_summary = entry.get("rewrittenSummary")
        if not isinstance(entry.get("originalSummary"), str):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    path,
                    "originalSummary must be a string.",
                )
            )
        if not isinstance(rewritten_summary, str):
            findings.append(
                Finding(
                    "error",
                    "evidence-note-schema",
                    path,
                    "rewrittenSummary must be a string.",
                )
            )
            rewritten_summary = ""
        is_rewritten = bool(rewritten_summary)
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
        baseline_digest = entry.get("baselineEvidenceSha256")
        baseline_digest_valid = (
            isinstance(baseline_digest, str)
            and SHA256_RE.fullmatch(baseline_digest) is not None
            and baseline_digest == _baseline_evidence_sha256(entry)
        )
        if not baseline_digest_valid:
            findings.append(
                Finding(
                    "error",
                    "evidence-baseline-digest-mismatch",
                    path,
                    (
                        "baselineEvidenceSha256 must match originalSummary and the stable "
                        "fact id/text/sourceRefs ledger."
                    ),
                )
            )
        coverage_digest = entry.get("coverageEvidenceSha256")
        coverage_digest_valid = (
            isinstance(coverage_digest, str)
            and SHA256_RE.fullmatch(coverage_digest) is not None
            and coverage_digest == _coverage_evidence_sha256(entry)
        )
        if not coverage_digest_valid:
            findings.append(
                Finding(
                    "error",
                    "evidence-coverage-digest-mismatch",
                    path,
                    (
                        "coverageEvidenceSha256 must match rewrittenSummary, fact "
                        "dispositions, and summaryBulletEvidence."
                    ),
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
            if not is_rewritten and original_hash != note.sha256:
                findings.append(
                    Finding(
                        "error",
                        "evidence-hash-mismatch",
                        path,
                        "Current note SHA-256 differs from originalSha256.",
                    )
                )
            if not is_rewritten and entry.get("originalSummary") != note.original_summary:
                findings.append(
                    Finding(
                        "error",
                        "evidence-summary-mismatch",
                        path,
                        "originalSummary is not a lossless snapshot of the current note.",
                    )
                )
            if is_rewritten and rewritten_summary != note.original_summary:
                findings.append(
                    Finding(
                        "error",
                        "evidence-rewritten-summary-mismatch",
                        path,
                        "rewrittenSummary is not a lossless snapshot of the current note Summary.",
                    )
                )
            if is_rewritten:
                findings.extend(validate_summary(note))

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
        has_research_needed = False
        has_manual_review = False
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
            if not _is_string_member(disposition, FACT_DISPOSITIONS):
                findings.append(
                    Finding(
                        "error",
                        "fact-disposition",
                        path,
                        f"Fact unit {fact_id!r} has unsupported disposition {disposition!r}.",
                    )
                )
            if disposition == "research-needed":
                has_research_needed = True
            if disposition == "manual-review":
                has_manual_review = True
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
            if disposition != "research-needed" and disposition != "manual-review" and (
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
        summary_bullet_evidence = entry.get("summaryBulletEvidence")
        actual_bullets = _summary_bullet_lines(note) if note is not None else []
        unsupported_bullet_count = 0
        coverage_mapping_complete = not is_rewritten
        summary_evidence_refs_defined = True
        if not isinstance(summary_bullet_evidence, list):
            findings.append(
                Finding(
                    "error",
                    "summary-bullet-evidence-schema",
                    path,
                    "summaryBulletEvidence must be an array.",
                )
            )
            unsupported_bullet_count = len(actual_bullets) if is_rewritten else 0
            coverage_mapping_complete = False
            summary_evidence_refs_defined = False
        elif not is_rewritten:
            if summary_bullet_evidence:
                findings.append(
                    Finding(
                        "error",
                        "summary-bullet-evidence-schema",
                        path,
                        "A pre-edit baseline must have empty summaryBulletEvidence.",
                    )
                )
                coverage_mapping_complete = False
        else:
            mapped_fact_ids: list[str] = []
            evidence_schema_valid = True
            if len(summary_bullet_evidence) != len(actual_bullets):
                findings.append(
                    Finding(
                        "error",
                        "summary-bullet-evidence",
                        path,
                        (
                            "summaryBulletEvidence count must equal the actual top-level "
                            "Summary bullet count."
                        ),
                    )
                )
            for bullet_index, bullet_line in enumerate(actual_bullets, start=1):
                expected_id = f"{slug}-s{bullet_index:02d}"
                if bullet_index > len(summary_bullet_evidence):
                    unsupported_bullet_count += 1
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-unsupported",
                            path,
                            f"Actual Summary bullet {expected_id!r} has no evidence record.",
                        )
                    )
                    continue
                evidence = summary_bullet_evidence[bullet_index - 1]
                if not isinstance(evidence, dict):
                    evidence_schema_valid = False
                    unsupported_bullet_count += 1
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-evidence-schema",
                            path,
                            f"Summary bullet evidence {expected_id!r} must be an object.",
                        )
                    )
                    continue
                evidence_id = evidence.get("id")
                bullet_sha256 = evidence.get("sha256")
                fact_ids = evidence.get("factIds")
                source_refs = evidence.get("sourceRefs")
                if evidence_id != expected_id:
                    evidence_schema_valid = False
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-evidence-schema",
                            path,
                            f"Summary bullet evidence at position {bullet_index} must use {expected_id!r}.",
                        )
                    )
                expected_bullet_sha256 = hashlib.sha256(
                    bullet_line.encode("utf-8")
                ).hexdigest()
                if bullet_sha256 != expected_bullet_sha256:
                    unsupported_bullet_count += 1
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-unsupported",
                            path,
                            (
                                f"Actual Summary bullet {expected_id!r} does not match its "
                                "approved evidence digest."
                            ),
                        )
                    )
                refs_valid = (
                    isinstance(source_refs, list)
                    and all(isinstance(source_ref, str) and source_ref for source_ref in source_refs)
                    and len(source_refs) == len(set(source_refs))
                )
                if not refs_valid or source_refs != _ordered_footnote_refs(bullet_line):
                    evidence_schema_valid = False
                    summary_evidence_refs_defined = False
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-source-refs",
                            path,
                            (
                                f"Summary bullet evidence {expected_id!r} sourceRefs must "
                                "exactly match its inline footnote references."
                            ),
                        )
                    )
                elif note is not None and any(
                    source_ref not in note.footnote_defs for source_ref in source_refs
                ):
                    summary_evidence_refs_defined = False
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-source-undefined",
                            path,
                            f"Summary bullet evidence {expected_id!r} maps to an undefined footnote.",
                        )
                    )
                fact_ids_valid = (
                    isinstance(fact_ids, list)
                    and all(isinstance(fact_id, str) and fact_id for fact_id in fact_ids)
                    and len(fact_ids) == len(set(fact_ids))
                )
                if not fact_ids_valid:
                    evidence_schema_valid = False
                    findings.append(
                        Finding(
                            "error",
                            "summary-bullet-fact-coverage",
                            path,
                            (
                                f"Summary bullet evidence {expected_id!r} factIds must be "
                                "unique non-empty strings."
                            ),
                        )
                    )
                else:
                    mapped_fact_ids.extend(fact_ids)
                    unknown_fact_ids = sorted(set(fact_ids) - seen_fact_ids)
                    if unknown_fact_ids:
                        evidence_schema_valid = False
                        findings.append(
                            Finding(
                                "error",
                                "summary-bullet-fact-coverage",
                                path,
                                (
                                    f"Summary bullet evidence {expected_id!r} maps unknown "
                                    f"fact IDs: {', '.join(unknown_fact_ids)}."
                                ),
                            )
                        )
            if len(summary_bullet_evidence) > len(actual_bullets):
                evidence_schema_valid = False
                findings.append(
                    Finding(
                        "error",
                        "summary-bullet-evidence",
                        path,
                        "summaryBulletEvidence contains records with no actual Summary bullet.",
                    )
                )
            mapped_fact_id_set = set(mapped_fact_ids)
            duplicate_mapped_fact_ids = sorted(
                fact_id
                for fact_id in mapped_fact_id_set
                if mapped_fact_ids.count(fact_id) > 1
            )
            missing_mapped_fact_ids = sorted(seen_fact_ids - mapped_fact_id_set)
            if duplicate_mapped_fact_ids or missing_mapped_fact_ids:
                evidence_schema_valid = False
                details = []
                if missing_mapped_fact_ids:
                    details.append("missing " + ", ".join(missing_mapped_fact_ids))
                if duplicate_mapped_fact_ids:
                    details.append("duplicated " + ", ".join(duplicate_mapped_fact_ids))
                findings.append(
                    Finding(
                        "error",
                        "summary-bullet-fact-coverage",
                        path,
                        "Fact-to-bullet mapping is incomplete: " + "; ".join(details) + ".",
                    )
                )
            coverage_mapping_complete = (
                evidence_schema_valid
                and unsupported_bullet_count == 0
                and mapped_fact_id_set == seen_fact_ids
                and not duplicate_mapped_fact_ids
            )
        has_unsupported_batch_bullet = (
            has_unsupported_batch_bullet or unsupported_bullet_count > 0
        )
        validation = entry.get("validation")
        if isinstance(validation, dict):
            valid_fact_units = [fact for fact in fact_units if isinstance(fact, dict)]
            expected_validation = {
                "hashMatches": (
                    baseline_digest_valid
                    if is_rewritten
                    else note is not None and original_hash == note.sha256
                ),
                "losslessSummaryMatches": (
                    baseline_digest_valid
                    if is_rewritten
                    else note is not None and entry.get("originalSummary") == note.original_summary
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
                    and summary_evidence_refs_defined
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
                "newUnsupportedFacts": unsupported_bullet_count,
            }
            if is_rewritten:
                summary_findings = validate_summary(note) if note is not None else []
                expected_validation.update(
                    {
                        "structure": (
                            "pass"
                            if not any(
                                finding.code != "footnote-undefined"
                                for finding in summary_findings
                            )
                            else "fail"
                        ),
                        "footnotes": (
                            "pass"
                            if not any(
                                finding.code == "footnote-undefined"
                                for finding in summary_findings
                            )
                            else "fail"
                        ),
                        "factCoverage": (
                            "pass"
                            if all(
                                fact.get("disposition") == "covered"
                                for fact in valid_fact_units
                            )
                            and len(valid_fact_units) == len(fact_units)
                            and coverage_mapping_complete
                            and unsupported_bullet_count == 0
                            else "fail"
                        ),
                    }
                )
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
        has_unresolved = (
            has_research_needed
            or has_manual_review
            or unsupported_bullet_count > 0
        )
        if _is_string_member(source_status, SOURCE_STATUSES):
            if is_rewritten and (has_manual_review or unsupported_bullet_count > 0):
                source_status_matches_facts = source_status == "conflict"
            elif is_rewritten and has_research_needed:
                source_status_matches_facts = source_status == "research-needed"
            elif is_rewritten:
                source_status_matches_facts = source_status in {
                    "existing-sufficient",
                    "researched",
                }
            elif has_unresolved:
                source_status_matches_facts = source_status in {
                    "research-needed",
                    "conflict",
                }
            else:
                source_status_matches_facts = source_status == "existing-sufficient"
            if not source_status_matches_facts:
                findings.append(
                    Finding(
                        "error",
                        "evidence-source-status",
                        path,
                        (
                            "Manual-review facts require conflict sourceStatus."
                            if has_manual_review
                            else "Research-needed facts require research-needed sourceStatus."
                            if has_research_needed
                            else (
                                "Resolved rewritten facts require existing-sufficient or "
                                "researched sourceStatus."
                            )
                            if is_rewritten
                            else "Resolved baseline facts require existing-sufficient sourceStatus."
                        ),
                    )
                )
        expected_note_status = (
            "manual-review"
            if has_manual_review or unsupported_bullet_count > 0
            else "research-needed"
            if has_research_needed
            else "verified"
            if is_rewritten
            else "pending"
        )
        if _is_string_member(note_status, NOTE_STATUSES) and note_status != expected_note_status:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-status",
                    path,
                    (
                        f"Fact dispositions require {expected_note_status!r} "
                        "baseline note status."
                    ),
                )
            )
    valid_entries = [entry for entry in report_notes if isinstance(entry, dict)]
    all_rewritten = (
        len(valid_entries) == len(report_notes)
        and bool(valid_entries)
        and all(
            isinstance(entry.get("rewrittenSummary"), str)
            and bool(entry["rewrittenSummary"])
            for entry in valid_entries
        )
    )
    all_facts = [
        fact
        for entry in valid_entries
        if isinstance(entry.get("factUnits"), list)
        for fact in entry["factUnits"]
        if isinstance(fact, dict)
    ]
    has_pending_batch_fact = any(
        fact.get("disposition") == "pending" for fact in all_facts
    )
    has_unresolved_batch_fact = any(
        fact.get("disposition") == "research-needed"
        or fact.get("disposition") == "manual-review"
        for fact in all_facts
    )
    expected_batch_status = (
        "baseline"
        if has_pending_batch_fact or not all_rewritten
        else "needs-review"
        if has_unresolved_batch_fact or has_unsupported_batch_bullet
        else "verified"
    )
    if _is_string_member(batch_status, BATCH_STATUSES) and batch_status != expected_batch_status:
        findings.append(
            Finding(
                "error",
                "evidence-status",
                batch_path,
                f"Batch content requires status {expected_batch_status!r}.",
            )
        )
    return findings


def _inventory_finding(code: str, path: str, message: str) -> Finding:
    return Finding(severity="error", code=code, path=path, message=message)


def validate_inventory(inventory: object) -> list[Finding]:
    """Validate the closed Phase 1 inventory schema and enum values."""
    findings: list[Finding] = []
    if not isinstance(inventory, dict):
        return [
            _inventory_finding(
                "inventory-root",
                "inventory.json",
                "Inventory root must be an object.",
            )
        ]
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

    if len(entries) != EXPECTED_NR_NOTE_COUNT:
        findings.append(
            _inventory_finding(
                "inventory-count",
                "inventory.json",
                f"Phase 1 inventory must contain exactly {EXPECTED_NR_NOTE_COUNT} notes.",
            )
        )
    valid_slugs = [
        entry.get("slug")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    ]
    if (
        len(NOTE_TYPE_OVERRIDES) != EXPECTED_NR_NOTE_COUNT
        or set(valid_slugs) != set(NOTE_TYPE_OVERRIDES)
    ):
        findings.append(
            _inventory_finding(
                "inventory-override-completeness",
                "inventory.json",
                "Inventory slugs must exactly equal the reviewed note-type override map.",
            )
        )
    batch_00_count = sum(
        isinstance(entry, dict) and entry.get("batch") == "batch-00"
        for entry in entries
    )
    unassigned_count = sum(
        isinstance(entry, dict) and entry.get("batch") == "unassigned"
        for entry in entries
    )
    assigned_count = len(entries) - batch_00_count - unassigned_count
    phase1_split = (
        batch_00_count == EXPECTED_BATCH_00_COUNT
        and unassigned_count == EXPECTED_UNASSIGNED_COUNT
        and assigned_count == 0
    )
    phase2_split = (
        batch_00_count == EXPECTED_BATCH_00_COUNT
        and unassigned_count == 0
        and assigned_count == EXPECTED_UNASSIGNED_COUNT
    )
    if not (phase1_split or phase2_split):
        findings.append(
            _inventory_finding(
                "inventory-batch-counts",
                "inventory.json",
                (
                    f"Inventory must have {EXPECTED_BATCH_00_COUNT} batch-00 "
                    f"pilots and either {EXPECTED_UNASSIGNED_COUNT} unassigned "
                    "or assigned non-pilots."
                ),
            )
        )

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
        if not _is_string_member(entry.get("type"), NOTE_TYPES):
            findings.append(
                _inventory_finding(
                    "inventory-type",
                    path,
                    f"Unsupported note type: {entry.get('type')!r}.",
                )
            )
        slug = entry.get("slug")
        expected_type = NOTE_TYPE_OVERRIDES.get(slug) if isinstance(slug, str) else None
        if expected_type is not None and entry.get("type") != expected_type:
            findings.append(
                _inventory_finding(
                    "inventory-override-completeness",
                    path,
                    f"Inventory type for {slug!r} must equal reviewed override {expected_type!r}.",
                )
            )
        if not _is_string_member(entry.get("status"), NOTE_STATUSES):
            findings.append(
                _inventory_finding(
                    "inventory-status",
                    path,
                    f"Unsupported note status: {entry.get('status')!r}.",
                )
            )
        if not _is_string_member(entry.get("sourceStatus"), SOURCE_STATUSES):
            findings.append(
                _inventory_finding(
                    "inventory-source-status",
                    path,
                    f"Unsupported source status: {entry.get('sourceStatus')!r}.",
                )
            )
        if not _is_inventory_batch(entry.get("batch")):
            findings.append(
                _inventory_finding(
                    "inventory-batch",
                    path,
                    f"Unsupported inventory batch: {entry.get('batch')!r}.",
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
    inventory: object,
    notes: dict[str, NoteRecord],
) -> list[Finding]:
    """Validate inventory coverage against reviewed pilot and current nonpilot hashes."""
    findings = validate_inventory(inventory)
    if not isinstance(inventory, dict):
        return findings
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
    if len(nr_notes) != EXPECTED_NR_NOTE_COUNT:
        findings.append(
            _inventory_finding(
                "inventory-count",
                "inventory.json",
                f"Current NR scope must contain exactly {EXPECTED_NR_NOTE_COUNT} notes.",
            )
        )
    if set(nr_notes) != set(NOTE_TYPE_OVERRIDES):
        findings.append(
            _inventory_finding(
                "inventory-override-completeness",
                "inventory.json",
                "Current NR slugs must exactly equal the reviewed note-type override map.",
            )
        )
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
        if slug in PILOT_SLUGS:
            trusted_hash = TRUSTED_PILOT_ORIGINAL_SHA256.get(slug)
            if trusted_hash is None or entry.get("originalSha256") != trusted_hash:
                findings.append(
                    _inventory_finding(
                        "inventory-trusted-baseline-mismatch",
                        expected_path,
                        (
                            f"Inventory hash for {slug} does not match the "
                            "independently reviewed pilot baseline."
                        ),
                    )
                )
        elif entry.get("originalSha256") != note.sha256:
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
        entry["slug"]
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("batch") == "batch-00"
        and isinstance(entry.get("slug"), str)
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


def _apply_trusted_inventory_hashes(
    generated: dict,
    immutable_hash_slugs: frozenset[str],
) -> dict:
    """Apply code-owned pre-edit hashes to a generated inventory projection."""
    generated_entries = generated.get("notes")
    if not isinstance(generated_entries, list):
        return generated
    for entry in generated_entries:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug")
        if slug not in immutable_hash_slugs:
            continue
        trusted_hash = TRUSTED_PILOT_ORIGINAL_SHA256.get(slug)
        if trusted_hash is not None:
            entry["originalSha256"] = trusted_hash
    return generated


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


def _inventory_counts(report: object) -> tuple[int, int, int, int, int]:
    if not isinstance(report, dict):
        return 0, 0, 0, 0, 0
    entries = report.get("notes", [])
    if not isinstance(entries, list):
        return 0, 0, 0, 0, 0
    slugs = [
        entry.get("slug")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    ]
    duplicates = len(slugs) - len(set(slugs))
    unclassified = sum(
        1
        for entry in entries
        if not isinstance(entry, dict)
        or not _is_string_member(entry.get("type"), NOTE_TYPES)
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


def _inventory_hash_anchor_findings(
    report: dict,
    inventory: dict,
    inventory_path: Path,
) -> list[Finding]:
    findings: list[Finding] = []
    report_entries = report.get("notes") if isinstance(report, dict) else None
    inventory_entries = inventory.get("notes") if isinstance(inventory, dict) else None
    if not isinstance(report_entries, list) or not isinstance(inventory_entries, list):
        return findings
    inventory_by_slug = {
        entry.get("slug"): entry
        for entry in inventory_entries
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    for entry in report_entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("slug"), str):
            continue
        slug = entry["slug"]
        inventory_entry = inventory_by_slug.get(slug)
        if inventory_entry is None:
            continue
        inventory_hash = inventory_entry.get("originalSha256")
        hash_matches = (
            isinstance(inventory_hash, str)
            and SHA256_RE.fullmatch(inventory_hash) is not None
            and entry.get("originalSha256") == inventory_hash
        )
        if not isinstance(inventory_hash, str) or not SHA256_RE.fullmatch(inventory_hash):
            findings.append(
                Finding(
                    "error",
                    "evidence-inventory-hash-missing",
                    inventory_path.as_posix(),
                    f"Inventory pilot {slug!r} lacks a valid originalSha256 anchor.",
                )
            )
        elif not hash_matches:
            findings.append(
                Finding(
                    "error",
                    "evidence-inventory-hash-mismatch",
                    inventory_path.as_posix(),
                    (
                        f"Batch originalSha256 for {slug!r} does not match the "
                        "checked-in inventory anchor."
                    ),
                )
            )
        validation = entry.get("validation")
        if isinstance(validation, dict) and validation.get("hashMatches") != hash_matches:
            findings.append(
                Finding(
                    "error",
                    "evidence-validation",
                    str(slug),
                    "Stale or invalid validation fields: hashMatches.",
                )
            )
    return findings


def _trusted_report_pilot_hash_findings(
    report: dict,
    path: str,
) -> list[Finding]:
    """Bind a complete fixed-pilot report to the reviewed code trust map."""
    report_entries = report.get("notes") if isinstance(report, dict) else None
    if not isinstance(report_entries, list):
        return []
    report_by_slug = {
        entry.get("slug"): entry
        for entry in report_entries
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    if set(report_by_slug) != PILOT_SLUGS:
        return []
    findings: list[Finding] = []
    for slug, trusted_hash in sorted(TRUSTED_PILOT_ORIGINAL_SHA256.items()):
        if report_by_slug[slug].get("originalSha256") != trusted_hash:
            findings.append(
                Finding(
                    "error",
                    "evidence-trusted-baseline-mismatch",
                    path,
                    (
                        f"Pilot {slug!r} originalSha256 differs from the "
                        "independently reviewed code trust anchor."
                    ),
                )
            )
    return findings


def _trusted_pilot_hash_anchor_findings(
    report: dict,
    inventory: dict,
    inventory_path: Path,
) -> list[Finding]:
    """Bind both mutable evidence files to the code-owned reviewed baselines."""
    report_entries = report.get("notes") if isinstance(report, dict) else None
    inventory_entries = inventory.get("notes") if isinstance(inventory, dict) else None
    if not isinstance(report_entries, list) or not isinstance(inventory_entries, list):
        return []
    inventory_by_slug = {
        entry.get("slug"): entry
        for entry in inventory_entries
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str)
    }
    findings = _trusted_report_pilot_hash_findings(
        report,
        inventory_path.as_posix(),
    )
    for slug, trusted_hash in sorted(TRUSTED_PILOT_ORIGINAL_SHA256.items()):
        inventory_entry = inventory_by_slug.get(slug)
        if not isinstance(inventory_entry, dict) or inventory_entry.get(
            "originalSha256"
        ) != trusted_hash:
            findings.append(
                Finding(
                    "error",
                    "evidence-trusted-baseline-mismatch",
                    inventory_path.as_posix(),
                    (
                        f"Pilot {slug!r} originalSha256 differs from the "
                        "independently reviewed code trust anchor."
                    ),
                )
            )
    return findings


def _load_batch_notes(
    report_path: Path,
    report: dict | None = None,
) -> tuple[dict[str, NoteRecord], list[Finding]]:
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
    batch_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("batch") == "batch-00"
    ]
    pilot_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict)
        and _is_string_member(entry.get("slug"), PILOT_SLUGS)
    ]
    batch_slugs = [
        entry.get("slug")
        for entry in batch_entries
        if isinstance(entry.get("slug"), str)
    ]
    pilot_slugs = [entry["slug"] for entry in pilot_entries]
    exact_membership = (
        len(batch_entries) == len(PILOT_SLUGS)
        and len(batch_slugs) == len(PILOT_SLUGS)
        and len(set(batch_slugs)) == len(PILOT_SLUGS)
        and set(batch_slugs) == PILOT_SLUGS
        and len(pilot_entries) == len(PILOT_SLUGS)
        and len(set(pilot_slugs)) == len(PILOT_SLUGS)
        and all(entry.get("batch") == "batch-00" for entry in pilot_entries)
    )
    if not exact_membership:
        return {}, [
            Finding(
                "error",
                "evidence-inventory-membership",
                inventory_path.as_posix(),
                "Inventory does not define the exact fixed pilot membership.",
            )
        ]

    anchor_findings = (
        _inventory_hash_anchor_findings(report, inventory, inventory_path)
        if report is not None
        else []
    )

    for entry in pilot_entries:
        slug = entry["slug"]
        expected_path = (Path("vault") / "concepts" / f"{slug}.md").as_posix()
        if entry.get("path") != expected_path:
            return {}, [
                Finding(
                    "error",
                    "evidence-inventory-path",
                    inventory_path.as_posix(),
                    (
                        f"Pilot {slug!r} must use canonical inventory path "
                        f"{expected_path!r}."
                    ),
                )
            ]

    repo_root: Path | None = None
    for candidate in report_path.resolve().parents:
        if all(
            (candidate / "vault" / "concepts" / f"{slug}.md").is_file()
            for slug in PILOT_SLUGS
        ):
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
    findings: list[Finding] = list(anchor_findings)
    resolved_repo_root = repo_root.resolve()
    concepts_root = (resolved_repo_root / "vault" / "concepts").resolve()
    if not concepts_root.is_relative_to(resolved_repo_root):
        return {}, [
            Finding(
                "error",
                "evidence-inventory-path",
                concepts_root.as_posix(),
                "Canonical vault/concepts directory resolves outside the repository.",
            )
        ]
    _, inventory_notes = _inventory(concepts_root)
    findings.extend(
        validate_inventory_against_notes(
            inventory,
            inventory_notes,
        )
    )
    for entry in sorted(pilot_entries, key=lambda item: item["slug"]):
        slug = entry["slug"]
        canonical_path = repo_root / "vault" / "concepts" / f"{slug}.md"
        try:
            note_path = canonical_path.resolve(strict=True)
            if not note_path.is_relative_to(concepts_root) or note_path.parent != concepts_root:
                findings.append(
                    Finding(
                        "error",
                        "evidence-inventory-path",
                        canonical_path.as_posix(),
                        f"Pilot note {slug!r} resolves outside vault/concepts.",
                    )
                )
                continue
            note = parse_note(note_path)
            if note.slug != slug:
                findings.append(
                    Finding(
                        "error",
                        "evidence-inventory-slug-mismatch",
                        note_path.as_posix(),
                        (
                            f"Parsed note slug {note.slug!r} does not match "
                            f"inventory slug {slug!r}."
                        ),
                    )
                )
                continue
            notes[slug] = note
        except (OSError, UnicodeDecodeError) as error:
            findings.append(
                Finding(
                    "error",
                    "evidence-note-unreadable",
                    note_path.as_posix(),
                    f"Cannot read pilot note: {error}.",
                )
            )
    findings.extend(
        _trusted_pilot_hash_anchor_findings(
            report if report is not None else {},
            inventory,
            inventory_path,
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

    validate_assignment = commands.add_parser(
        "validate-assignment",
        help="Validate a Phase 2 assignment through an explicit repository root.",
    )
    validate_assignment.add_argument("--repo-root", type=Path, required=True)
    validate_assignment.add_argument("--inventory", required=True)
    validate_assignment.add_argument("--assignment", required=True)

    validate_baseline = commands.add_parser(
        "validate-baseline",
        help="Validate one Phase 2 baseline lock.",
    )
    validate_baseline.add_argument("--repo-root", type=Path, required=True)
    validate_baseline.add_argument("--assignment", required=True)
    validate_baseline.add_argument("--batch", required=True)

    validate_batch = commands.add_parser(
        "validate-batch", help="Validate a source-mapped batch evidence report."
    )
    validate_batch.add_argument("path", type=Path, nargs="?")
    validate_batch.add_argument("--repo-root", type=Path)
    validate_batch.add_argument("--assignment")
    validate_batch.add_argument("--batch")
    validate_batch.add_argument(
        "--allow-pending",
        action="store_true",
        help="Permit pending fact dispositions in a pre-edit baseline.",
    )
    validate_batch.add_argument(
        "--check-source-hashes",
        action="store_true",
        help="Run the explicit pre-edit source hash and lossless Summary snapshot gate.",
    )
    validate_batch.add_argument("--check-generated", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inventory":
        expected, notes = _inventory(args.root)
        expected = _apply_trusted_inventory_hashes(
            expected,
            PILOT_SLUGS,
        )
        if args.check:
            if not args.output.is_file():
                print(f"Inventory output does not exist: {args.output}")
                return 1
            try:
                report = json.loads(args.output.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                _print_findings(
                    [
                        _inventory_finding(
                            "inventory-json-invalid",
                            args.output.as_posix(),
                            f"Cannot read inventory JSON: {error}.",
                        )
                    ]
                )
                return 1
            findings = validate_inventory_against_notes(
                report,
                notes,
            )
            checked_expected = expected
            assignment_path = args.output.with_name("phase2-assignment.json")
            if assignment_path.is_file():
                try:
                    assignment = json.loads(
                        assignment_path.read_text(encoding="utf-8")
                    )
                except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                    findings.append(
                        Finding(
                            "error",
                            "phase2-assignment-membership",
                            assignment_path.as_posix(),
                            f"Cannot read Phase 2 assignment JSON: {error}.",
                        )
                    )
                else:
                    expected_assignment = build_phase2_assignment(expected)
                    checked_expected = synchronize_phase2_inventory(
                        expected, expected_assignment
                    )
                    findings.extend(
                        validate_phase2_assignment(assignment, report)
                    )
            if report != checked_expected:
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
        findings = validate_inventory_against_notes(
            report,
            notes,
        )
        if findings:
            _print_inventory_counts(report)
            _print_findings(findings)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _print_inventory_counts(report)
        return 0
    if args.command == "validate-note":
        findings = validate_summary(parse_note(args.path))
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    if args.command == "validate-assignment":
        inventory = None
        assignment = None
        try:
            inventory_file = _resolve_phase2_path(
                args.repo_root,
                args.inventory,
                display_path=args.inventory,
            )
            assignment_file = _resolve_phase2_path(
                args.repo_root,
                args.assignment,
                display_path=args.assignment,
            )
            inventory = _read_phase2_json(
                inventory_file, Path(args.inventory)
            )
            assignment = _read_phase2_json(
                assignment_file, Path(args.assignment)
            )
            assert inventory is not None and assignment is not None
            findings = validate_phase2_assignment(assignment, inventory)
        except Phase2LoadError as error:
            findings = [error.finding()]
        if isinstance(inventory, dict) and isinstance(assignment, dict):
            _print_phase2_assignment_counts(assignment, inventory)
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    if args.command == "validate-baseline":
        try:
            if _phase2_path_parts(args.assignment) is None:
                raise Phase2LoadError(
                    "phase2-path-invalid",
                    "phase2-assignment.json",
                    "--assignment must be a repo-relative POSIX path.",
                )
            context = load_phase2_batch(
                args.repo_root, Path(args.assignment), args.batch
            )
            findings = validate_baseline_lock(context)
            findings.extend(
                _validate_phase2_source_state(context, pre_edit=True)
            )
        except Phase2LoadError as error:
            findings = [error.finding()]
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    if args.command == "validate-batch":
        explicit_phase2 = any((args.repo_root, args.assignment, args.batch))
        if explicit_phase2:
            try:
                if not all((args.repo_root, args.assignment, args.batch)):
                    raise Phase2LoadError(
                        "phase2-path-invalid",
                        "phase2-assignment.json",
                        "Phase 2 validation requires --repo-root, --assignment, and --batch.",
                    )
                if _phase2_path_parts(args.assignment) is None:
                    raise Phase2LoadError(
                        "phase2-path-invalid",
                        "phase2-assignment.json",
                        "--assignment must be a repo-relative POSIX path.",
                    )
                context = load_phase2_batch(
                    args.repo_root, Path(args.assignment), args.batch
                )
                findings = validate_phase2_batch(
                    context,
                    check_source_hashes=args.check_source_hashes,
                    check_generated=args.check_generated,
                )
            except Phase2LoadError as error:
                findings = [error.finding()]
            _print_findings(findings)
            return 1 if _findings_have_errors(findings) else 0
        if args.path is None:
            _print_findings(
                [
                    Finding(
                        "error",
                        "evidence-json-invalid",
                        "batch.json",
                        "Legacy validation requires a batch evidence path.",
                    )
                ]
            )
            return 1
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
        notes, findings = _load_batch_notes(args.path, report)
        findings.extend(validate_evidence(report, notes))
        generated_root, root_findings = _canonical_generated_root(args.path, notes)
        findings.extend(root_findings)
        if generated_root is not None:
            findings.extend(validate_generated_keypoints(generated_root, notes))
            expected_generated_count = (
                EXPECTED_GENERATED_CONCEPT_COUNT
                if generated_root.resolve() == Path(__file__).resolve().parents[1]
                else None
            )
            findings.extend(
                validate_generated_index(
                    generated_root,
                    expected_count=expected_generated_count,
                )
            )
        if not args.allow_pending and not args.check_source_hashes:
            findings.extend(_pending_fact_findings(report))
        _print_batch_counts(report, findings)
        _print_findings(findings)
        return 1 if _findings_have_errors(findings) else 0
    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
