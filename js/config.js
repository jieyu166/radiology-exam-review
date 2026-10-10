/* =====================================================
   config.js — 執行期設定（獨立檔案，避免 inline script 牴觸 CSP）
   REX_API_BASE：rex-api Worker 網址（不含結尾斜線）。
   本機開發時 `wrangler dev` 預設在 http://127.0.0.1:8787。
   ===================================================== */
(function () {
  const host = (typeof location !== 'undefined' && location.hostname) || '';
  const isLocal = host === 'localhost' || host === '127.0.0.1';
  window.REX_API_BASE = window.REX_API_BASE || (isLocal ? 'http://127.0.0.1:8787' : 'https://rex-api.jieyu166.workers.dev');
})();
