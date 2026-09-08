const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/note-renderer.js', 'utf8') + '\nglobalThis.NoteRenderer = NoteRenderer;';
const context = { console, window: { REX_PUBLICATION_BASE: 'dist/' } };
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const raw = `---\nid: brain-abscess\n---\n# Brain abscess\n\n## Teaching Pearls\n\n- one\n1. two\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n> [!note] Callout\n> body\n\nA [[other-concept|link]], ![[brain.png]], $x^2$, and [source](https://example.com).\n\n[^1]: footnote\n==unknown==`;
const result = context.NoteRenderer.renderDocument(raw, {
  record: { embeds: [{ target: 'brain.png', resolvedPath: 'assets/abc-brain.png' }] },
});
assert(result.html.includes('<h2>Teaching Pearls</h2>'), 'unmapped headings should render');
assert(result.html.includes('<ul'), 'unordered lists should render');
assert(result.html.includes('<ol'), 'ordered lists should render');
assert(result.html.includes('<table'), 'tables should render');
assert(result.html.includes('note-callout'), 'callouts should render');
assert(result.html.includes('href="#/concept/other-concept"'), 'wikilinks should become internal links');
assert(result.html.includes('dist/assets/abc-brain.png'), 'resolved image embeds should render');
assert(result.html.includes('note-math'), 'math should render');
assert(result.html.includes('note-degraded'), 'unknown blocks should be explicit degraded content');
assert(result.warnings.length === 1, 'unknown block should produce one warning');
assert(!result.html.includes('<script>'), 'raw HTML must not execute');
const clinicalRaw = fs.readFileSync('vault/concepts/acute-mesenteric-ischemia.md', 'utf8');
const clinicalResult = context.NoteRenderer.renderDocument(clinicalRaw);
assert(!clinicalResult.html.includes('list from #交換'), 'Obsidian queries must not appear on the website');
assert(!clinicalResult.html.includes('<h2>考題</h2>'), 'query-only question headings should be hidden');
assert(!clinicalResult.html.includes('渲染提示'), 'a supported hidden query should not produce a warning');
assert(clinicalResult.html.includes('臨床重點') && clinicalResult.html.includes('2021-194'), 'clinical prose and real question content must remain');

const mixed = context.NoteRenderer.renderDocument('## 考題\n\n請先閱讀病例。\n\n```dataview\nlist from #交換\n```\n\n## 下一節\n保留正文');
assert(mixed.html.includes('<h2>考題</h2>') && mixed.html.includes('請先閱讀病例。'), 'question headings with actual content must remain');
assert(mixed.html.includes('<h2>下一節</h2>') && mixed.html.includes('保留正文'), 'content following a query must remain');
for (const fence of ['```dataview', '~~~dataviewjs']) {
  const hidden = context.NoteRenderer.renderDocument('## 考題\n' + fence + '\nquery code\n' + fence.slice(0, 3));
  assert(!hidden.html.trim() && hidden.warnings.length === 0, 'closed Dataview blocks should be omitted without warnings');
}
const unknownCode = context.NoteRenderer.renderDocument('```python\nprint("keep")\n```');
assert(unknownCode.html.includes('print') && unknownCode.warnings.length === 1, 'other fenced content must retain its fallback rendering');
const unclosedQuery = context.NoteRenderer.renderDocument('```dataview\n請勿遺失後續內容');
assert(unclosedQuery.html.includes('請勿遺失後續內容') && unclosedQuery.warnings.length === 1, 'unclosed fences must not silently discard content');
const quoted = context.NoteRenderer.renderDocument('正文\n> 引用\n>\n> - **重點**\n> - 第二點');
assert(quoted.html.includes('<blockquote') && quoted.html.includes('<ul') && quoted.html.includes('<strong>重點</strong>'), 'quoted paragraphs and lists must render as blocks');
assert(!quoted.html.includes('&gt;'), 'quote markers must not leak into prose');
const folded = context.NoteRenderer.renderDocument('> [!quote]- 出處\n> ## 判讀\n> - 重點\n>\n> ![[scan.png]]', {record:{embeds:[{target:'scan.png',resolvedPath:'assets/scan.png'}]},assetBase:''});
assert(folded.html.includes('<details') && !folded.html.includes(' open') && folded.html.includes('<summary>出處</summary>'), 'minus callouts should be collapsed with a clean title');
assert(folded.html.includes('<h2>判讀</h2>') && folded.html.includes('src="assets/scan.png"'), 'callout block content and images must render');
const expanded = context.NoteRenderer.renderDocument('> [!note]+ 提示\n> 內容');
assert(expanded.html.includes(' open') && !expanded.html.includes('+ 提示'), 'plus callouts should start expanded');
console.log('note renderer tests passed');
