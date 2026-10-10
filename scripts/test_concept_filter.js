const fs = require('fs');
const vm = require('vm');

const context = { console };
vm.createContext(context);
vm.runInContext(fs.readFileSync('js/concept-filter.js', 'utf8') + '\nglobalThis.ConceptFilter = ConceptFilter;', context);
const CF = context.ConceptFilter;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const entries = [
  { id: 'brain-abscess', name: 'Brain abscess', subspecialty: ['NR'], aliases: ['cerebral abscess'] },
  { id: 'aaa', name: 'AAA', subspecialty: ['ABD', 'CV'] },
  { id: 'gi-bleed', name: 'GI bleeding CTA', subspecialty: ['GI'] },
  { id: 'gu-stone', name: 'Ureteric stone', subspecialty: ['GU'] },
  { id: 'mammo', name: 'Mammography BI-RADS', subspecialty: ['Breast'] },
  { id: 'misc', name: 'Misc note', subspecialty: [] },
  { id: 'er-triage', name: 'ER triage imaging', subspecialty: 'ER' },
];

// spec example: NR, ABD, GU, GI, Breast, (empty) → ABD, NR, Breast, GU, GI, Uncategorized (after "All")
const pills = CF.buildPills(entries);
assert(pills[0].key === '' && pills[0].label === '全部' && pills[0].count === 7, 'All pill first with total count');
const order = pills.slice(1).map(p => p.label).join(',');
assert(order === 'ABD,CV,NR,Breast,ER,GI,GU,未分類', 'canonical first, extras alphabetical, uncategorized last: ' + order);
assert(pills.find(p => p.key === 'ABD').count === 1 && pills.find(p => p.key === CF.UNCATEGORIZED).count === 1, 'counts per subspecialty');

// filtering
assert(CF.filterConcepts(entries, { sub: 'CV' }).map(e => e.id).join() === 'aaa', 'filter by one subspecialty');
assert(CF.filterConcepts(entries, { sub: 'ER' }).map(e => e.id).join() === 'er-triage', 'string subspecialty is treated as a one-item list');
assert(CF.filterConcepts(entries, { sub: CF.UNCATEGORIZED }).map(e => e.id).join() === 'misc', 'uncategorized filter');
assert(CF.filterConcepts(entries, { sub: '' }).length === 7, 'empty key = all');
assert(CF.filterConcepts(entries, { query: 'cerebral' }).map(e => e.id).join() === 'brain-abscess', 'alias search');
assert(CF.filterConcepts(entries, { query: 'GI BLEED' }).map(e => e.id).join() === 'gi-bleed', 'case-insensitive multi-term search');
assert(CF.filterConcepts(entries, { sub: 'ABD', query: 'aaa' }).length === 1 && CF.filterConcepts(entries, { sub: 'NR', query: 'aaa' }).length === 0, 'subspecialty AND query');
console.log('concept filter tests passed');
