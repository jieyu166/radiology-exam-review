const fs = require('fs');
const vm = require('vm');
const path = require('path');

function loadUmd() {
  const candidates = [path.join(process.env.TEMP || '/tmp', 'ts-fsrs.umd.js'), 'node_modules/ts-fsrs/dist/index.umd.js', 'tmp/ts-fsrs.umd.js'];
  for (const file of candidates) if (fs.existsSync(file)) return fs.readFileSync(file, 'utf8');
  return null;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const UMD_URL = 'https://cdn.jsdelivr.net/npm/ts-fsrs@5.4.2/dist/index.umd.js';
async function ensureUmd() {
  const local = loadUmd();
  if (local) return local;
  const res = await fetch(UMD_URL);
  if (!res.ok) throw new Error('cannot download ts-fsrs UMD: HTTP ' + res.status);
  const text = await res.text();
  fs.mkdirSync('tmp', { recursive: true });
  fs.writeFileSync('tmp/ts-fsrs.umd.js', text);
  return text;
}

(async () => {
const umd = await ensureUmd();

// ── without the library: available() is false and nothing throws ──
{
  const ctx = { console, window: {} };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync('js/scheduler/fsrs-adapter.js', 'utf8'), ctx);
  const f = ctx.window.RexScheduler.fsrs;
  assert(f.available() === false, 'available() false without FSRS');
  assert(f.rate(null, 'q', Date.now(), 'good') === null && f.preview(null, Date.now()) === null && f.createCard('q', Date.now()) === null, 'graceful null without library');
}

// ── with the library ──
const context = { console, window: {} };
vm.createContext(context);
vm.runInContext(umd + '\nwindow.FSRS = FSRS;', context);
vm.runInContext(fs.readFileSync('js/scheduler/fsrs-adapter.js', 'utf8'), context);
const f = context.window.RexScheduler.fsrs;
assert(f.available() === true, 'available() true with FSRS');
const T = Date.parse('2026-10-10T01:00:00Z');
const fresh = f.createCard('2020-100', T);
assert(fresh.state === 0 && fresh.reps === 0 && fresh.questionId === '2020-100', 'empty card row');

const pv = f.preview(null, T);
assert(pv && ['again', 'hard', 'good', 'easy'].every(k => Number.isFinite(pv[k].dueAt)), 'preview has four outcomes');
const rated = f.rate(null, '2020-100', T, 'good');
assert(rated.cardRow.reps === 1 && rated.cardRow.state === 1, 'first good rating → Learning with reps 1: ' + JSON.stringify(rated.cardRow));
assert(rated.cardRow.dueAt === T + 10 * 60 * 1000, 'first good on a new card is due in 10 minutes (learning step 2)');
assert(rated.log.state === 0 && rated.log.rating === 'good' && rated.log.reviewedAt === T, 'log records the state before rating');
assert(pv.good.dueAt === rated.cardRow.dueAt, 'preview matches the actual rating');
assert(f.rate(rated.cardRow, '2020-100', T + 1000, 'bogus') === null, 'invalid rating returns null');

// graduate: good again after the 10-minute step → Review with days
const second = f.rate(rated.cardRow, '2020-100', rated.cardRow.dueAt, 'good');
assert(second.cardRow.state === 2 && second.cardRow.scheduledDays >= 1, 'second good graduates to Review: ' + JSON.stringify(second.cardRow));
assert(second.log.state === 1, 'log state before = Learning');
const r = f.retrievability(second.cardRow, second.cardRow.dueAt);
assert(r !== null && r > 0 && r <= 1, 'retrievability in (0,1]');
assert(f.retrievability(fresh, T) === null, 'retrievability of a new card is null');
const again = f.rate(second.cardRow, '2020-100', second.cardRow.dueAt, 'again');
assert(again.cardRow.lapses === 1 && again.cardRow.state === 3, 'again on review → Relearning with a lapse');

// interval labels
assert(f.intervalLabel(T + 30 * 1000, T) === '<1 分', '<1 分');
assert(f.intervalLabel(T + 10 * 60 * 1000, T) === '10 分', '10 分');
assert(f.intervalLabel(T + 3 * 86400000, T) === '3 天', '3 天');
assert(f.intervalLabel(T + 45 * 86400000, T) === '1.5 月', '1.5 月, got ' + f.intervalLabel(T + 45 * 86400000, T));

// ── ReviewView queue logic (pure) with the real scheduler modules ──
for (const file of ['due-window', 'queue-mix']) vm.runInContext(fs.readFileSync(`js/scheduler/${file}.js`, 'utf8'), context);
vm.runInContext(fs.readFileSync('js/review-view.js', 'utf8') + '\nglobalThis.ReviewView = ReviewView;', context);
const RV = context.ReviewView;
const nowT = Date.parse('2026-10-10T09:00:00+08:00');
const entries = [];
for (let i = 1; i <= 60; i++) entries.push({ id: `2020-${String(i).padStart(3, '0')}`, scorable: true });
entries.push({ id: '2018-360', scorable: false });
const cards = {};
for (let i = 1; i <= 3; i++) cards[`2020-${String(i).padStart(3, '0')}`] = { questionId: `2020-${String(i).padStart(3, '0')}`, state: 1, dueAt: nowT - 1000 * i, updatedAt: 1 };
cards['2020-004'] = { questionId: '2020-004', state: 1, dueAt: nowT + 300000, updatedAt: 1 };
for (let i = 5; i <= 14; i++) cards[`2020-${String(i).padStart(3, '0')}`] = { questionId: `2020-${String(i).padStart(3, '0')}`, state: 2, dueAt: nowT + i * 1000, updatedAt: 1 };
cards['2020-015'] = { questionId: '2020-015', state: 2, dueAt: nowT + 36 * 3600 * 1000, updatedAt: 1 };
const logsToday = [{ questionId: '2020-020', state: 0, rating: 'good', reviewedAt: nowT - 60000 }];
const progress = { cards, reviewLogs: logsToday, settings: { newPerDay: 5, dayStartHour: 4 } };
const queue = RV.buildQueue({ entries, progress, now: nowT, settings: progress.settings });
const c = RV.counts(queue);
assert(c.learning === 3 && c.due === 10 && c.newAvailable === 45 && c.newRemaining === 4 && c.introducedToday === 1, 'counts: ' + JSON.stringify(c));
assert(queue.tomorrowDue === 1, 'tomorrow due counted');
assert(queue.learning[0] === '2020-003', 'learning ordered by dueAt (most overdue first)');
const seq = [];
let item;
while ((item = RV.takeNext(queue)) && seq.length < 20) seq.push(item.kind);
assert(seq.slice(0, 3).join(',') === 'learning,learning,learning', 'learning first: ' + seq.join(','));
assert(seq.slice(3).join(',') === 'new,due,due,due,new,due,due,due,new,due,due,due,new,due', 'mixing after learning (served counts continue; 4 new + 10 due): ' + seq.slice(3).join(','));
assert(seq.length === 17, 'all 3 learning + 10 due + 4 allowed new served');
assert(queue.newRemaining === 0, 'new allowance consumed');
assert(RV.takeNext(queue) === null, 'queue exhausted');
assert(RV.defaultRating({ correct: true }) === 'good' && RV.defaultRating({ correct: false }) === 'again' && RV.defaultRating(null) === 'again', 'default rating focus');

// rate() goes through a store stub: card + log + review attempt
const stored = { cards: {}, logs: [], answers: [] };
const store = {
  getCard: id => stored.cards[id] || null,
  setCard: row => { stored.cards[row.questionId] = row; },
  appendReviewLog: log => { stored.logs.push(log); return log; },
  recordAnswer: (id, r) => { stored.answers.push([id, r]); },
};
const outcome = RV.rate(store, '2020-100', 'good', nowT, { chosen: 'B', correct: true, scorable: true, elapsedMs: 1000, confidence: 2 });
assert(outcome.card.reps === 1 && stored.cards['2020-100'].state === 1, 'rate stores the card');
assert(stored.logs.length === 1 && stored.logs[0].state === 0 && stored.logs[0].rating === 'good', 'rate appends a review log');
assert(stored.answers.length === 1 && stored.answers[0][1].source === 'review' && stored.answers[0][1].confidence === 2, 'rate records a review attempt');
const bar = RV.ratingBar(stored.cards['2020-100'], nowT, 'again');
assert((bar.match(/data-rating=/g) || []).length === 4 && bar.includes('rating-again is-default'), 'rating bar renders four buttons with default focus');
assert(RV.countsHtml(RV.buildQueue({ entries, progress, now: nowT, settings: progress.settings }), 61).includes('學習中 <strong>3</strong>'), 'counts html');
// ── AnalyticsView model ──
for (const file of ['wrong-criterion', 'calibration', 'weakness', 'drill']) vm.runInContext(fs.readFileSync(`js/scheduler/${file}.js`, 'utf8'), context);
vm.runInContext(fs.readFileSync('js/analytics-view.js', 'utf8') + '\nglobalThis.AnalyticsView = AnalyticsView;', context);
const AV = context.AnalyticsView;
const qEntries = [
  { id: 'm1', years: [2020], subspecialty: 'MSK', conceptIds: ['foot'] }, { id: 'm2', years: [2021], subspecialty: 'MSK', conceptIds: ['foot'] }, { id: 'm3', years: [2022], subspecialty: 'MSK', conceptIds: [] },
  { id: 'c1', years: [2020], subspecialty: 'CH', conceptIds: [] }, { id: 'c2', years: [2020], subspecialty: 'CH', conceptIds: [] }, { id: 'n1', years: [2019], subspecialty: 'NR', conceptIds: [] },
];
const attemptsA = [];
['m1', 'm2', 'm3', 'c1', 'c2', 'n1'].forEach((id, i) => attemptsA.push({ clientId: 'w' + i, questionId: id, chosen: 'A', isCorrect: false, confidence: 3, clientTs: 100 + i }));
for (let i = 0; i < 4; i++) attemptsA.push({ clientId: 'ok' + i, questionId: 'ok' + i, chosen: 'B', isCorrect: true, confidence: 3, clientTs: 50 + i });
const progressA = { attempts: attemptsA, answers: {}, starred: {} };
attemptsA.forEach(a => { progressA.answers[a.questionId] = { correct: a.isCorrect, ts: a.clientTs, last: a.chosen }; });
const model = AV.buildModel({ entries: qEntries, progress: progressA, conceptNames: { foot: 'Foot & ankle soft-tissue masses' } });
assert(model.buckets[2].n === 10 && model.buckets[2].correct === 4 && model.buckets[0].accuracy === null, 'calibration buckets in model');
assert(model.hyper.length === 6 && model.hyper[0].questionId === 'n1' && model.hyper[0].subspecialty === 'NR', 'hypercorrection newest first with entry info');
assert(model.wrongCount === 6, 'wrong count');
assert(model.groups.map(g => `${g.label}:${g.size}`).join(',') === 'MSK:3,CH:2,Foot & ankle soft-tissue masses:2', 'groups with concept names: ' + model.groups.map(g => `${g.label}:${g.size}`).join(','));
const html = AV.render(model);
assert(html.includes('有把握卻答錯') && (html.match(/href="#\/card\?qid=/g) || []).length === 6 && (html.match(/data-drill-group=/g) || []).length === 3, 'render links and drill buttons');
const byId = new Map(qEntries.map(e => [e.id, e]));
const drill = AV.drillForGroup(model.groups[0], byId, nowT, { dayStartHour: 4 });
assert(drill.length === 2 && !drill.includes(model.groups[0].anchor), 'group drill excludes anchor and keeps the other members');
assert(JSON.stringify(drill) === JSON.stringify(AV.drillForGroup(model.groups[0], byId, nowT, { dayStartHour: 4 })), 'group drill deterministic for the day');
console.log('review view tests passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
