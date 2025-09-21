#!/usr/bin/env node
/**
 * Standardize all Super Prompt command bodies:
 * - Remove extraneous inline code blocks
 * - Keep frontmatter and Execution line (already annotated with tool)
 * - Replace body with:
 *   - Title
 *   - Clear directives
 *   - Checklist/TODO plan with actionable steps
 *   - Guidance to use relevant MCP tools
 *   - Mandatory double-check step using sp_high (confession review)
 */
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const TARGET_DIRS = [
  path.join(ROOT, '.cursor', 'commands', 'super-prompt'),
  path.join(ROOT, 'packages', 'cursor-assets', 'commands', 'super-prompt'),
];

function* iterMarkdown(dir) {
  if (!fs.existsSync(dir)) return;
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) yield* iterMarkdown(full);
    else if (name.endsWith('.md')) yield full;
  }
}

function parseFrontmatter(text) {
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  return { fm: text.slice(0, end + 4), rest: text.slice(end + 4) };
}

function parseToolAndPersona(fm) {
  const toolMatch = fm.match(/\n\s*tool:\s*([\w\.-]+)\s*/);
  const personaMatch = fm.match(/\n\s*persona:\s*"([\w\-\.]+)"\s*/);
  return {
    tool: toolMatch ? toolMatch[1] : null,
    persona: personaMatch ? personaMatch[1] : null,
  };
}

function commandNameFromPath(p) {
  return path.basename(p, '.md');
}

function buildStandardBody(cmdName, tool, persona) {
  const titlePersona = persona || cmdName;
  const directiveTitle = `# ${titlePersona.replace(/(^|\b)([a-z])/g,(m,_,c)=>m.toUpperCase())} — Guided Execution`;

  const useLine = 'Use: /super-prompt/' + cmdName + ' "<your input>"';
  const doubleCheck = 'Run Double-Check: /super-prompt/high "Confession review for <scope>"';

  return `
${directiveTitle}

## Instructions
- Provide a short, specific input describing the goal and constraints
- Prefer concrete artifacts (file paths, diffs, APIs) for higher quality output
- ${useLine}

## Execution Checklist
- [ ] Define goal and scope
  - What outcome is expected? Any constraints or deadlines?
  - ${doubleCheck}

- [ ] Run the tool for primary analysis
  - ${useLine}
  - ${doubleCheck}

- [ ] Apply recommendations and produce artifacts
  - Implement changes, write tests/docs as needed
  - ${doubleCheck}

- [ ] Convert follow-ups into tasks
  - Use: /super-prompt/tasks "Break down follow-ups into tasks"
  - ${doubleCheck}

## Outputs
- Prioritized findings with rationale
- Concrete fixes/refactors with examples
- Follow-up TODOs (tests, docs, monitoring)
`.trimStart();
}

function rewriteBody(text, p) {
  const parsed = parseFrontmatter(text);
  if (!parsed) return null;
  const { fm, rest } = parsed;

  // Find Execution Mode section
  const execIdx = rest.indexOf('## Execution Mode');
  if (execIdx === -1) return null;

  // Keep only the Execution Mode header and the execution line, replace everything else
  const afterExec = rest.slice(execIdx);
  const firstBreak = afterExec.indexOf('\n\n');
  const execBlock = firstBreak !== -1 ? afterExec.slice(0, firstBreak) : afterExec;

  const { tool, persona } = parseToolAndPersona(fm);
  const cmdName = commandNameFromPath(p);
  const newBody = buildStandardBody(cmdName, tool, persona);

  const result = fm + '\n\n' + execBlock + '\n\n' + newBody + '\n';
  return result;
}

let scanned = 0, changed = 0;
for (const dir of TARGET_DIRS) {
  for (const p of iterMarkdown(dir)) {
    scanned++;
    const text = fs.readFileSync(p, 'utf-8');
    const updated = rewriteBody(text, p);
    if (updated) {  // Always update to ensure standardization
      fs.writeFileSync(p, updated);
      changed++;
    }
  }
}

console.error(`-------- standardize: scanned=${scanned} changed=${changed}`);

