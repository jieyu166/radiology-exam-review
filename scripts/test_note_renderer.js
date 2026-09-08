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
console.log('note renderer tests passed');
