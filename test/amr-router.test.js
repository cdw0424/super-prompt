// Minimal tests using Node's built-in test runner
const test = require('node:test');
const assert = require('node:assert');
const { classifyTask, decideSwitch } = require('../src/amr/router');

test('classifyTask: heavy reasoning detected', () => {
  assert.strictEqual(classifyTask('architecture design & p95 profiling'), 'H');
});

test('decideSwitch: H from medium → high', () => {
  const d = decideSwitch('medium', 'H');
  assert.strictEqual(d.switch, 'high');
});

test('decideSwitch: back to medium from high when not H', () => {
  const d = decideSwitch('high', 'L1');
  assert.strictEqual(d.switch, 'medium');
});

