const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync('js/content-store.js', 'utf8') + '\nglobalThis.ContentStore = ContentStore;';
const calls = [];
const payloads = {
  'dist/manifest.json': { entries: [{ id: 'brain-abscess', kind: 'concept', recordPath: 'records/concept/brain-abscess.json', rawPath: 'notes/concepts/brain-abscess.md' }] },
  'dist/indexes/concepts.json': { entries: [{ id: 'brain-abscess', kind: 'concept' }] },
  'dist/indexes/questions.json': { entries: [] },
  'dist/indexes/relations.json': { entries: [] },
  'dist/indexes/search.json': { entries: [{ id: 'brain-abscess', kind: 'concept', title: 'Brain abscess' }] },
  'dist/records/concept/brain-abscess.json': { id: 'brain-abscess', kind: 'concept', rawPath: 'notes/concepts/brain-abscess.md' },
  'dist/notes/concepts/brain-abscess.md': '# Brain abscess\n\n## Teaching Pearls\n',
};
const context = {
  console,
  window: { REX_PUBLICATION_BASE: 'dist/' },
  fetch: async (url) => {
    calls.push(url);
    if (!(url in payloads)) return { ok: false, status: 404, json: async () => ({}), text: async () => '' };
    const value = payloads[url];
    return { ok: true, status: 200, json: async () => value, text: async () => value };
  },
};
vm.createContext(context);
vm.runInContext(code, context);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

(async () => {
  const note = await context.ContentStore.getConcept('brain-abscess');
  assert(note.record.id === 'brain-abscess', 'selected concept record should load');
  assert(note.raw.includes('Teaching Pearls'), 'selected raw note should load');
  assert(calls.filter(url => url.includes('/notes/')).length === 1, 'only selected raw note should load');
  assert(calls.filter(url => url.includes('/records/')).length === 1, 'only selected record should load');
  assert(!calls.some(url => url.includes('data/')), 'legacy data JSON must not be requested');
  // Pages uploads the contents of dist at the site root. The loader's 404
  // fallback and the renderer must agree on that same publication directory.
  for (const prefix of ['dist/', '']) {
    const deployed = {};
    for (const [path, value] of Object.entries(payloads)) deployed[prefix + path.slice(5)] = value;
    deployed[prefix + 'records/concept/brain-abscess.json'] = {
      id: 'brain-abscess', kind: 'concept', rawPath: 'notes/concepts/brain-abscess.md',
      embeds: [{ target: 'brain.png', resolvedPath: 'assets/abc-brain.png' }],
    };
    deployed[prefix + 'notes/concepts/brain-abscess.md'] = '![[brain.png]]';
    deployed[prefix + 'assets/abc-brain.png'] = 'image bytes';
    const site = { console, window: {}, fetch: async url => ({
      ok: url in deployed, status: url in deployed ? 200 : 404,
      json: async () => deployed[url], text: async () => deployed[url],
    }) };
    vm.createContext(site);
    vm.runInContext(code, site);
    vm.runInContext(fs.readFileSync('js/note-renderer.js', 'utf8') + '\nglobalThis.NoteRenderer = NoteRenderer;', site);
    const loaded = await site.ContentStore.getConcept('brain-abscess');
    const html = site.NoteRenderer.render(loaded.raw, { record: loaded.record });
    const imageUrl = html.match(/src="([^"]+)"/)[1];
    assert((await site.fetch(imageUrl)).ok, 'rendered image must exist in ' + (prefix || 'root') + ' deployment: ' + imageUrl);
    assert(imageUrl === prefix + 'assets/abc-brain.png', 'image URL must follow the resolved publication base');
    assert(site.NoteRenderer.render('![remote](https://example.com/a.png)').includes('src="https://example.com/a.png"'), 'external image URL must remain unchanged');
  }
  console.log('content store lazy-load tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
