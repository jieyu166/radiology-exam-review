/* =====================================================
   content-store.js — vault-native publication loader
   ===================================================== */

const ContentStore = (function () {
  'use strict';

  const INDEX_FILES = {
    concepts: 'indexes/concepts.json',
    questions: 'indexes/questions.json',
    relations: 'indexes/relations.json',
    search: 'indexes/search.json',
  };
  let _base = null;
  let _manifestPromise = null;
  let _indexesPromise = null;
  const _recordCache = new Map();
  const _rawCache = new Map();

  function _publicationBase() {
    if (_base !== null) return _base;
    const configured = typeof window !== 'undefined' && window.REX_PUBLICATION_BASE;
    const value = typeof configured === 'string' && configured.trim() ? configured.trim() : 'dist/';
    _base = value.replace(/\\/g, '/').replace(/^\/*/, '').replace(/\/*$/, '') + '/';
    return _base;
  }

  function _safePackagePath(value) {
    if (typeof value !== 'string' || !value || value.startsWith('/') || value.includes('\\')) return false;
    return value.split('/').every(part => part && part !== '..' && part !== '.');
  }

  function _url(path) {
    if (!_safePackagePath(path)) throw new Error('不合法的 publication path：' + path);
    return _publicationBase() + path;
  }

  async function _json(path) {
    const requestedBase = _publicationBase();
    let response = await fetch(_url(path), { cache: 'no-store' });
    if (!response.ok && response.status === 404 && requestedBase === 'dist/') {
      _base = '';
      response = await fetch(_url(path), { cache: 'no-store' });
    }
    if (!response.ok) throw new Error('無法載入 publication JSON：' + path + ' (' + response.status + ')');
    return response.json();
  }

  async function _text(path) {
    const requestedBase = _publicationBase();
    let response = await fetch(_url(path), { cache: 'no-store' });
    if (!response.ok && response.status === 404 && requestedBase === 'dist/') {
      _base = '';
      response = await fetch(_url(path), { cache: 'no-store' });
    }
    if (!response.ok) throw new Error('無法載入 publication note：' + path + ' (' + response.status + ')');
    return response.text();
  }

  async function loadManifest() {
    if (!_manifestPromise) _manifestPromise = _json('manifest.json');
    return _manifestPromise;
  }

  async function loadIndexes() {
    if (!_indexesPromise) {
      _indexesPromise = Promise.all([
        loadManifest(),
        _json(INDEX_FILES.concepts),
        _json(INDEX_FILES.questions),
        _json(INDEX_FILES.relations),
        _json(INDEX_FILES.search),
      ]).then(([manifest, concepts, questions, relations, search]) => ({
        manifest,
        concepts,
        questions,
        relations,
        search,
      }));
    }
    return _indexesPromise;
  }

  async function _entry(id, kind) {
    const data = await loadIndexes();
    const entry = (data.manifest.entries || []).find(item => item && item.id === id && (!kind || item.kind === kind));
    if (!entry) return null;
    if (!_safePackagePath(entry.recordPath) || !_safePackagePath(entry.rawPath)) {
      throw new Error('publication entry path invalid：' + id);
    }
    return entry;
  }

  async function getRecord(id, kind) {
    const key = (kind || '') + ':' + id;
    if (_recordCache.has(key)) return _recordCache.get(key);
    const entry = await _entry(id, kind);
    if (!entry) return null;
    const record = await _json(entry.recordPath);
    _recordCache.set(key, record);
    return record;
  }

  async function getRawNote(id, kind) {
    const key = (kind || '') + ':' + id;
    if (_rawCache.has(key)) return _rawCache.get(key);
    const entry = await _entry(id, kind);
    if (!entry) return null;
    const text = await _text(entry.rawPath);
    _rawCache.set(key, text);
    return text;
  }

  async function getNote(id, kind) {
    const record = await getRecord(id, kind);
    if (!record) return null;
    const raw = await getRawNote(id, kind);
    return { record, raw };
  }

  async function getConcept(id) {
    return getNote(id, 'concept');
  }

  async function getQuestion(id) {
    return getNote(id, 'question');
  }

  async function getIndexes() {
    return loadIndexes();
  }

  async function getRelations() {
    const data = await loadIndexes();
    return data.relations;
  }

  async function search(query) {
    const data = await loadIndexes();
    const needle = String(query || '').trim().toLowerCase();
    if (!needle) return data.search.entries || [];
    return (data.search.entries || []).filter(item => JSON.stringify(item).toLowerCase().includes(needle));
  }

  function configure(options) {
    if (options && typeof options.base === 'string') {
      _base = options.base;
      _base = _base.replace(/\\/g, '/').replace(/^\/*/, '').replace(/\/*$/, '') + '/';
    }
    clearCache();
  }

  function clearCache() {
    _manifestPromise = null;
    _indexesPromise = null;
    _recordCache.clear();
    _rawCache.clear();
  }

  return {
    loadManifest,
    loadIndexes,
    getIndexes,
    getRecord,
    getRawNote,
    getNote,
    getConcept,
    getQuestion,
    getRelations,
    search,
    getPublicationBase: _publicationBase,
    configure,
    clearCache,
  };
})();
