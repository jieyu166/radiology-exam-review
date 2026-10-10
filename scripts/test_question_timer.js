const fs = require('fs');
const vm = require('vm');

const context = { console };
vm.createContext(context);
vm.runInContext(fs.readFileSync('js/question-timer.js', 'utf8') + '\nglobalThis.QuestionTimer = QuestionTimer;', context);
const T = context.QuestionTimer;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

let s = T.startTimer(1000);
assert(T.read(s, 6000).elapsedMs === 5000, 'running timer accumulates');
s = T.hide(s, 6000);
assert(T.read(s, 60000).elapsedMs === 5000, 'hidden time is not counted');
s = T.hide(s, 70000);
assert(s.accumulatedMs === 5000 && s.runningSince === null, 'hide is idempotent');
s = T.show(s, 80000);
const sameShow = T.show(s, 90000);
assert(sameShow.runningSince === 80000, 'show while running keeps original start');
assert(T.read(s, 85000).elapsedMs === 10000, 'resumed timer continues');
s = T.pause(s, 85000);
assert(T.read(s, 999999).elapsedMs === 10000 && T.read(s, 999999).outlier === false, 'pause freezes');
const long = T.startTimer(0);
const reading = T.read(long, 11 * 60 * 1000);
assert(reading.elapsedMs === T.MAX_QUESTION_MS && reading.outlier === true, 'over 10 minutes is clamped and flagged');
assert(T.formatElapsed(reading.elapsedMs, reading.outlier) === '10:00+', 'outlier label');
assert(T.formatElapsed(42000) === '0:42', 'm:ss format');
assert(T.formatElapsed(-5) === '0:00', 'negative clamps to 0');
assert(T.read(null, 5).elapsedMs === 0, 'null state reads zero');
console.log('question timer tests passed');
