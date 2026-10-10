const fs = require('fs');
const vm = require('vm');

const context = { console, window: {} };
vm.createContext(context);
for (const file of ['wrong-criterion', 'test-builder', 'exam-resume']) vm.runInContext(fs.readFileSync(`js/scheduler/${file}.js`, 'utf8'), context);
const tb = context.window.RexScheduler.testBuilder;
const er = context.window.RexScheduler.examResume;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

// normalization (spec example table)
const n1 = tb.normalizeFilters({ status: ['wrong', 'wrong', 'nope'], count: 500 });
assert(JSON.stringify(n1.status) === '["wrong"]' && n1.count === 100 && n1.tutor === false && n1.timed === true, 'row 1: ' + JSON.stringify(n1));
const n2 = tb.normalizeFilters({ count: 0, tutor: 'yes', timed: false });
assert(n2.count === 1 && n2.tutor === false && n2.timed === false, 'row 2: ' + JSON.stringify(n2));
assert(tb.normalizeFilters({}).count === 20 && tb.normalizeFilters({ years: ['2020', 2020, 'x'] }).years.join() === '2020', 'defaults + numeric years');

// pool: OR between statuses, AND across dimensions, unscorable excluded
const entries = [
  { id: '2020-001', years: [2020], subspecialty: 'CH', conceptIds: ['abpa'], scorable: true },
  { id: '2020-002', years: [2020], subspecialty: 'CH', conceptIds: [], scorable: true },
  { id: '2020-003', years: [2020], subspecialty: 'CH', conceptIds: [], scorable: true },
  { id: '2020-004', years: [2020], subspecialty: 'NR', conceptIds: [], scorable: true },
  { id: '2019-001', years: [2019], subspecialty: 'CH', conceptIds: [], scorable: true },
  { id: '2020-005', years: [2020], subspecialty: 'CH', conceptIds: [], scorable: false },
  { id: '2021-144', years: [2021, 2022], subspecialty: 'NR', conceptIds: [], scorable: true },
];
const progress = {
  answers: { '2020-001': { correct: false }, '2020-002': { correct: true }, '2020-004': { correct: false }, '2019-001': { correct: false }, '2020-005': { correct: false } },
  starred: { '2020-003': true, '2020-002': true },
};
const pool = tb.buildPool(entries, progress, { status: ['wrong', 'bookmarked'], years: [2020], subspecialties: ['CH'] });
assert(pool.join(',') === '2020-001,2020-002,2020-003', 'wrong OR bookmarked AND 2020 AND CH: ' + pool.join(','));
assert(tb.buildPool(entries, progress, { status: ['unseen'] }).join(',') === '2020-003,2021-144', 'unseen = no attempt (scorable only)');
assert(tb.buildPool(entries, progress, { status: ['correct'], concepts: ['abpa'] }).length === 0, 'AND across dimensions');
assert(tb.buildPool(entries, progress, { years: [2022] }).join(',') === '2021-144', 'multi-year entry matches either year');
assert(tb.buildPool(entries, progress, {}).length === 6, 'no filters = all scorable');

// sampling is reproducible for a seed and bounded by count/pool
const all = tb.buildPool(entries, progress, {});
assert(JSON.stringify(tb.sample(all, 3, 7)) === JSON.stringify(tb.sample(all, 3, 7)), 'same seed same paper');
assert(tb.sample(all, 3, 7).length === 3 && tb.sample(all, 50, 7).length === all.length, 'count bounded by pool');
assert(JSON.stringify(tb.sample(all, 6, 7)) !== JSON.stringify(tb.sample(all, 6, 8)) || all.length < 2, 'different seed usually differs');

// resume
assert(er.resumeIndex(['a', 'b', 'c', 'd', 'e'], { a: 'A', b: 'B', c: 'C', d: 'D' }) === 4, 'first unanswered');
assert(er.resumeIndex(['a', 'b'], { a: 'A', b: 'B' }) === 0, 'all answered → 0');
assert(er.resumeIndex(['a', 'b'], {}) === 0 && er.resumeIndex([], {}) === 0, 'empty cases');
// ── ExamSession state machine (UI layer, pure) ──
vm.runInContext(fs.readFileSync('js/exam-session.js', 'utf8') + '\nglobalThis.ExamSession = ExamSession;', context);
const ES = context.ExamSession;
const session = ES.start({ entries, progress, filters: { status: [], count: 5, timed: true }, seed: 7, now: 1000, secondsPerQuestion: 90 });
assert(session.entryIds.length === 5 && session.poolSize === 6 && session.secondsPerQuestion === 90 && session.seed === 7, 'start builds a 5-question timed paper: ' + JSON.stringify(session.entryIds));
assert(JSON.stringify(ES.start({ entries, progress, filters: { count: 5 }, seed: 7, now: 1 }).entryIds) === JSON.stringify(session.entryIds), 'same seed reproduces the paper');
const ids = session.entryIds;
ES.answer(session, ids[0], 'A', 1200); ES.advance(session);
ES.answer(session, ids[1], 'B', 800); ES.advance(session);
assert(session.index === 2 && ES.currentId(session) === ids[2], 'advance moves to question 3');
ES.expire(session, ids[2]);
assert(session.answers[ids[2]] === ES.EXPIRED && session.index === 3 && ES.currentId(session) === ids[3], 'countdown expiry records unanswered and shows question 4');
ES.answer(session, ids[3], 'C'); ES.advance(session);
// reload before answering question 5 → resume at index 4 (expired question is not revisited)
assert(ES.resumeIndex(session) === 4, 'resume at first unanswered (expired counts as handled): ' + ES.resumeIndex(session));
ES.answer(session, ids[4], 'D');
assert(ES.resumeIndex(session) === 0, 'all answered → 0');
assert(!ES.isFinished(session) && ES.advance(session) && ES.isFinished(session), 'advance past last finishes');
const scoring = ES.scoringAnswers(session);
assert(Object.keys(scoring).length === 4 && !(ids[2] in scoring) && ES.expiredIds(session).join() === ids[2], 'expired question excluded from scoring answers');
const untimed = ES.start({ entries, progress, filters: { timed: false, count: 3 }, seed: 1, now: 1, secondsPerQuestion: 90 });
assert(untimed.secondsPerQuestion === 0, 'timed=false disables the countdown');
const removed = ES.pruneMissing(session, ids.filter(id => id !== ids[1]));
assert(removed.join() === ids[1] && session.entryIds.length === 4, 'missing ids pruned and reported');
console.log('exam builder tests passed');
