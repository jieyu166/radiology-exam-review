# Worktree 操作備忘（多 session 並行 backfill）

> 目的：4 個 Claude session 同時處理不同年份交換考題，避免互相蓋檔、避免 git index 污染。
> 做法：每個 backfill session 用**獨立的 git worktree**（各有獨立工作目錄與 index），醫師 Obsidian 主庫維持在 main。

---

## 1. 架構對照表

| Session | 工作目錄 | 分支 | 說明 |
|---|---|---|---|
| **2016** | `C:\Users\jai16\OneDrive\00 放射科\radiology-exam-review` | `main` | 醫師 Obsidian 主庫，2016 session 也在此 |
| **2017** | `C:\Users\jai16\radiology-worktrees\radiology-2017` | `backfill-2017` | |
| **2018** | `C:\Users\jai16\radiology-worktrees\radiology-2018` | `backfill-2018` | |
| **2019** | `C:\Users\jai16\radiology-worktrees\radiology-2019` | `backfill-2019` | |

- Worktree 母目錄：`C:\Users\jai16\radiology-worktrees\`（**刻意放在 OneDrive 外**，避免 OneDrive 同步 worktree 檔案與 `.git` 連結造成損壞）。
- 所有 worktree 共用同一個 `.git`（在 main 的 OneDrive repo 內），但工作檔案各自獨立。

---

## 2. 每個 worktree session 開場 3 步

1. **確認位置正確**
   ```
   git branch --show-current
   ```
   應顯示 `backfill-YYYY`（不是 `main`）。若不是，代表這個 session 沒開在正確的 worktree 目錄，先切到對照表裡的目錄。

2. **同步最新 main**
   ```
   git merge main
   ```
   拿到 main 上的醫師 checked 回寫、共用 concept 檔的最新內容，保持與其他年份一致。

3. **確認進度檔存在**
   `scripts\_YYYY_backfill_progress.json`（gitignored，不隨 worktree 自動帶過，已手動複製）。
   若缺，從 main 的 `scripts\` 複製對應年份那份過來。

---

## 3. 工作紀律

- **檔案分區**：各 session 只改**自己年份**的 `data/{year}.json` 與 `vault/questions/{year}/`。
- **commit 列明確路徑**（別用 `git add` 後裸 `git commit`）：
  ```
  git add <我的新檔...>
  git commit <我的所有檔...> -m "..."
  ```
  worktree 各有獨立 index，理論上不會互相污染，但保持此習慣最保險。
- **跨年去重**：優先寫進 `data/rex-edits-*.json` patch，由協調者用 `merge_edits.py` 併入；
  若真的要改更早年份的 json，它會留在你的 worktree，日後 merge 回 main 時變成**看得到的衝突**（不再無聲蓋檔）。
- **共用 concept 檔**：worktree 內是你自己的副本，不會即時被別人蓋；但若兩年都改同一個 concept 檔，
  merge 回 main 時會產生**真正的 git merge 衝突**（可解、可見，這正是我們要的）。
- **第一次 push**：
  ```
  git push -u origin backfill-YYYY
  ```

---

## 4. 兩個同步方向要分清（重要）

| 方向 | 內容 | 在哪裡做 |
|---|---|---|
| **json → vault** | 產生新題卡（`json_to_vault.py {year} --force`） | **你的 worktree** |
| **vault → json** | 醫師確認回寫 checked 旗標（`vault_to_json.py {year} --write`） | **main** |

- 醫師的 Obsidian 主庫是 **main**，他的 `checked:true`、詳解修正只存在 main 的卡片裡。
- 所以「醫師修改回寫 json」一律在 **main** 執行：
  ```
  # 在 main 目錄
  python scripts/vault_to_json.py 2017          # dry-run 先看差異
  python scripts/vault_to_json.py 2017 --write  # 回寫 checked 至 json
  git commit data/2017.json -m "醫師審閱回寫：checked 同步"
  ```
- `vault_to_json.py` **只回寫結構性欄位**（預設 `checked`，可加 `--fields checked,subspecialty,correctAnswer,concepts`）；
  **不碰** `<!--SR:!...-->` 間隔複習註解、也不碰自由文字詳解（那些以 .md 為準，受 genHash 保護）。
- worktree session 之後 `git merge main` 就能拿到這些 checked 更新。

---

## 5. 年份收尾 / 整合回 main

年份做完（或階段性）時，把該年成果併回 main：
```
# 切到 main 目錄
cd "C:\Users\jai16\OneDrive\00 放射科\radiology-exam-review"
git merge backfill-2017
# 若有共用 concept 檔衝突 → 解衝突後 git add + git commit
git push
```

---

## 6. 2016 session 特別注意

- 2016 留在 **main**，與醫師主庫共用。**session 進行期間醫師不要在 Obsidian 改庫**，以免撞車。
- 2016 session 恢復後：
  1. 先把目前卡在 main 的未提交 2016 工作 commit 掉。
  2. 跑 `python scripts/vault_to_json.py 2016 --write` 補上醫師的 checked 確認（約 35 題）。
  3. commit（列明確路徑，只 commit `data/2016.json` 與自己的卡片）。

---

## 7. 維運指令備查

- **列出所有 worktree**：
  ```
  git worktree list
  ```
- **未來新增年份 worktree**（例如 2020 session 要開工時）：
  ```
  git worktree add "C:\Users\jai16\radiology-worktrees\radiology-2020" -b backfill-2020
  copy scripts\_2020_backfill_progress.json 到該 worktree 的 scripts\   # 若有進度檔
  ```
- **移除某個 worktree**（該年完成、已 merge 回 main 後）：
  ```
  git worktree remove "C:\Users\jai16\radiology-worktrees\radiology-2020"
  git branch -d backfill-2020   # 確認已 merge 才刪分支
  ```
- **清掉失效的 worktree 記錄**（手動刪目錄後）：
  ```
  git worktree prune
  ```

---

## 8. 禁忌

- ❌ worktree 目錄**不要**放進 OneDrive（同步會損壞 `.git` 連結、造成 index 競爭）。
- ❌ 不要 `git add` 後跑裸 `git commit`（會掃到別人 staged 的檔）。
- ❌ 不要在 main 擅自 commit 別的 session 或醫師的未提交工作。
- ❌ 不要修改或刪除 `<!--SR:!...-->` 間隔複習註解。
