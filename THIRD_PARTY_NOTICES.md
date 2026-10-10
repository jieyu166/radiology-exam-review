# Third-party notices

本專案除下列項目外皆為自有程式碼。

## ts-fsrs（MIT）

前端以 `<script>` 自 jsDelivr 載入 `ts-fsrs@5.4.2/dist/index.umd.js`（SRI 固定），用於 `js/scheduler/fsrs-adapter.js` 的間隔重複排程。
https://github.com/open-spaced-repetition/ts-fsrs — MIT License, Copyright (c) 2023 Open Spaced Repetition。

## mcq-bank（MIT）

以下模組的設計與邏輯移植自 https://github.com/htlin222/mcq-bank（commit 2e411ef0，2026-09-17），並改寫為本專案的 vanilla JS／plain Worker 形式：

- `js/question-timer.js` ← `frontend/src/lib/questionTimer.ts`（單題計時狀態機、10 分鐘 outlier）
- `js/attempt-outbox.js` ← `frontend/src/lib/attemptOutbox.ts`、`attemptFlusher.ts`（離線佇列、觸發點）
- `worker/src/attempts.js` 的 `clampElapsedMs` ← `worker/lib/attempts.ts`
- 作答事件表（`attempts`）append-only 與 `confidence` 1–3 的資料模型 ← `migrations/0023_attempts.sql`、`0020_answer_confidence.sql`

```
MIT License

Copyright (c) 2026 Hsiehting Lin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
