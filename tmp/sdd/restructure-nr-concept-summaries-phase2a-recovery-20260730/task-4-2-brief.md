# Task 4.2 implementation brief — batch-03 pattern Summary rewrite

## Binding task and base

Implement only Spectra Task 4.2 for `batch-03-pattern`, starting from
`abfcac6`.

Read first:

- Task 4.2 in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/tasks.md`;
- the evidence, research, sequencing, and acceptance contracts in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/design.md`;
- the corresponding requirements and scenarios in
  `openspec/changes/restructure-nr-concept-summaries-phase2a/specs/nr-summary-production-batches/spec.md`;
- the approved Batch 03 baseline, pending evidence scaffold, Task 4.1 report,
  and independent Task 4.1 round-2 review;
- `C:/Users/jai16/.codex/skills/obsidian-markdown/SKILL.md`;
- `C:/Users/jai16/.agents/skills/radiology-topic-research/SKILL.md`.

Canonical implementer identity:
`/root/phase2a_task4_2_impl`.

Do not mark the Spectra checkbox. The controller does that only after a new,
independent Task 4.2 reviewer finds no Critical or Important issue.

## Fixed scope

Rewrite only the accepted Summary span(s) of these ten locked notes, in
assignment order:

1. `brain-tumor-imaging`
2. `cerebral-infarction-fogging`
3. `cerebral-microbleeds`
4. `cerebrovascular-malformations`
5. `chemical-shift-artifact`
6. `cns-opportunistic-infection`
7. `cranial-nerve-muscle-atrophy`
8. `dural-based-masses-aids`
9. `facial-fracture-complications`
10. `gbm-vs-pcnsl`

Update
`docs/reports/nr-summary-rewrite/phase2a/evidence/batch-03-pattern.json`
from its pending scaffold to a ready-for-independent-review content record.
Update audit/build tests or validator logic only when a real Task 4.2 contract
is not already enforced. Run one batch-scoped concept build for these ten
notes.

Do not edit:

- the approved baseline or its trusted digest;
- inventory or assignment;
- any other concept Markdown;
- Batch 01/02 artifacts, generated files, review records, or seals;
- scheduled notes or Phase 1 artifacts;
- the generated-observation trust registry;
- a final generated manifest or final batch approval, which belong to Task
  4.3.

## Required pattern/DDx style

Use the user's requested “粗體標籤＋短 bullets” matrix analogue:

- every accepted Summary line is either a nonempty `###` grouping heading or
  a top-level bullet beginning with `**粗體標籤**：`;
- every bullet contains one or more defined Obsidian footnotes;
- organize only by discriminating axes already supported by the locked source,
  such as site, sequence/signal, distribution, symmetry, enhancement,
  age/clinical context, named sign, DDx discriminator, or pitfall;
- omit an axis absent from the source rather than filling a template;
- preserve the governing subject for every comparison and relationship;
- use short retrieval-friendly bullets without losing qualifiers, numbers,
  polarity, exceptions, ordering, or exam-answer context;
- no tables, callouts, nested bullets, plain prose lines, unsupported
  headings, or unreferenced matrix cells.

Preserve Traditional Chinese and original English medical terminology. Prefer
source order. Reordering is allowed only when every locked fact is mapped
exactly once and no relationship changes.

## Medical and source fidelity

The approved 94 fact IDs are immutable. The baseline contains 69 accepted
source statements and 94 facts; footnote definitions are not facts. For every
fact:

- preserve subject, relationship, polarity, qualifiers, numbers, dates,
  versions, negations, exceptions, comparisons, ordering, and DDx;
- do not turn an association into a diagnostic rule or a list into an
  equivalence;
- do not add a disease, imaging pattern, sequence relationship, threshold, or
  management conclusion absent from the source;
- retain only applicable existing source refs, or an actually verified
  exception-research source;
- set exactly one final disposition:
  `covered`, `research-needed`, or `manual-review`;
- every covered fact must have nonempty `sourceRefs`, valid clause-level
  coverage anchors, rendered footnotes, and complete source definitions;
- every unresolved fact must have `coverage: null`, stay out of the rewritten
  Summary, and appear in the derived queue.

`newUnsupportedFacts` must be exactly `0`.

## Exact empty-projection exception

`cerebrovascular-malformations` is a deliberate legacy-heading edge case:

- its approved baseline is exactly
  `summaryHeadings=[]`, `originalSummary=""`, `factUnits=[]`;
- its three existing `## Summary（...）` sections are outside the accepted
  grammar and were therefore not baseline facts;
- do not expand the accepted heading regex and do not change assignment,
  inventory, or the Batch 03 baseline/trust digest;
- do not rename, delete, move, or edit those three legacy sections or any
  other existing byte;
- add exactly one canonical accepted `## Summary` span, using only direct,
  conservative compression of the existing cited legacy Summary bullets;
- every new bullet must carry the same applicable rendered footnote(s); no
  claim may be inferred from the title, lead paragraph, uncited prose, or a
  nearby but inapplicable reference;
- because the lock has no fact IDs, do not invent IDs or claim locked-fact
  coverage. The evidence must instead derive the bullet source refs and
  rendered source definitions explicitly.

If the current Phase 2 evidence validator cannot honestly represent this
case, add the narrowest TDD change that:

1. accepts a rewritten zero-fact note only when its trusted baseline is the
   exact empty projection above and the current note has a nonempty accepted
   Summary;
2. derives `sourceDefinitions` from the ordered union of covered fact refs and
   actual Summary-bullet refs, so source-backed zero-fact bullets are audited;
3. requires every bullet ref to be rendered and defined;
4. derives the source/note status and `newUnsupportedFacts=0`;
5. rejects the same evidence for any nonempty baseline, any hidden accepted
   pre-edit Summary, any bullet without refs, any undefined/mismatched source
   definition, any non-Summary byte change, or any invented fact ID.

This is a narrow source-preserving migration, not permission to make empty
locks generally verify or to relax Summary grammar.

## Exception-only research decision

Only these four locked facts presently have no original source ref:

- `cns-opportunistic-infection-f06`:
  `三者皆正確 → 故「何者正確」答 D（以上皆正確）（2016-184 正解 D）。`
- `dural-based-masses-aids-f04`:
  `腫瘤性：轉移、孤立性纖維瘤、黑色素細胞腫瘤、膠質母細胞瘤、EBV相關平滑肌腫瘤。`
- `dural-based-masses-aids-f05`:
  `肉芽腫性：結核病、多發血管炎性肉芽腫病(GPA)、類肉瘤病。`
- `dural-based-masses-aids-f06`:
  `淋巴增生性：淋巴瘤、Rosai-Dorfman disease、Erdheim-Chester disease。`

First inspect whether an existing rendered article/chapter footnote directly
supports the complete locked claim. Do not infer support merely because it is
nearby. Only these unresolved facts may trigger `radiology-topic-research`;
no other fact receives broad literature expansion.

Follow the research skill exactly:

- verify the readable article/chapter body, not a search snippet;
- do not guess citations, cite inaccessible body text, handle credentials,
  bypass access controls, or download restricted PDFs;
- cover a fact only if the complete compound claim is supported;
- otherwise omit it, keep `sourceRefs=[]`, set `research-needed` or
  `manual-review`, and derive it into the queue.

Authentication is not required in advance. If a required source is gated,
retain the queue and continue the other facts.

## Evidence and workflow state

Build the evidence deterministically from the approved lock and current
rewritten notes. Do not hand-copy duplicated medical text.

For every note:

- `rewrittenSummary` is the exact current accepted Summary projection;
- fact IDs/order equal the baseline;
- each covered fact has clause-level `{bulletIndex, quote}` anchors;
- unresolved facts have `coverage: null`;
- source definitions exactly equal the rendered sources actually referenced
  by covered facts and, for the exact empty-projection exception, Summary
  bullets;
- `summaryBulletEvidence` equals current generated keyPoints in source order;
- validation fields, note/source status, and
  `coverageEvidenceSha256` are derived;
- `newUnsupportedFacts=0`.

At the batch root:

- `manualReviewFactIds` is the sorted derived unresolved queue;
- status is `verified` only when every locked fact is covered and the exact
  empty-projection note passes the source-backed exception; otherwise it is
  honestly `needs-review`;
- implementer is `/root/phase2a_task4_2_impl`;
- intended reviewer may be `/root/phase2a_task4_3_review`, but
  `reviewStatus` remains `not-started` and
  `reviewedBaselineSha256` remains `null`;
- do not claim Task 4.3 approval, generated observation, lint acceptance, or
  terminal batch validation.

A pre-review batch finding may be review-gate-only. It must have no content,
source, structure, footnote, unsupported-fact, baseline, membership,
predecessor, manual-queue, or empty-projection integrity findings.

## Byte-scope requirements

Before writing, verify all ten current hashes equal the approved baseline. If
any differ, stop and report `BLOCKED`; do not overwrite.

For nine ordinary notes, preserve every byte outside accepted Summary spans,
except a verified exception-research footnote definition appended with the
file's existing newline convention.

For `cerebrovascular-malformations`, preserve every original byte and add only
the new canonical accepted Summary span. The three parenthesized legacy
Summary sections remain byte-identical.

No nonselected note or generated detail may change. The scoped build may write
only changed selected `data/concepts/<slug>.json` files and
`data/concepts-index.json`.

## TDD and required verification

Add RED tests before production edits for at least:

1. all 94 baseline facts retain stable IDs/order and exact dispositions;
2. every covered fact has clause-level, medical-body coverage anchors;
3. every rewritten bullet has bold-label grammar and defined inline refs;
4. all pattern axes and DDx relationships remain source-grounded;
5. qualifiers, numbers, versions, negations, exceptions, comparisons, and
   exam-answer context are preserved;
6. the four empty-ref facts are either completely sourced or omitted with
   `coverage:null` and a derived queue entry;
7. the exact empty-projection exception passes only with source-backed bullets
   and rejects all broader/forged variants listed above;
8. `newUnsupportedFacts=0`;
9. exact byte preservation outside allowed Summary additions/replacements;
10. no nonselected Markdown/generated writes and no false Task 4.3 approval.

Required gates:

- ten current pre-edit hashes equal the baseline before the first edit;
- 10/10 strict `validate-note` exits 0;
- evidence has 94 exact dispositions and `newUnsupportedFacts=0`;
- content/source/footnote/coverage/manual-queue/empty-projection checks have no
  findings;
- remaining batch findings, if any, are review-gate-only and listed;
- one scoped build succeeds;
- selected generated `keyPoints` equal all accepted Summary bullets;
- complete index/detail corpus remains coherent;
- nonselected source/detail bytes and mtimes are unchanged;
- Batch 01 and Batch 02 terminal
  `validate-batch --check-generated` remain exact `[]`;
- complete audit/build pytest, direct Phase 1 smokes, four-file `py_compile`,
  Spectra strict/analyze, and `git diff --check` pass;
- range diff proves the allowed Markdown scope;
- no scheduled artifact exists.

## Report and commit

Write
`tmp/sdd/restructure-nr-concept-summaries-phase2a-recovery-20260730/task-4-2-report.md`
with:

- RED/GREEN evidence;
- per-note before/after Summary and fact-to-bullet coverage counts;
- all final dispositions and the derived queue;
- source-definition/footnote parity;
- exception-research access/results;
- exact empty-projection migration and attack results;
- byte-scope and nonselected-write proof;
- scoped build written paths and keyPoints parity;
- all test/CLI/Spectra gates;
- changed files and concerns.

Make one focused commit and return DONE, DONE_WITH_CONCERNS, or BLOCKED with
the commit SHA. Do not mark Task 4.2 complete.
