// Auto Model Router — classification and switch decision (CJS)

/** @typedef {import('../types/amr').TaskClass} TaskClass */
/** @typedef {import('../types/amr').ReasoningLevel} ReasoningLevel */
/** @typedef {import('../types/amr').RouterDecision} RouterDecision */

const H_PATTERNS = [
  /architecture|design(?!\s*small)|hexagonal|domain model|DDD/i,
  /security|CWE|auth(entication|orization)|RBAC|secret|XSS|SQLi/i,
  /performance|profil(ing)?|latency|p95|throughput|memory/i,
  /debug(ging)?|root\s*cause|unknown\s*error|flaky/i,
  /migration|backfill|data model/i,
  /shopify|rate limit|idempotency|backoff/i,
  /cross-?module|monorepo|multi-?module/i,
];

/**
 * @param {string} input
 * @returns {TaskClass}
 */
function classifyTask(input) {
  const s = (input || '').slice(0, 4000);
  if (H_PATTERNS.some((rx) => rx.test(s))) return 'H';
  if (/\b(test|jest|unit|integration|type(s)?|migration)\b/i.test(s)) return 'L1';
  if (/\b(lint|format|rename|prettier|eslint|find[- ]?replace|small refactor)\b/i.test(s)) return 'L0';
  return 'L1';
}

/**
 * @param {ReasoningLevel} current
 * @param {TaskClass} cls
 * @returns {RouterDecision}
 */
function decideSwitch(current, cls) {
  if (cls === 'H' && current !== 'high') return { switch: 'high', reason: 'deep_planning' };
  if (cls !== 'H' && current !== 'medium') return { switch: 'medium', reason: 'execution' };
  return {};
}

module.exports = { classifyTask, decideSwitch };

