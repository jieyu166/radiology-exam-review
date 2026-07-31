# Task 3.2 implementation brief — batch-02 disease Summary rewrite

## Binding task and base

Implement only Spectra Task 3.2 for `batch-02-disease`, starting from
`0a3f73f`.

Read first:

- Task 3.2 in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/tasks.md`;
- the content, evidence, research, and acceptance contracts in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/design.md`;
- the corresponding requirements and scenarios in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/specs/nr-summary-production-batches/spec.md`;
- the approved baseline, pending evidence scaffold, Task 3.1 reports, and
  independent Task 3.1 round-2 review;
- `C:/Users/jai16/.codex/skills/obsidian-markdown/SKILL.md`;
- `C:/Users/jai16/.agents/skills/radiology-topic-research/SKILL.md`.

Canonical implementer identity:
`/root/phase2a_task3_2_impl`.

Do not mark the Spectra checkbox. The controller does that only after a new,
independent Task 3.2 reviewer finds no Critical or Important issue.

## Fixed scope

Rewrite only the accepted `## Summary` span(s) of these ten locked notes, in
assignment order:

1. `2-hydroxyglutarate-idh-mutant-glioma`
2. `adrenoleukodystrophy`
3. `aicardi-syndrome`
4. `als-imaging`
5. `angioinvasive-aspergillosis`
6. `anti-nmda-encephalitis`
7. `arterial-dissection-mri`
8. `atypical-teratoid-rhabdoid-tumor`
9. `autoimmune-encephalitis`
10. `basilar-artery-occlusion`

Update
`docs/reports/nr-summary-rewrite/phase2a/evidence/batch-02-disease.json`
from its pending scaffold to a ready-for-independent-review content record.
Update audit/build tests or validator logic only if a real Task 3.2 contract is
not already enforced. Run one batch-scoped concept build for these ten notes.

Do not edit:

- the approved baseline or its trusted digest;
- inventory or assignment;
- any other concept Markdown;
- Batch 01 artifacts, generated files, review records, or seals;
- Batch 03 or any scheduled note;
- Phase 1 artifacts;
- the generated-observation trust registry;
- a final generated manifest or final batch approval, which belong to Task
  3.3.

## Required disease-summary style

Use the user's requested Alzheimer-card analogue as a content organization
rule, not as a source of medical facts:

- only short top-level bullets;
- every bullet begins with `**粗體標籤**：`;
- every bullet contains one or more defined Obsidian footnotes;
- use only disease axes supported by the locked source, for example:
  age/demographics, genetics/etiology, pathology, symptoms, distribution,
  imaging, characteristic signs, DDx, treatment, or prognosis;
- omit any axis absent from the locked source rather than filling a template;
- split dense material into retrieval-friendly bullets when useful, but keep
  the governing subject attached to all qualifiers, comparisons, negations,
  exceptions, numbers, dates, versions, and DDx relationships;
- no tables, callouts, nested bullets, unsupported headings, plain prose
  lines, or facts inferred from the Alzheimer image.

Preserve Traditional Chinese and original English medical terminology. Prefer
source order. Reordering is allowed only when every locked fact is mapped
exactly once and no relationship changes.

## Medical and source fidelity

The approved 98 fact IDs are immutable. The baseline contains 60 source
statements and 98 facts; footnote definitions are not facts. For every fact:

- preserve subject, relationship, polarity, qualifiers, numbers, dates,
  versions, negations, exceptions, comparisons, ordering, and DDx;
- preserve the Aicardi triad context and its three members;
- preserve the ALD Schaumburg three-zone center-to-outside context and order;
- never add a relationship or conclusion absent from the baseline/source;
- retain only applicable existing source refs, or an actually verified
  exception-research source;
- set exactly one final disposition:
  `covered`, `research-needed`, or `manual-review`;
- never place a non-covered fact into a rewritten bullet or count it as
  covered.

Every covered fact must have nonempty `sourceRefs`; each ref must have a
rendered footnote and a complete `sourceDefinitions` entry. Existing
footnotes remain `kind=existing-footnote`. A genuinely researched source must
be `kind=article` or `kind=chapter` and include article/chapter-level citation
metadata.

`newUnsupportedFacts` must be exactly `0`.

## Exception-only research decision

Only these two locked facts presently have no applicable original source ref:

- `adrenoleukodystrophy-f30`:
  `PML：免疫低下、不對稱、皮質下 U-fibre、通常不強化（除 IRIS）、無腎上腺關聯。`
- `adrenoleukodystrophy-f33`:
  `PRES（後部可逆性腦病）：亦後部頂枕為主,但多為皮質下血管源性水腫、可逆、有高血壓／免疫抑制劑等誘因,通常不沿壓部呈進展性強化前緣。`

These unmapped facts trigger `radiology-topic-research`; no other fact should
receive broad literature expansion. Follow the skill exactly:

- use its allowed source hierarchy and verify the readable article/chapter
  body, not a search snippet;
- do not guess citations, cite an inaccessible page body, download restricted
  PDFs, handle credentials, or bypass access controls;
- if a readable allowed source supports the complete locked claim, record the
  audit, add a rendered article/chapter footnote, mark the fact `covered`, and
  set the note source status to `researched`;
- if the complete compound claim is not supported, do not weaken or silently
  split it merely to claim coverage: omit it from Summary, keep its empty refs,
  set `research-needed` or `manual-review`, and include it in the derived
  queue.

Authentication is not required in advance. If an allowed source is
authentication-gated, record the access state and retain the queue; do not
block the other 96 facts.

## Evidence and workflow state

Build the evidence file deterministically from the approved lock and current
rewritten notes; do not hand-copy duplicated medical text.

For every note:

- `rewrittenSummary` is the exact current accepted Summary span;
- fact IDs/order/text equal the baseline;
- source definitions are actual rendered definitions only;
- dispositions and refs reflect the real rewrite;
- `summaryBulletEvidence` equals current generated keyPoints in source order;
- validation fields and `coverageEvidenceSha256` are derived;
- note/source statuses are derived;
- `newUnsupportedFacts=0`.

At the batch root:

- `manualReviewFactIds` is the sorted, derived unresolved queue;
- status is `verified` only when every note is verified and the queue is
  empty; otherwise it is honestly `needs-review`;
- implementer is `/root/phase2a_task3_2_impl`;
- the intended final workflow reviewer may be
  `/root/phase2a_task3_3_review`, but `reviewStatus` remains `not-started` and
  `reviewedBaselineSha256` remains `null`;
- do not claim Task 3.3 approval, generated observation, lint acceptance, or
  terminal batch validation.

A pre-review batch finding may be review-gate-only. It must have no content,
source, structure, footnote, unsupported-fact, baseline, membership,
predecessor, or manual-queue integrity findings.

## Byte-scope requirements

For each selected Markdown file, preserve every byte outside the accepted
Summary span, except for a verified exception-research footnote definition
that may be appended using the file's existing newline convention. Preserve
frontmatter, headings, body, questions, images/embeds, Dataview, existing
footnote definitions, and EOF/newline conventions.

Before writing, verify all ten current hashes equal the approved baseline. If
any differ, stop and report `BLOCKED`; do not overwrite.

No nonselected note or generated detail may change. The scoped build may write
only the ten selected `data/concepts/<slug>.json` files whose deterministic
bytes change and `data/concepts-index.json`.

## TDD and required verification

Add RED tests before production edits for at least:

1. all 98 baseline facts retain stable IDs/order and exact final dispositions;
2. every rewritten bullet has valid bold-label grammar, defined inline refs,
   and evidence-backed coverage;
3. disease axes are optional and no unsupported category is synthesized;
4. Aicardi triad and ALD zone context/order remain fully represented;
5. qualifiers, numbers, versions, negations, exceptions, and compound DDx
   relationships are preserved;
6. uncovered ALD f30/f33 are omitted and derived into the queue unless a
   complete, audited source makes them covered;
7. `newUnsupportedFacts=0`;
8. exact byte preservation outside selected Summary spans;
9. no nonselected Markdown/generated writes;
10. pre-review evidence cannot be mistaken for Task 3.3 approval.

Required gates:

- ten current pre-edit hashes equal the baseline before the first edit;
- 10/10 strict `validate-note` exits 0;
- evidence has 98 final dispositions and `newUnsupportedFacts=0`;
- content/source/footnote/manual-queue checks have no findings;
- remaining batch findings, if any, are review-gate-only and listed;
- one scoped build using the evidence batch file succeeds;
- selected generated `keyPoints` equal accepted Summary bullets;
- complete index/detail corpus remains coherent;
- nonselected source/detail bytes and mtimes are unchanged;
- Batch 01 terminal `validate-batch --check-generated` remains exact `[]`;
- complete audit/build pytest, direct Phase 1 smokes, four-file `py_compile`,
  Spectra strict/analyze, and `git diff --check` pass;
- range diff proves only the ten Summary spans plus permitted verified
  research footnotes changed in Markdown;
- no Batch 03/scheduled artifact exists.

## Report and commit

Write
`tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-3-2-report.md`
with:

- RED/GREEN evidence;
- per-note before/after Summary and fact-to-bullet coverage counts;
- all final dispositions and the derived manual queue;
- source-definition/footnote parity;
- exception-research access/result;
- byte-scope and nonselected-write proof;
- scoped build written paths and keyPoints parity;
- all test/CLI/Spectra gates;
- changed files and concerns.

Make one focused commit and return DONE, DONE_WITH_CONCERNS, or BLOCKED with
the commit SHA. Do not mark Task 3.2 complete.
