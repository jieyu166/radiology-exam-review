const fs = require('fs');
const vm = require('vm');

const context = { console, window: {} };
vm.createContext(context);
for (const file of ['due-window', 'queue-mix', 'wrong-criterion', 'calibration', 'weakness', 'drill', 'test-builder', 'exam-resume']) {
  const path = `js/scheduler/${file}.js`;
  if (fs.existsSync(path)) vm.runInContext(fs.readFileSync(path, 'utf8'), context);
}
const S = context.window.RexScheduler;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function taipei(iso) { return Date.parse(iso + '+08:00'); }

// ── due-window ──
const dw = S.dueWindow;
assert(dw.dayWindow(taipei('2026-10-10T03:59:00'), { dayStartHour: 4 }).dayKey === '2026-10-09', '03:59 belongs to previous study day');
assert(dw.dayWindow(taipei('2026-10-10T04:00:00'), { dayStartHour: 4 }).dayKey === '2026-10-10', '04:00 starts the new study day');
assert(dw.dayWindow(taipei('2026-10-10T00:30:00'), { dayStartHour: 0 }).dayKey === '2026-10-10', 'dayStartHour 0 uses midnight');
assert(dw.clampHour('x') === 4 && dw.clampHour(25) === 4 && dw.clampHour(7.9) === 7, 'clampHour');
const w = dw.dayWindow(taipei('2026-10-10T09:00:00'), { dayStartHour: 4 });
assert(dw.isDueToday({ state: 2, dueAt: taipei('2026-10-10T22:00:00') }, taipei('2026-10-10T09:00:00'), w) === true, 'review card due later today is due');
assert(dw.isDueToday({ state: 2, dueAt: taipei('2026-10-11T05:00:00') }, taipei('2026-10-10T09:00:00'), w) === false, 'review card due tomorrow is not due');
const now = taipei('2026-10-10T09:00:00');
assert(dw.isDueToday({ state: 1, dueAt: now + 5 * 60000 }, now, w) === false, 'learning step 5 min ahead is not served yet');
assert(dw.isDueToday({ state: 3, dueAt: now - 1 }, now, w) === true, 'relearning due now is served');
assert(dw.isDueToday(null, now, w) === true && dw.isDueToday({ state: 0, dueAt: now + 1e9 }, now, w) === true, 'new / missing cards are always due');

// ── queue-mix ──
const qm = S.queueMix;
const kinds = [];
for (let served = 0; served < 8; served++) kinds.push(qm.pickNextKind({ served, learning: 0, dueReview: 10, newAvailable: 50, newRemaining: 20 }));
assert(kinds.join(',') === 'due,due,due,new,due,due,due,new', 'interleave: ' + kinds.join(','));
assert(qm.pickNextKind({ served: 3, learning: 1, dueReview: 10, newAvailable: 50, newRemaining: 20 }) === 'learning', 'learning always first');
assert(qm.pickNextKind({ served: 0, learning: 0, dueReview: 0, newAvailable: 5, newRemaining: 5 }) === 'new', 'new when nothing due');
assert(qm.pickNextKind({ served: 0, learning: 0, dueReview: 0, newAvailable: 5, newRemaining: 0 }) === null, 'nothing when allowance exhausted');
assert(qm.pickNextKind({ served: 3, learning: 0, dueReview: 10, newAvailable: 0, newRemaining: 20 }) === 'due', 'no new available falls back to due');
assert(qm.parseNewLimit(undefined) === 20 && qm.parseNewLimit('35') === 35 && qm.parseNewLimit('999') === 200 && qm.parseNewLimit('-3') === 20, 'parseNewLimit table');
assert(qm.remainingNewToday(5, 20) === 15 && qm.remainingNewToday(25, 20) === 0 && qm.remainingNewToday(0, NaN) === 0, 'remainingNewToday');
const logs = [
  { questionId: 'q1', state: 0, reviewedAt: w.dayStart + 1000 },
  { questionId: 'q1', state: 1, reviewedAt: w.dayStart + 2000 },
  { questionId: 'q2', state: 2, reviewedAt: w.dayStart + 3000 },
  { questionId: 'q3', state: 0, reviewedAt: w.dayStart - 10 },
];
assert(qm.introducedToday(logs, w) === 1, 'introducedToday counts first New rating inside the window only');

// ── wrong-criterion ──
const wc = S.wrongCriterion;
const progress = { answers: { '2017-008': { correct: true, ts: 200 }, '2020-100': { correct: false, ts: 150 }, '2019-521': { correct: false, ts: 300 } }, starred: {} };
assert(wc.isWrong(progress.answers['2020-100']) && !wc.isWrong(progress.answers['2017-008']) && !wc.isWrong(undefined), 'latest attempt decides wrong');
assert(wc.wrongIds(progress).join(',') === '2019-521,2020-100', 'wrongIds newest first');

// ── calibration ──
const cal = S.calibration;
const attempts = [];
for (let i = 0; i < 10; i++) attempts.push({ questionId: 'q' + i, confidence: 3, isCorrect: i < 6, clientTs: 1000 + i });
attempts.push({ questionId: 'nc', confidence: null, isCorrect: true, clientTs: 5 });
const buckets = cal.calibration(attempts);
assert(buckets[2].n === 10 && buckets[2].correct === 6 && Math.abs(buckets[2].accuracy - 0.6) < 1e-9, 'level 3 bucket');
assert(buckets[0].n === 0 && buckets[0].accuracy === null, 'level 1 empty bucket has null accuracy');
const many = [];
for (let i = 0; i < 25; i++) many.push({ questionId: 'h' + i, confidence: 3, isCorrect: false, clientTs: i });
const hc = cal.hypercorrectionCandidates(many);
assert(hc.length === 20 && hc[0].questionId === 'h24' && hc[19].questionId === 'h5', 'hypercorrection: 20 newest first');

// ── weakness ──
const wk = S.weakness;
const wrongEntries = [
  { id: 'm1', subspecialty: 'MSK', conceptIds: ['foot-ankle-soft-tissue-masses'] },
  { id: 'm2', subspecialty: 'MSK', conceptIds: ['foot-ankle-soft-tissue-masses'] },
  { id: 'm3', subspecialty: 'MSK', conceptIds: ['other'] },
  { id: 'c1', subspecialty: 'CH', conceptIds: [] },
  { id: 'c2', subspecialty: 'CH', conceptIds: [] },
  { id: 'n1', subspecialty: 'NR', conceptIds: [] },
];
const groups = wk.groupByTopic(wk.rowsFromEntries(wrongEntries), ['m2', 'c1', 'm1', 'm3', 'c2', 'n1']);
assert(groups.map(g => `${g.label}:${g.size}`).join(',') === 'MSK:3,CH:2,foot-ankle-soft-tissue-masses:2', 'groups: ' + groups.map(g => `${g.label}:${g.size}`).join(','));
assert(!groups.find(g => g.label === 'NR'), 'single-question group omitted');
assert(groups[0].anchor === 'm2' && groups[1].anchor === 'c1', 'anchor is the most recently wrong question');
assert(wk.groupByTopic(wk.rowsFromEntries(wrongEntries), [], { limit: 1 }).length === 1, 'limit respected');
const multiRows = wk.rowsFromEntries([{ id: 'g1', subspecialty: ['GI', 'ABD'], conceptIds: [] }, { id: 'g2', subspecialty: ['GU', 'ABD'], conceptIds: [] }]);
assert(wk.groupByTopic(multiRows, ['g1', 'g2']).map(g => `${g.label}:${g.size}`).join(',') === 'ABD:2', 'multi-subspecialty entries contribute a row per subspecialty');

// ── drill ──
const dr = S.drill;
const hits = [{ id: 'a16', year: 2016 }, { id: 'b16', year: 2016 }, { id: 'a17', year: 2017 }, { id: 'a18', year: 2018 }, { id: 'b18', year: 2018 }, { id: 'a16', year: 2016 }, { id: 'anchor', year: 2017 }];
const pick1 = dr.pickInterleaved(hits, { anchor: 'anchor', n: 10, seed: 42 });
const pick2 = dr.pickInterleaved(hits, { anchor: 'anchor', n: 10, seed: 42 });
assert(JSON.stringify(pick1) === JSON.stringify(pick2), 'deterministic');
assert(pick1.length === 5 && !pick1.includes('anchor') && new Set(pick1).size === 5, 'dedupe + exclude anchor');
assert(pick1[0].endsWith('16') && pick1[1].endsWith('17') && pick1[2].endsWith('18'), 'round-robin across years: ' + pick1.join(','));
assert(dr.pickInterleaved(hits, { n: 2, seed: 1 }).length === 2, 'n respected');
assert(dr.hashSeed('2026-10-10') === dr.hashSeed('2026-10-10') && dr.hashSeed('a') !== dr.hashSeed('b'), 'hashSeed stable');
console.log('scheduler tests passed');
