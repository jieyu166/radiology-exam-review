# NR Concept Summary Semantic Restructure Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可稽核的 NR Summary 驗證工具與完整 inventory，並完成 10 篇代表性 NR concepts 的第 0 批語意重組。

**Architecture:** `vault/concepts/*.md` 仍是 source of truth；新的唯讀 audit 工具負責辨識 NR、擷取 Summary 變體、檢查粗體標籤與 footnotes，並驗證批次 evidence JSON。語意改寫由人／agent 逐篇執行，工具只驗證結構與 evidence 完整性，不自動產生醫學事實。第 0 批通過後才另建 Phase 2 計畫處理其餘批次。

**Tech Stack:** Python 3 標準函式庫、Obsidian Markdown、JSON、既有 `scripts/build_concepts.py`、既有 `scripts/lint_concepts.py`、Spectra/OpenSpec。

## Global Constraints

- 範圍只包含 frontmatter `subspecialty: [NR]` 的 216 篇 concepts。
- 疾病型使用「族群／年齡、症狀、病理／機轉、檢查、影像、治療／追蹤、陷阱」中有來源支持的欄位。
- Pattern／鑑別型使用「第一鑑別軸、位置、側別／對稱性、序列／訊號、分布、Pattern → diagnosis、陷阱」中有來源支持的欄位。
- 解剖／量測／分級／處置型依原文使用「結構／範圍、量測、門檻、分級、臨床意義、操作順序、陷阱」。
- 每個改寫後 bullet 必須以粗體標籤開始，且保留有效 footnote reference。
- 只允許重排、合併、拆句與縮寫既有有來源事實；禁止新增無來源結果。
- 不重寫正文、題目、frontmatter、圖片、Dataview、既有 references。
- 額外文獻查證只在來源不足、互相衝突、時效性規則或弱來源無法安全壓縮時啟用。
- 需要受限平台時由使用者自行登入；不得處理帳密、規避存取控制或下載受限 PDF。
- 任何無法確認的事實覆蓋必須標記 `manual-review`，不得視為通過。
- `scripts/lint_concepts.py --quiet` 的既有 baseline 為 2 errors／124 warnings：
  `ceap-classification.md` 的未定義 `[^*]`，以及 `2022-264` JSON 的 `![[...]]`。
  本計畫不得新增 lint error；NR Summary 自身的 footnote／結構檢查仍須零錯誤。
- 不得 stage 或 commit 目前工作樹中既有的題目與覆核筆記變更。

---

## File Map

- Create: `scripts/nr_summary_audit.py`
  - 純標準函式庫的唯讀 parser、validator 與 evidence checker。
- Create: `scripts/test_nr_summary_audit.py`
  - 不依賴 pytest 的 smoke tests，沿用本專案 `scripts/test_import_obsidian_sr.py` 風格。
- Create: `docs/reports/nr-summary-rewrite/inventory.json`
  - 216 篇 NR concept 的穩定排序、類型、批次與狀態。
- Create: `docs/reports/nr-summary-rewrite/batch-00.json`
  - 第 0 批原始事實單元、來源對映、改寫狀態與驗證結果。
- Modify: 10 files listed in Task 4 under `vault/concepts/`.
- Regenerate:
  - `data/concepts/clippers.json`
  - `data/concepts/cerebral-amyloid-angiopathy.json`
  - `data/concepts/craniopharyngioma.json`
  - `data/concepts/basal-ganglia-t1-shortening.json`
  - `data/concepts/cpa-masses.json`
  - `data/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.json`
  - `data/concepts/artery-of-adamkiewicz.json`
  - `data/concepts/aspects-score.json`
  - `data/concepts/acute-stroke-management.json`
  - `data/concepts/dementia-neuroimaging-overview.json`
- Potentially modify: `data/concepts-index.json` only if `scripts/build_concepts.py` produces a real deterministic difference.
- Modify only if calibration changes are approved: `docs/superpowers/specs/2026-07-29-nr-summary-semantic-restructure-design.md`.

### Task 1: NR Summary parser and structural validator

**Files:**
- Create: `scripts/nr_summary_audit.py`
- Create: `scripts/test_nr_summary_audit.py`

**Interfaces:**
- Consumes: UTF-8 Obsidian concept Markdown text and batch evidence JSON.
- Produces:
  - `parse_note(path: Path) -> NoteRecord`
  - `extract_summary_sections(body: str) -> list[SummarySection]`
  - `validate_summary(note: NoteRecord) -> list[Finding]`
  - `validate_evidence(report: dict, notes: dict[str, NoteRecord]) -> list[Finding]`
  - CLI commands `inventory`, `validate-note`, and `validate-batch`.

- [ ] **Step 1: Write parser tests that fail before implementation**

Create `scripts/test_nr_summary_audit.py` with temporary Markdown fixtures covering:

```python
def test_summary_variants_are_extracted():
    text = """---
concepts: [demo]
name: Demo
subspecialty: [NR]
---
# demo

## Summary — 影像
- **影像**：DWI 高訊號。[^1]

## Summary — 陷阱
- **陷阱**：不能只靠單一序列。[^1]

### 參考來源
[^1]: Example source. DOI 10.1000/example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert [s.heading for s in note.summaries] == [
        "Summary — 影像",
        "Summary — 陷阱",
    ]


def test_non_nr_note_is_not_in_scope():
    text = """---
concepts: [demo]
subspecialty: [ABD]
---
## Summary
- **影像**：Example。[^1]
[^1]: Example.
"""
    note = audit.parse_note_text(Path("demo.md"), text)
    assert note.in_scope is False


def test_validator_rejects_unlabeled_and_undefined_footnote():
    text = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- 沒有粗體標籤。[^missing]
"""
    findings = audit.validate_summary(audit.parse_note_text(Path("demo.md"), text))
    codes = {f.code for f in findings}
    assert "summary-bullet-label" in codes
    assert "footnote-undefined" in codes


def test_validator_rejects_callout_table_and_nested_bullet():
    text = """---
concepts: [demo]
subspecialty: [NR]
---
## Summary
- **影像**：Example。[^1]
  - nested
> [!note] callout
| A | B |
|---|---|
[^1]: Example.
"""
    findings = audit.validate_summary(audit.parse_note_text(Path("demo.md"), text))
    codes = {f.code for f in findings}
    assert {"summary-nested-bullet", "summary-callout", "summary-table"} <= codes
```

Add a `run_smoke()` entry point and exit nonzero on assertion failure.

- [ ] **Step 2: Run the smoke test and verify RED**

Run:

```powershell
python scripts/test_nr_summary_audit.py
```

Expected: FAIL because `nr_summary_audit.py` or its public interfaces do not exist.

- [ ] **Step 3: Implement the parser data structures and Summary extraction**

In `scripts/nr_summary_audit.py`, define immutable dataclasses:

```python
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
```

Parse inline YAML arrays used by this vault without introducing a YAML dependency. Recognize `## Summary` and
`## Summary — ...` until the next level-2 heading. Preserve level-3 headings inside a Summary variant as content.

- [ ] **Step 4: Implement structural validation**

`validate_summary()` must emit stable finding codes:

```text
summary-missing
summary-bullet-label
summary-nested-bullet
summary-callout
summary-table
summary-empty-bullet
footnote-undefined
```

A valid top-level bullet matches `^- \*\*[^*]+\*\*[：:]` and contains at least one `[^id]` reference. A Summary may
contain multiple `## Summary — ...` sections, but every section must contain at least one valid bullet.

- [ ] **Step 5: Implement CLI commands**

Required commands:

```powershell
python scripts/nr_summary_audit.py inventory --root vault/concepts --output docs/reports/nr-summary-rewrite/inventory.json
python scripts/nr_summary_audit.py validate-note vault/concepts/clippers.md
python scripts/nr_summary_audit.py validate-batch docs/reports/nr-summary-rewrite/batch-00.json
```

`validate-note` and `validate-batch` must print findings and return exit code 1 on any `error`; warnings alone return 0.

- [ ] **Step 6: Run smoke tests and verify GREEN**

Run:

```powershell
python scripts/test_nr_summary_audit.py
python -m py_compile scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py
```

Expected: both commands exit 0 and the smoke test prints `NR_SUMMARY_AUDIT_OK`.

- [ ] **Step 7: Commit Task 1**

Stage only:

```powershell
git add -- scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py
git commit -m "test: add NR summary audit tooling"
```

### Task 2: Full NR inventory, classification, and stable batch assignment

**Files:**
- Modify: `scripts/nr_summary_audit.py`
- Modify: `scripts/test_nr_summary_audit.py`
- Create: `docs/reports/nr-summary-rewrite/inventory.json`

**Interfaces:**
- Consumes: `parse_note()` from Task 1 and all `vault/concepts/*.md`.
- Produces: deterministic `inventory.json` with one entry per NR concept.

- [ ] **Step 1: Add failing inventory schema tests**

Add:

```python
def test_inventory_requires_allowed_type_and_status():
    entry = {
        "slug": "demo",
        "path": "vault/concepts/demo.md",
        "type": "unknown",
        "batch": "batch-00",
        "status": "pending",
        "sourceStatus": "existing-sufficient",
        "originalSha256": "a" * 64,
    }
    findings = audit.validate_inventory({"schemaVersion": 1, "notes": [entry]})
    assert "inventory-type" in {f.code for f in findings}


def test_inventory_rejects_duplicate_slug_and_missing_nr_note():
    findings = audit.validate_inventory_against_notes(
        inventory_with_duplicate_demo,
        {"demo": nr_demo, "other": nr_other},
    )
    codes = {f.code for f in findings}
    assert "inventory-duplicate-slug" in codes
    assert "inventory-scope-mismatch" in codes
```

Allowed values:

```python
NOTE_TYPES = {"disease", "pattern-ddx", "anatomy-measurement-management"}
NOTE_STATUSES = {
    "pending", "rewritten", "unchanged", "research-needed",
    "manual-review", "build-failed", "verified",
}
SOURCE_STATUSES = {
    "existing-sufficient", "research-needed", "researched", "conflict",
}
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
python scripts/test_nr_summary_audit.py
```

Expected: FAIL because inventory validation is not implemented.

- [ ] **Step 3: Implement deterministic inventory generation and validation**

The generated root object must be:

```json
{
  "schemaVersion": 1,
  "scope": "NR",
  "generatedFrom": "vault/concepts",
  "notes": []
}
```

Each entry must contain:

```json
{
  "slug": "clippers",
  "path": "vault/concepts/clippers.md",
  "type": "disease",
  "batch": "batch-00",
  "status": "pending",
  "sourceStatus": "existing-sufficient",
  "originalSha256": "<64 lowercase hex>",
  "summaryHeadings": ["Summary"]
}
```

The tool may prefill `type` only from a checked-in overrides map. It must never infer medical type from keywords and
silently accept it. Unknown entries must fail inventory validation until manually classified.

- [ ] **Step 4: Generate all 216 entries and classify them**

Run inventory generation once, then review every entry and assign exactly one allowed `type`. Assign `batch-00` only
to the following 10 slugs:

```text
clippers
cerebral-amyloid-angiopathy
craniopharyngioma
basal-ganglia-t1-shortening
cpa-masses
bilateral-subcortical-dwi-hyperintensity-ddx
artery-of-adamkiewicz
aspects-score
acute-stroke-management
dementia-neuroimaging-overview
```

Assign the remaining 206 notes to `unassigned` during Phase 1; Phase 2 will create 15–25-note production batches after
the pilot rules are accepted.

- [ ] **Step 5: Verify inventory completeness and determinism**

Run:

```powershell
python scripts/nr_summary_audit.py inventory --root vault/concepts --output docs/reports/nr-summary-rewrite/inventory.json --check
python scripts/test_nr_summary_audit.py
```

Expected:

```text
NR notes: 216
Duplicate slugs: 0
Unclassified: 0
Batch 00: 10
Unassigned: 206
```

- [ ] **Step 6: Commit Task 2**

Stage only:

```powershell
git add -- scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py docs/reports/nr-summary-rewrite/inventory.json
git commit -m "feat: inventory NR summary rewrite scope"
```

### Task 3: Batch 00 source ledger and fact-unit baseline

**Files:**
- Modify: `scripts/nr_summary_audit.py`
- Modify: `scripts/test_nr_summary_audit.py`
- Create: `docs/reports/nr-summary-rewrite/batch-00.json`

**Interfaces:**
- Consumes: Task 2 inventory entries and current Summary/body/reference sections of the 10 pilot notes.
- Produces: a complete, source-mapped fact ledger before any Summary edit.

- [ ] **Step 1: Add failing evidence-schema tests**

Add a fixture that verifies:

```python
def test_evidence_rejects_unmapped_or_unresolved_fact_units():
    report = batch_report_fixture()
    report["notes"][0]["factUnits"] = [
        {
            "id": "demo-f01",
            "text": "DWI high signal",
            "sourceRefs": [],
            "disposition": "covered",
        }
    ]
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    codes = {f.code for f in findings}
    assert "fact-source-missing" in codes


def test_evidence_rejects_source_ref_not_defined_in_note():
    report = batch_report_fixture(source_refs=["missing"])
    findings = audit.validate_evidence(report, {"demo": nr_demo})
    assert "fact-source-undefined" in {f.code for f in findings}
```

Allowed fact dispositions:

```python
FACT_DISPOSITIONS = {
    "pending", "covered", "research-needed", "manual-review",
}
```

- [ ] **Step 2: Run the test and verify RED**

Run `python scripts/test_nr_summary_audit.py`.

Expected: FAIL because evidence validation is incomplete.

- [ ] **Step 3: Implement evidence validation**

The batch report root must contain:

```json
{
  "schemaVersion": 1,
  "batch": "batch-00",
  "scope": "NR",
  "status": "baseline",
  "notes": []
}
```

Each note must include `slug`, `type`, `originalSha256`, `originalSummary`, `factUnits`, `sourceStatus`, `status`,
`rewrittenSummary`, and `validation`. `originalSummary` is a lossless string snapshot. Each fact unit must preserve
subject, relationship, polarity, qualifier, numeric/version constraints, and source refs in its `text`.

- [ ] **Step 4: Build the 10-note baseline before editing Markdown**

For every pilot note:

1. Copy all Summary variants losslessly into `originalSummary`.
2. Split every independent claim into stable IDs using the note slug as prefix, for example
   `clippers-f01`, `clippers-f02`, `aspects-score-f01`, and `aspects-score-f02`.
3. Attach all footnotes supporting that claim in `sourceRefs`.
4. Set `disposition` to `pending`.
5. Set `sourceStatus`:
   - `existing-sufficient` when every fact has a defined adequate source.
   - `research-needed` when a fact is unmapped, conflicted, time-sensitive, or weak-source dependent.

Do not edit any concept Summary in this task.

- [ ] **Step 5: Validate baseline**

Run:

```powershell
python scripts/nr_summary_audit.py validate-batch docs/reports/nr-summary-rewrite/batch-00.json --allow-pending
python scripts/test_nr_summary_audit.py
```

Expected: exit 0; `10 notes`, `0 missing sources`, and all facts either `pending` or explicitly
`research-needed/manual-review`.

- [ ] **Step 6: Commit Task 3**

Stage only:

```powershell
git add -- scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py docs/reports/nr-summary-rewrite/batch-00.json
git commit -m "docs: baseline NR summary pilot facts"
```

### Task 4: Rewrite the 10 pilot Summaries

**Files:**
- Modify: `vault/concepts/clippers.md`
- Modify: `vault/concepts/cerebral-amyloid-angiopathy.md`
- Modify: `vault/concepts/craniopharyngioma.md`
- Modify: `vault/concepts/basal-ganglia-t1-shortening.md`
- Modify: `vault/concepts/cpa-masses.md`
- Modify: `vault/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.md`
- Modify: `vault/concepts/artery-of-adamkiewicz.md`
- Modify: `vault/concepts/aspects-score.md`
- Modify: `vault/concepts/acute-stroke-management.md`
- Modify: `vault/concepts/dementia-neuroimaging-overview.md`
- Modify: `docs/reports/nr-summary-rewrite/batch-00.json`

**Interfaces:**
- Consumes: Task 3 fact units and source mappings.
- Produces: reformatted Summary sections and an evidence report with every fact disposition resolved.

- [ ] **Step 1: Record pre-edit hashes and check for concurrent edits**

Run:

```powershell
python scripts/nr_summary_audit.py validate-batch docs/reports/nr-summary-rewrite/batch-00.json --check-source-hashes
```

Expected: all 10 current file hashes match `originalSha256`. On mismatch, stop that note and mark `manual-review`;
do not overwrite it.

- [ ] **Step 2: Rewrite disease/entity notes**

Rewrite only Summary sections in:

```text
clippers
cerebral-amyloid-angiopathy
craniopharyngioma
```

Use only applicable bold labels from the disease template. Preserve qualifiers such as typical, rare, relative
preservation, exclusion diagnosis, and treatment-response conditions. After each note:

```powershell
$pilotSlugs = @(
  'clippers',
  'cerebral-amyloid-angiopathy',
  'craniopharyngioma'
)
foreach ($pilotSlug in $pilotSlugs) {
  python scripts/nr_summary_audit.py validate-note "vault/concepts/$pilotSlug.md"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

- [ ] **Step 3: Rewrite pattern/DDx notes**

Rewrite only Summary sections in:

```text
basal-ganglia-t1-shortening
cpa-masses
bilateral-subcortical-dwi-hyperintensity-ddx
```

Arrange facts by the first discriminating axis before disease lists. Preserve sequence names, directionality,
symmetry, distribution, and negative findings exactly as supported.

- [ ] **Step 4: Rewrite anatomy/scoring/management notes**

Rewrite only Summary sections in:

```text
artery-of-adamkiewicz
aspects-score
acute-stroke-management
```

For `acute-stroke-management`, retain historical-versus-current guideline layers and their citations; do not merge
2015, 2019, and 2020 recommendations into one timeless rule.

- [ ] **Step 5: Rewrite the multi-Summary dementia overview**

Normalize the three `## Summary — ...` sections into one `## Summary` only if every nested subsection and fact unit can
be preserved. Otherwise retain multiple Summary variants but ensure every bullet follows the bold-label contract.
Do not convert association into causation or generalize proteinopathy subtypes.

- [ ] **Step 6: Escalate only triggered source problems**

For notes marked `research-needed`, apply `radiology-topic-research`:

1. Use public and already accessible sources first.
2. If STATdx/ClinicalKey/RadioGraphics/AJR requires authentication, pause only that note and tell the user the platform
   and topic; continue safe notes.
3. Add any verified fact with article/chapter-level footnote and accessed date.
4. If sources conflict, record both and mark `manual-review`; do not choose an unsupported single value.

- [ ] **Step 7: Complete the evidence mappings**

Set each original fact unit to `covered`, `research-needed`, or `manual-review`. Add `rewrittenSummary` losslessly and
record:

```json
{
  "validation": {
    "structure": "pass",
    "footnotes": "pass",
    "factCoverage": "pass",
    "newUnsupportedFacts": 0
  }
}
```

`factCoverage` may be `pass` only if every original fact is `covered`; otherwise the note status cannot be `verified`.

- [ ] **Step 8: Validate all pilot notes**

Run:

```powershell
python scripts/nr_summary_audit.py validate-batch docs/reports/nr-summary-rewrite/batch-00.json
python scripts/test_nr_summary_audit.py
```

Expected: no structural or footnote errors, no unmapped fact units, and no unsupported new facts. Notes requiring
research or manual review remain explicitly unresolved rather than failing silently.

- [ ] **Step 9: Commit Task 4**

Stage only the 10 listed Markdown files and `batch-00.json`. Verify staged scope before commit.

```powershell
git diff --cached --name-only
git commit -m "docs: restructure NR summary pilot"
```

### Task 5: Build, lint, generated-output verification, and pilot review gate

**Files:**
- Regenerate:
  - `data/concepts/clippers.json`
  - `data/concepts/cerebral-amyloid-angiopathy.json`
  - `data/concepts/craniopharyngioma.json`
  - `data/concepts/basal-ganglia-t1-shortening.json`
  - `data/concepts/cpa-masses.json`
  - `data/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.json`
  - `data/concepts/artery-of-adamkiewicz.json`
  - `data/concepts/aspects-score.json`
  - `data/concepts/acute-stroke-management.json`
  - `data/concepts/dementia-neuroimaging-overview.json`
- Potentially modify: `data/concepts-index.json`.
- Modify: `docs/reports/nr-summary-rewrite/batch-00.json`
- Modify only if approved calibration changes are needed:
  `docs/superpowers/specs/2026-07-29-nr-summary-semantic-restructure-design.md`

**Interfaces:**
- Consumes: the verified 10-note pilot.
- Produces: website JSON, final batch evidence, and a Phase 1 acceptance result.

- [ ] **Step 1: Capture generated-data baseline**

Run:

```powershell
git status --short -- data/concepts data/concepts-index.json
python scripts/build_concepts.py
```

Record the pre-existing generated-data status before build so unrelated user changes cannot be attributed to this task.

- [ ] **Step 2: Verify generated JSON scope**

Run:

```powershell
git diff --name-only -- data/concepts data/concepts-index.json
```

Expected: only the 10 pilot JSON files, plus `data/concepts-index.json` if it has a deterministic metadata difference.
Any non-pilot concept JSON difference must be inspected and reverted only if it was generated by this task and is
proven unrelated; never discard pre-existing user changes.

- [ ] **Step 3: Run project lint and audit tests**

Run:

```powershell
python scripts/test_nr_summary_audit.py
python scripts/nr_summary_audit.py validate-batch docs/reports/nr-summary-rewrite/batch-00.json
python scripts/lint_concepts.py --quiet
python scripts/build_concepts.py --quiet
```

Expected: audit test、batch validation 與 concept build 均 exit 0。`lint_concepts.py` 維持既有 exit 1，
且輸出必須精確保持 2 errors／124 warnings，錯誤只能是：

```text
[footnote 未定義] ceap-classification.md 用了 [^*] 但無定義
[json 殘留 ![[...]]] 2022-264
```

任何新增 lint error 都使本步驟失敗；NR pilot notes 自身不得出現在 error 清單。

- [ ] **Step 4: Verify website keyPoints exactly mirror Summary bullets**

Parse these exact files and compare `keyPoints` to the corresponding source Summary top-level bullets after footnote
removal:

```text
data/concepts/clippers.json
data/concepts/cerebral-amyloid-angiopathy.json
data/concepts/craniopharyngioma.json
data/concepts/basal-ganglia-t1-shortening.json
data/concepts/cpa-masses.json
data/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.json
data/concepts/artery-of-adamkiewicz.json
data/concepts/aspects-score.json
data/concepts/acute-stroke-management.json
data/concepts/dementia-neuroimaging-overview.json
```

Add this comparison to `nr_summary_audit.py validate-batch`; a mismatch emits
`generated-keypoints-mismatch`.

- [ ] **Step 5: Finalize Phase 1 evidence**

Set batch root status:

- `verified` only when all 10 notes pass structure, footnote, fact coverage, and generated-output checks.
- `needs-review` when any note remains `research-needed` or `manual-review`.

Record command results and changed file lists in `batch-00.json`.

- [ ] **Step 6: Commit generated outputs and final evidence**

Stage only the verified generated JSON, validator changes, and batch report:

```powershell
git add -- scripts/nr_summary_audit.py scripts/test_nr_summary_audit.py docs/reports/nr-summary-rewrite/batch-00.json
git add -- data/concepts/clippers.json data/concepts/cerebral-amyloid-angiopathy.json
git add -- data/concepts/craniopharyngioma.json data/concepts/basal-ganglia-t1-shortening.json
git add -- data/concepts/cpa-masses.json data/concepts/bilateral-subcortical-dwi-hyperintensity-ddx.json
git add -- data/concepts/artery-of-adamkiewicz.json data/concepts/aspects-score.json
git add -- data/concepts/acute-stroke-management.json data/concepts/dementia-neuroimaging-overview.json
git add -- data/concepts-index.json
git diff --cached --check
git commit -m "build: publish NR summary pilot data"
```

Omit `data/concepts-index.json` from staging when it has no real diff.

- [ ] **Step 7: Present the pilot review gate**

Report:

- 10 per-note statuses.
- Original and rewritten Summary links.
- Any research/login queue.
- Fact-unit coverage counts.
- Build/lint results.
- Generated JSON scope.

Do not create Phase 2 production batches until the user accepts the pilot style or requests calibration changes.

## Plan Self-Review Results

- Spec coverage: classification, templates, source escalation, fact coverage, batch state, build/lint, and non-NR
  isolation are each mapped to a task.
- Scope: Phase 1 intentionally stops after a 10-note pilot review gate; processing the remaining 206 notes belongs to
  a Phase 2 plan after calibration.
- Completeness scan: every code-producing step names concrete files, interfaces, commands, and expected results.
- Interface consistency: Tasks 2–5 consume the `NoteRecord`, `Finding`, inventory schema, and evidence schema defined in
  Tasks 1–3 without renaming.
