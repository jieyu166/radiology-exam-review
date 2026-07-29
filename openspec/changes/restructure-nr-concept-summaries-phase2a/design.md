## Context

Phase 1 已完成 10 個固定 NR pilot 的結構、證據與 scoped build 校準；它是 Phase 2A 的不可變前提，不得重寫、重封印或以 Phase 2A 的資料取代。NR inventory 仍固定為 216 筆：10 筆 Phase 1 pilot，加上 206 筆非 pilot。這 206 筆目前分為 122 disease、35 pattern-ddx、49 anatomy-measurement-management。

Phase 2A 是第一次受限的 production tranche：只改寫 30 筆，且必須依序完成三個同類型的 10-note batch。固定成員如下，名稱、順序與 slug 都是契約的一部分：

1. `batch-01-anatomy`：`ajcc-8th-head-neck-n-staging`、`aneurysm-coiling-recurrence`、`atlantodental-interval`、`brachial-plexus-anatomy`、`brain-herniation-syndromes`、`carotid-vertebrobasilar-anastomoses`、`cerebral-border-zone-infarct-arteries`、`cerebral-deep-venous-cortex`、`cerebral-herniation-types`、`cerebral-infarction-evolution`。
2. `batch-02-disease`：`2-hydroxyglutarate-idh-mutant-glioma`、`adrenoleukodystrophy`、`aicardi-syndrome`、`als-imaging`、`angioinvasive-aspergillosis`、`anti-nmda-encephalitis`、`arterial-dissection-mri`、`atypical-teratoid-rhabdoid-tumor`、`autoimmune-encephalitis`、`basilar-artery-occlusion`。
3. `batch-03-pattern`：`brain-tumor-imaging`、`cerebral-infarction-fogging`、`cerebral-microbleeds`、`cerebrovascular-malformations`、`chemical-shift-artifact`、`cns-opportunistic-infection`、`cranial-nerve-muscle-atrophy`、`dural-based-masses-aids`、`facial-fracture-complications`、`gbm-vs-pcnsl`。

其餘 176 筆必須被排入 deterministic assignment，但在本變更中保持 `scheduled`，不得建立其 baseline、證據、Markdown 改寫或 generated JSON 差異。所有 source Markdown 仍是內容事實來源；報告、lock、manifest 與程式信任根只記錄和驗證其狀態，絕不自動產生醫學語句。

Phase 1 的 Summary 封閉文法、三種 note type 的內容規則、footnote 規則、例外式 `radiology-topic-research`、既有兩個 named lint errors，以及生成 keyPoints 的 source-order 對照全部沿用。Phase 2A 不處理認證、不下載受限 PDF、不修復既有 lint baseline，亦不改 renderer 或 concept JSON schema。

## Goals / Non-Goals

**Goals**

- 以單一 `phase2-assignment.json` 對所有 206 筆非 pilot 作完整、可重算且不依賴工作目錄位置的排程；其中只有三個固定 batch 為 `active`。
- 為每一個 active batch 在任何 Markdown 改寫之前建立無損 baseline lock，並以「中央、程式擁有、每 batch 一個 SHA-256」的信任登錄表封印，而非為每個 note 新增程式常數。
- 以可驗證的 fact-unit、source 定義、disposition、rewritten Summary、manual queue、review metadata 與 generated manifest，讓每一個 note 可獨立判定；安全的 sibling 不可被另一個 note 的 manual-review 阻塞。
- 讓 audit、build 與驗證在任意完整 checkout 的任意絕對路徑下產生相同結果；所有持久化檔案只使用 repository-relative POSIX path。
- 嚴格以 `batch-01-anatomy` → `batch-02-disease` → `batch-03-pattern` 執行。每批次由一名 implementer subagent 完成，再由另一名 reviewer subagent 核准，下一批才可開始。
- 在三個 batch、30 個 strict notes、216-note inventory、生成資料與 lint baseline 都通過後，留下可稽核的 Phase 2A completion 狀態，而不啟動其餘 176 筆。

**Non-Goals**

- 不執行 Phase 2B、後續 tranche 或剩餘 176 筆的 Summary rewrite、baseline lock、research、generated JSON 或 review。
- 不改寫 10 個 Phase 1 pilot、其 `batch-00.json`、其程式 trust roots 或其既有 evidence。
- 不以 slug、標題或醫學關鍵字推測 type、fact、source、disposition 或 clinical conclusion；缺資料時保守地標記 research-needed 或 manual-review。
- 不讓一次全庫 build 寫入資料，亦不接受「看 diff 應該沒問題」取代 manifest、hash、mtime 與 validator gate。
- 不改變既有 concept web renderer、公開 JSON schema、frontmatter、問題、Dataview、圖片或 Summary 以外的 note 部分，除非該 note 已有觸發式 research 所需的 article/chapter footnote。

## Decisions

### 1. 所有非 pilot note 由 deterministic assignment 排程，active 與 scheduled 明確分離

新增 `docs/reports/nr-summary-rewrite/phase2-assignment.json`。它是 206 筆非 pilot 的唯一排程來源；`inventory.json` 保留每筆 note 的 canonical path、type、pre-edit hash 與目前 batch/status 對照。assignment 的重算算法必須：

1. 從 inventory 取出全部且僅有非 `batch-00` 的 206 筆；拒絕重複 slug、未知 type、或任何 pilot 混入。
2. 先以固定表保留三個 active batch 的 30 個 slug，並驗證每組恰為 10 筆且 type 分別為 anatomy-measurement-management、disease、pattern-ddx。
3. 對剩餘 176 筆，先依固定 type 次序 `anatomy-measurement-management`、`disease`、`pattern-ddx` 分組，再在每組內依 ASCII slug 遞增排序，連續切成最多 10 筆的同質 scheduled batch。未滿 10 筆的尾 batch 仍是一個合法 scheduled batch。
4. scheduled batch ID 為 `scheduled-<type-short>-<two-digit-ordinal>`，其中 ordinal 在該 type 的「排除 active 固定 batch 後」序列從 `01` 起算；不得由檔案掃描順序、OS locale 或絕對路徑決定。

資料 shape（所有 object key 使用此名稱；array 保持所列順序）：

```json
{
  "schemaVersion": 1,
  "scope": "NR",
  "phase": "2",
  "sourceInventorySha256": "<64 lower-hex>",
  "batchSize": 10,
  "activeBatchIds": ["batch-01-anatomy", "batch-02-disease", "batch-03-pattern"],
  "batches": [
    {
      "id": "batch-01-anatomy",
      "ordinal": 1,
      "type": "anatomy-measurement-management",
      "state": "active",
      "slugs": ["..."]
    },
    {
      "id": "scheduled-anatomy-01",
      "ordinal": 4,
      "type": "anatomy-measurement-management",
      "state": "scheduled",
      "slugs": ["..."]
    }
  ]
}
```

`sourceInventorySha256` 是 inventory 中 206 筆非 pilot 的 canonical JSON projection（`slug`、`path`、`type`、`originalSha256`、`summaryHeadings`，依 slug 排序）的 UTF-8 SHA-256。它不允許 assignment 與 inventory 各自悄悄改寫相同內容。`state` 僅可為 `active` 或 `scheduled`；本 tranche 只能有三個 active batch 和 30 個 active slug。驗證器必須同時重算 projection、固定成員、scheduled 切分與整份 assignment 的 canonical bytes，並要求 206 筆出現一次且僅一次。

替代方案：把 176 筆留在 `unassigned`，等下一 tranche 再排程。拒絕，因為這會在後續執行時改變 batch 成員，無法證明 Phase 2A 沒有漏帳或偷偷擴大範圍。

### 2. baseline lock 使用每批一個中央程式信任摘要，而非每 note trust constant

每個 active batch 於改寫前新增 `docs/reports/nr-summary-rewrite/phase2a/baselines/<batch-id>.json`。它必須保留該批 10 筆 note 的完整 pre-edit Summary、目前檔案 hash、accepted Summary headings 與 stable fact units。lock 是 immutable input；後續 evidence 可引用它，但不得複製後當作另一個真相來源。

```json
{
  "schemaVersion": 1,
  "kind": "phase2-baseline-lock",
  "batch": "batch-01-anatomy",
  "scope": "NR",
  "assignmentSha256": "<64 lower-hex>",
  "notes": [
    {
      "slug": "ajcc-8th-head-neck-n-staging",
      "path": "vault/concepts/ajcc-8th-head-neck-n-staging.md",
      "type": "anatomy-measurement-management",
      "originalSha256": "<64 lower-hex>",
      "summaryHeadings": ["Summary"],
      "originalSummary": "<lossless UTF-8 Summary spans>",
      "factUnits": [
        {
          "id": "ajcc-8th-head-neck-n-staging-f01",
          "text": "<lossless independent fact text>",
          "sourceRefs": ["1", "2"]
        }
      ]
    }
  ]
}
```

`originalSummary` 保留每個 accepted Summary span 的原始 bytes/換行內容；fact ID 是 `<slug>-fNN`，NN 兩位數並以原始 Summary 出現順序編號，不得在 rewrite 時重新編號。baseline 的 digest 是 canonical JSON（UTF-8、`ensure_ascii=false`、指定 key 順序、`\n`、不含 digest 欄）的 SHA-256。

`scripts/nr_summary_audit.py` 新增一個中央、code-owned `TRUSTED_PHASE2A_BATCH_LOCK_SHA256: Mapping[str, str]`，只含三個 key：這三個 active batch ID 各一個 64 lower-hex digest。它不得含 note slug 或 note hash 的第二份 map。`validate-baseline` 與 `validate-batch` 必須從該 mapping 取得預期 digest，重算 lock digest，並驗證 lock / assignment / inventory / source file 四者的 note membership、path、type、hash 與 Summary snapshot 相同。lock 內自稱的 digest、evidence 內複製的 digest、或 inventory 的欄位均不能成為信任根。

替代方案：延續 Phase 1，為 30 筆 note 各放一個程式常數。拒絕，因為 tranche 擴大時程式碼會線性膨脹，review 也會從批次稽核退化為 30 個分散的常數比對。另一替代方案是將 digest 放入 lock 本身或同資料夾的 JSON registry；也拒絕，因為協調變更 lock 與其自述 digest 不會留下可信邊界。

### 3. report 與 lock 分層；證據、處置與手動佇列可導出而不可自我宣稱

每一 active batch 的工作報告置於 `docs/reports/nr-summary-rewrite/phase2a/evidence/<batch-id>.json`。它引用 baseline lock，不可改寫 baseline 的 originalSummary 或 fact text。資料 shape 為：

```json
{
  "schemaVersion": 1,
  "kind": "phase2-batch-evidence",
  "batch": "batch-01-anatomy",
  "scope": "NR",
  "baselineLock": {
    "path": "docs/reports/nr-summary-rewrite/phase2a/baselines/batch-01-anatomy.json",
    "sha256": "<64 lower-hex>"
  },
  "status": "baseline|needs-review|verified",
  "workflow": {
    "sequence": 1,
    "predecessor": null,
    "implementer": "<nonempty subagent run id>",
    "reviewer": "<nonempty different subagent run id>",
    "reviewStatus": "not-started|changes-requested|approved",
    "reviewedBaselineSha256": "<64 lower-hex or null>"
  },
  "notes": [
    {
      "slug": "ajcc-8th-head-neck-n-staging",
      "sourceStatus": "existing-sufficient|research-needed|researched|conflict",
      "status": "pending|rewritten|unchanged|research-needed|manual-review|build-failed|verified",
      "rewrittenSummary": "<lossless rewritten Summary spans>",
      "facts": [
        {
          "id": "ajcc-8th-head-neck-n-staging-f01",
          "sourceRefs": ["1"],
          "disposition": "covered|research-needed|manual-review"
        }
      ],
      "sourceDefinitions": {
        "1": {
          "kind": "existing-footnote|article|chapter",
          "locator": "<footnote id or stable source locator>",
          "citation": "<full rendered footnote text>"
        }
      },
      "newUnsupportedFacts": 0,
      "validation": {
        "hashMatches": true,
        "losslessSummaryMatches": true,
        "allSourceRefsDefined": true,
        "structure": {"errors": 0, "codes": []},
        "footnotes": {"errors": 0, "codes": []},
        "factCoverage": {"total": 0, "covered": 0, "researchNeeded": 0, "manualReview": 0}
      },
      "summaryBulletEvidence": ["<normalized, footnote-free bullet in source order>"],
      "coverageEvidenceSha256": "<64 lower-hex>"
    }
  ],
  "manualReviewFactIds": ["<derived sorted ids only>"],
  "generatedManifest": "docs/reports/nr-summary-rewrite/phase2a/generated/batch-01-anatomy.json",
  "phase2aVerification": {"...": "defined below"}
}
```

`facts` 必須與 lock 的 factUnits 逐一同 ID、同順序；報告不能新增、移除、改名或改寫 `text`。每一 `sourceRefs` 至少對應一個 `sourceDefinitions`；新寫入的醫學事實僅可引用 `kind=article` 或 `kind=chapter`，且 note 的 rendered footnote 必須存在。既有 Summary 的 source 可用已存在的 footnote。`coverageEvidenceSha256` 是該 note 的 canonical projection：baseline lock digest、slug、rewrittenSummary、facts 的 ID/sourceRefs/disposition、sourceDefinitions、summaryBulletEvidence、newUnsupportedFacts 與 validation。它是防誤改的 local checksum，並非信任根。

`manualReviewFactIds` 必須由所有 `disposition=manual-review` 或 `research-needed` 的 fact ID 依字典序導出；若手寫值不同，報出錯誤。manual fact 不得計為 covered；含其任何一項的 note 不得為 `verified`。其他 note 若自身全數 covered、source/hash/grammar/build 都通過，可為 `verified`；batch root 在佇列非空時必為 `needs-review`，不會拖回安全 sibling。

替代方案：使用一個巨大的 batch JSON 同時當 baseline、rewrite report 與 trust root。拒絕，因為 pre-edit evidence 可能在輸入與輸出同步變動，無法說明覆寫是否保留了最初事實。

### 4. 驗證契約是 checkout-path independent，CLI 不可依目前檔案位置推論資料位置

所有新增與擴充驗證都以明確的 repository root 解析：

```text
python scripts/nr_summary_audit.py validate-assignment \
  --repo-root <repo-root> \
  --inventory docs/reports/nr-summary-rewrite/inventory.json \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json

python scripts/nr_summary_audit.py validate-baseline \
  --repo-root <repo-root> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --batch batch-01-anatomy

python scripts/nr_summary_audit.py validate-batch \
  --repo-root <repo-root> \
  --assignment docs/reports/nr-summary-rewrite/phase2-assignment.json \
  --batch batch-01-anatomy --check-source-hashes --check-generated

python scripts/build_concepts.py --repo-root <repo-root> \
  --batch-file docs/reports/nr-summary-rewrite/phase2a/evidence/batch-01-anatomy.json \
  --quiet
```

CLI 接受的所有相對 path 都相對 `--repo-root`；JSON 內 path 必須是相對 POSIX path、不可為 absolute、不可含 `.`、`..`、反斜線、drive prefix 或在 resolve 後離開 root。程式不得以 `Path.cwd()`、`Path(__file__).parents[n]`、特定 OneDrive/worktree 名稱、或 `resolve()==某絕對路徑` 決定 expected note count、manifest root 或 trust 行為。對兩個內容相同但絕對路徑不同的 coherent checkout，所有 canonical JSON digest、finding code、generated manifest、exit code 與第二次 build 的寫入集合都必須相同。

既有 `parse_note`、`parse_note_text`、`extract_summary_sections`、`validate_summary`、`validate_inventory`、`validate_inventory_against_notes`、`validate_evidence` 保持相容；`validate_evidence(report, notes)` 可由 batch resolver 傳入一個已經從 `--repo-root` 解出的 context，但不得從 global cwd 偷取 input。新增公開介面：

```text
build_phase2_assignment(inventory: dict) -> dict
validate_phase2_assignment(assignment: dict, inventory: dict) -> list[Finding]
load_phase2_batch(repo_root: Path, assignment_path: Path, batch_id: str) -> BatchContext
validate_baseline_lock(context: BatchContext) -> list[Finding]
validate_phase2_batch(context: BatchContext, check_source_hashes: bool, check_generated: bool) -> list[Finding]
build_phase2_generated_manifest(repo_root: Path, batch_id: str) -> dict
```

其中 `BatchContext` 是 immutable dataclass，至少包含 `repo_root`、`inventory_path`、`assignment_path`、`assignment`、`batch`、`baseline_path`、`baseline`、`evidence_path`、`evidence`、`note_records`、`generated_root`；所有 path 的顯示值用 repo-relative POSIX string。`Finding` 仍為 immutable，且包含 `severity`、`code`、`path`、`message`。

替代方案：延續目前僅以 report 所在資料夾推算 repository root。拒絕，因為 worktree、CI checkout 與 relocation 會改變父目錄深度，使同一 evidence 在不同位置得到不同的驗證結果。

### 5. 三批次是 sequential subagent/reviewer gate，不是三個可平行執行的工作項

每一 batch workflow 都固定為：baseline lock sealed → implementer subagent 改寫及更新該批證據 → 該 batch validator/build/lint gate → 不同 reviewer subagent 審核 evidence、Markdown 與 generated output → reviewer `approved`。只有第 N 批 `approved` 且其 acceptance gate 成功後，N+1 才允許 baseline lock 或任何 Markdown edit 開始。

`workflow.sequence` 固定為 1、2、3；`predecessor` 依序為 `null`、`batch-01-anatomy`、`batch-02-disease`。`implementer` 與 `reviewer` 均為非空、可追溯的 run ID，且必須不同。sequence > 1 的 batch 除了自身 `reviewStatus=approved` 之外，其 predecessor evidence 亦必須 `reviewStatus=approved`、status 為 `verified` 或 `needs-review` 且所有可驗證 note gate 已通過；若 predecessor 還有 manual queue，該狀態不得阻擋 sibling batch，但 reviewer 必須確認它是 derived queue 而非未處理 validation error。

validator 可機械驗證宣告的順序、identity inequality、predecessor 狀態、sealed lock digest 與 review snapshot；人類/獨立 reviewer 的內容判斷仍由 review 進行，不能假裝由一個布林欄位自動保證。若 reviewer 要求修改，該 batch 保持 `needs-review`，修正後重新跑完整 batch gate 並由同一位或另一位獨立 reviewer 再核准；下一批仍不得開始。

替代方案：三個 subagent 平行改寫、最後統一 review。拒絕，因為第一批的 fact/footnote/build failure 可能會污染後續流程，且沒有先驗證可擴展 trust contract 的機會。

### 6. generated output 以 batch-scoped manifest 驗證寫入邊界與目前 corpus coherence

每批 build 只能選取 evidence 中該 batch 的 10 個 slug。manifest 存放於 `docs/reports/nr-summary-rewrite/phase2a/generated/<batch-id>.json`：

```json
{
  "schemaVersion": 1,
  "kind": "phase2-generated-manifest",
  "batch": "batch-01-anatomy",
  "selectedSlugs": ["...10 slugs in assignment order..."],
  "detailFiles": {"data/concepts/foo.json": "<64 lower-hex>"},
  "index": {
    "path": "data/concepts-index.json",
    "sha256": "<64 lower-hex>",
    "entryCount": 978
  },
  "detailFileCount": 978,
  "detailTreeSha256": "<64 lower-hex>",
  "allowedWrites": ["data/concepts/foo.json", "...", "data/concepts-index.json"],
  "secondRun": {"changedPaths": [], "mtimeChangedPaths": []}
}
```

`detailTreeSha256` 是所有 `data/concepts/*.json` 依 repo-relative path 排序的 path + SHA-256 canonical projection；`entryCount` 與 `detailFileCount` 是 build 當下完整 corpus 的值，驗證器要求 index 與 detail tree 互相一致，而非以某個本機絕對路徑或過期常數為準。`allowedWrites` 恰為 selected detail paths 加 index，並依字典序排序。第一 run 僅可寫這些路徑中 deterministic bytes 確實變動者；第二 run 必須 zero byte changes、zero mtime changes、zero unrelated file writes。每個 selected JSON 的 `keyPoints` 必須等於該 note 所有 accepted Summary variant 的 top-level bullet（source order、移除 footnote marker、沿用既有 normalization）。

替代方案：只比較 10 個 selected JSON。拒絕，因為 index 或非 selected detail 的遺失、增添或漂移仍可讓網站 corpus 不一致。

Generated observations use a second central, code-owned trust registry,
`TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256`, with exactly one canonical
observation-projection digest per active batch. The projection is produced only
after assignment, baseline, evidence, and baseline-trust gates pass; it binds
the actual pre-build snapshot, first scoped build delta, post-build snapshot,
actual second-run byte/mtime delta, and final generated tree. Batch validation
derives the current output state independently and compares the projection with
this code-owned digest; checked manifest fields cannot authenticate themselves.
The registry is intentionally empty and fail-closed in Task 1.1. The independent
reviewers in Tasks 2.3, 3.3, and 4.3 seal their respective batch digest only
after reviewing the genuine two-run workflow.

The authenticated `detailFiles`, `index`, `detailFileCount`, and
`detailTreeSha256` fields describe that batch's immutable historical post-build
observation; revalidation checks them against the authenticated historical
detail map (`detailFiles` plus `nonselectedAfter`), not by requiring equality
with a later current full tree. Current detail-tree and index coherence is a
separate gate. A current detail delta is permitted only when it is outside the
earlier batch's selected set and belongs to a strictly later active batch whose
baseline, evidence, independent approval, generated-observation seal, and
current selected-detail hash all validate. Assignment membership or a mutable
manifest claim alone never authorizes evolution.

## Implementation Contract

### 狀態與資料不變量

- Phase 1 `batch-00` 的成員與報告完全不變。`inventory.json` 更新後仍須是 216 筆、slug 唯一、type 為 closed enum；10 pilot 仍屬 `batch-00`，其餘 206 的 batch 指派必須與 `phase2-assignment.json` 一致。
- active batch 每個恰 10 筆，且跨 active/scheduled/Phase 1 全部 membership 不重疊。三個 active type 分別固定為 anatomy-measurement-management、disease、pattern-ddx；176 scheduled note 恰出現一次且不會有 Phase 2A report/lock/manifest。
- 每個 active baseline lock 都必須在該 batch 第一次改寫之前建立、通過 source hash 與 lossless Summary snapshot 比對，並等於程式中央 registry 的同 batch digest。registry 缺 key、額外 key、未知 batch、非 lower-hex 或 digest mismatch 全部失敗。
- 每個 evidence fact 必須對應 lock 中一個 fact ID；只有 `covered`、`research-needed`、`manual-review` 三種 final disposition。`pending` 只允許 lock 建立前的工作中資料，不可出現在可接受 evidence。
- note `verified` 的必要且充分條件為：source hash / lossless lock / structure / footnotes / source definitions / fact coverage / generated keyPoints 全通過、`newUnsupportedFacts=0`、沒有 unresolved fact，且 review approved。任何 manual-review/research-needed fact 都讓該 note 保持相應非 verified status。
- batch `verified` 必須每個 note verified、manual queue 空、review approved、generated/lint gate 通過。若沒有 validation error 但 derived manual queue 非空，batch 為 `needs-review`；若有 validation error，不能用 `needs-review` 掩蓋，CLI 必須 nonzero。
- 新醫學事實不得只靠 Summary 文字或弱既有連結；必須附 article/chapter footnote、sourceDefinitions 與實際 rendered footnote。遇到不可存取的 authenticated source，記錄 `research-needed`，請使用者登入並保留可讀頁面；不得接觸 credential 或繞過限制。

- Generated-output acceptance MUST require the code-owned per-batch
  `TRUSTED_PHASE2A_GENERATED_OBSERVATION_SHA256` digest. A trusted observation
  is produced only by the gated two-run workflow; missing trust, a self-attested
  no-build manifest, or a digest mismatch fails before generated output can be
  accepted. Task 1.1 leaves the registry empty; Tasks 2.3, 3.3, and 4.3 seal one
  independently reviewed digest for their corresponding active batch.
- Batch revalidation MUST preserve the authenticated historical scope result
  while independently validating the current complete detail tree and index.
  Current differences from that historical tree are accepted only for
  strictly later selected details whose later batch passes baseline, evidence,
  independent-review, and generated-observation trust gates. Earlier selected
  drift, unattributed detail drift, and an incoherent current index remain
  stable generated-output failures.

### Stable failure modes

驗證器必須輸出 stable code、repo-relative path、nonzero exit；至少包含以下情形：

| Code | 觸發條件 | 安全結果 |
| --- | --- | --- |
| `phase2-assignment-inventory-mismatch` | assignment 的 206 筆與 inventory projection 不同 | 停止全部 Phase 2A batch |
| `phase2-assignment-membership` | 重複、遺漏、pilot 混入、未知 slug、非同質 batch 或 active 非固定成員 | 不可建立/使用 lock |
| `phase2-assignment-nondeterministic` | scheduled 切分、排序、ID 或 canonical bytes 不能由 inventory 重算 | 不可啟動 batch |
| `phase2-path-invalid` | absolute/escaping/non-POSIX evidence path，或 resolve 離開 repo root | 不讀取目標檔案 |
| `phase2-baseline-missing` / `phase2-baseline-schema` | lock 不存在或 shape 不完整 | 不得改寫該 batch |
| `phase2-trusted-batch-lock-mismatch` | lock digest 與中央程式 registry 不相同 | 不得接受可協調改動的 baseline |
| `phase2-baseline-inventory-mismatch` | lock / inventory / assignment 的 slug、path、type、hash 或 headings 不一致 | affected batch 停止 |
| `phase2-source-hash-mismatch` | 改寫前目前 note hash 與 lock 不同 | affected note `manual-review`，不得覆寫；sibling 可繼續 |
| `phase2-lossless-summary-mismatch` | lock 的 originalSummary 與 pre-edit accepted Summary spans 不同 | affected note 不可 verified |
| `evidence-fact-coverage` | 遺漏/多出/改名 fact ID 或 covered 以外的未處置事實 | note 與 root 不可 verified |
| `evidence-source-definition` | sourceRefs 未定義、new fact 非 article/chapter、或 rendered footnote 缺失 | affected note 不可 verified |
| `evidence-unsupported-fact` | `newUnsupportedFacts != 0` 或 rewrite 無 source mapping | affected note 不可 verified |
| `phase2-manual-queue-mismatch` | queue 不是 derived sorted unresolved fact IDs | report 不可信，nonzero |
| `phase2-review-sequence` / `phase2-reviewer-conflict` | predecessor 未核准、次序跳過、implementer=reviewer 或 review snapshot 不符 | 下一批不可開始 |
| `generated-keypoints-mismatch` | generated keyPoints 與 validated Summary bullets 不同 | affected note 不可 verified |
| `generated-manifest-mismatch` / `generated-unrelated-write` / `generated-non-idempotent` | tree/index/hash/write set/second run bytes 或 mtime 不符 | batch 不可完成 |
| `lint-baseline-mismatch` | 兩個 named baseline errors 不再精確相同、warning delta 未說明、或新增 error / selected note error | batch/tranche 不可完成 |

### 驗證與 acceptance gates

每一批次都必須按下列順序完成，下一步不因「預期人工複查」而自動略過：

1. **Assignment gate**：對 `--repo-root` 執行 assignment/inventory 檢查；必須得到 216 total、10 Phase 1 pilot、206 non-pilot、30 active、176 scheduled，及三個 exact active batch。
2. **Baseline gate**：該 batch lock 與中央 registry digest 通過；10 個 current source hashes、original Summary、headings、type、path 逐一一致。任何 mismatch 先生成 manual-review 記錄，絕不覆寫 note。
3. **Content gate**：十個 note 都符合 Summary grammar 和 type-specific labels；每個 original fact 有 source/disposition；newUnsupportedFacts=0；verified note 達完全 coverage。research/manual queue 可存在，但須明確、derived，且不會被誤算成 coverage。
4. **Build gate**：batch-scoped build 只寫 allowed set；selected `keyPoints` source-order 一致；index/detail tree coherent；第二 run byte/mtime idempotent。
5. **Lint gate**：完整 project lint 仍精確保留兩個 named baseline errors；任何 warning 數量變化均要在 `phase2aVerification.lint.warningDelta` 以 `{before, after, delta, explanations}` 記錄逐條理由，且沒有新 error 或 selected note error。
6. **Independent review gate**：與 implementer 不同的 reviewer 檢查 lock、fact disposition、footnote、generated manifest 與 CLI output，將 review snapshot hash 寫入 evidence 並設為 `approved`。未核准即不得開始下一批。

Tranche gate 只在三批依序完成後執行：三個 batch evidence/locks/reviews 都通過；30 個 strict notes 無 structural、footnote、hash、unsupported 或 generated error，且所有未 covered fact 都完整列入 derived manual queue；全 216 inventory 完整；assignment 仍僅有 30 active；兩個 named baseline error 精確保留且無新 error；warning delta 已解釋；完整 generated corpus coherent；176 scheduled notes 不存在 Phase 2A edit、lock、evidence 或 generated diff。若任何 batch 因 unresolved fact 為 `needs-review`，Tranche 只能報告 `phase2a-complete-with-manual-queue`，不可聲稱所有 30 notes verified；Phase 2A 本身不得啟動 Phase 2B，後續 tranche 是否開始由使用者在檢視該 queue 後另行決定。

`phase2aVerification` 必須至少包含：

```json
{
  "status": "verified|needs-review",
  "assignmentSha256": "<64 lower-hex>",
  "activeBatchIds": ["batch-01-anatomy", "batch-02-disease", "batch-03-pattern"],
  "strictNoteCount": 30,
  "verifiedNoteCount": 0,
  "manualReviewFactIds": [],
  "lint": {
    "namedErrors": ["<exact baseline error 1>", "<exact baseline error 2>"],
    "warningDelta": {"before": 124, "after": 124, "delta": 0, "explanations": []}
  },
  "generated": {"batchManifestSha256": "<64 lower-hex>", "coherent": true},
  "phase2BStarted": false
}
```

`phase2BStarted` 必須是 `false`；不存在、true、或以其他欄位暗示 scheduled work 已啟動都失敗。

## Risks / Trade-offs

- **批次信任根仍需在程式碼更新 digest。** 這是有意的人工成本：新增或調整 lock 必須重新 review 該批 10 筆並更新一筆 central mapping。代價是避免 mutable evidence 同時改內容與自述 digest；比每 note constant 更能隨 tranche 擴展。
- **fact-unit 和 source disposition 仍含專業判斷。** Validator 只能驗證對應、coverage 和文法，不能證明醫學真實性。以 lossless lock、source definitions、獨立 reviewer、exception-only research 與保守 manual queue 降低遺漏 qualifier、否定或時效性規則的風險。
- **sequential review 會降低吞吐量。** 這是為了讓第一批暴露的 schema、trust 或 build 問題在擴至第二、三批前被修正；Phase 2A 的目的是驗證可擴展流程而非最大化平行速度。
- **path-independent contract 需要較多明確參數。** 使用者和 CI 必須提供 `--repo-root`，但交換 worktree、搬移 checkout 或從不同 cwd 執行時仍可重現。
- **完整 corpus manifest 對正常的同時生成工作敏感。** 在 validation 期間其他流程不得改動 `data/concepts/`；若偵測到 drift，應重新從 coherent checkout 執行，而不是放寬 gate。
- **已知 lint baseline 不乾淨。** 只允許兩個精確 named errors；warning 的變動必須可解釋，不能把新的問題藏在總數比較內。
- **受限文獻可能無法取得。** 不可用猜測填補；該 fact/note 保留 research-needed/manual-review，安全 sibling 可繼續，tranche status 如實反映未解佇列。

## Migration / Rollback

本變更沒有資料庫 migration。採附加式、可回復路徑：先在不改 Markdown 的情況下建立並驗證 assignment、三個 baseline locks 與信任 registry；只有該批 baseline gate 通過才允許改寫 10 個 Summary 與其 selected generated JSON。既有 Phase 1 artifacts 和 `batch-00` 不修改。

若 batch 在 rewrite 前失敗，移除尚未 tracked 的暫存輸出或放棄該工作分支即可；不得更新中央 digest 來「接受」未審核的 baseline。若 batch 在 rewrite 後的任一 content/build/lint/review gate 失敗，使用 lock 中的 `originalSummary` 與 `originalSha256` 對該 batch 的 10 個 note 執行逐檔 hash-guarded restore：只有目前檔案仍是該次 rewrite 的受控版本時才回復；若 hash 不同，停止並標記 manual-review，避免覆寫並行編輯。之後以 batch-scoped build 回復 selected generated files，並以 pre-change generated manifest / full detail-tree digest 驗證 index 與 corpus coherence。

rollback 只可作用於正在失敗的 active batch，不可觸碰 Phase 1、已核准 predecessor batch、scheduled 176 notes 或任何不在 `allowedWrites` 的檔案。若已核准 batch 之後發現 evidence/trust defect，先停在 `needs-review`、保留原始 lock 與 review trail，建立新的受 review 修正而不是覆寫舊 lock；三個 active batch 都重新通過 tranche gate 前，`phase2BStarted` 持續為 `false`。

