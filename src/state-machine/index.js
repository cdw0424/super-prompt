// Fixed state-machine helpers (CJS, pure data helpers)

/** @typedef {'INTENT'|'TASK_CLASSIFY'|'PLAN'|'EXECUTE'|'VERIFY'|'REPORT'} Step */

/**
 * @typedef {Object} PlanSpec
 * @property {string} goal
 * @property {string[]} changes
 * @property {string[]} tests
 * @property {string[]} rollback
 */

/**
 * @typedef {Object} ExecutionResult
 * @property {string[]} diffs
 * @property {string[]} commands
 * @property {string[]=} notes
 */

/**
 * @typedef {Object} Verification
 * @property {boolean} passed
 * @property {string} summary
 * @property {string[]=} failures
 */

const StateMachine = {
  /** @type {Step[]} */
  steps: ['INTENT', 'TASK_CLASSIFY', 'PLAN', 'EXECUTE', 'VERIFY', 'REPORT'],
};

module.exports = { StateMachine };

