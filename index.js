#!/usr/bin/env node

/**
 * Super Prompt - Cursor-first CLI
 *
 * This is the npm entry point for the @cdw0424/super-prompt package.
 * For actual functionality, use the 'super-prompt' binary command.
 */

const { execSync } = require('child_process');
const path = require('path');

function showHelp() {
  console.log(`
🧠 Super Prompt (Cursor-first)

Quick install (scoped package):
  npm i -g @cdw0424/super-prompt

Usage:
  super-prompt [command] [options]

Commands:
  super:init           Initialize Cursor rules and commands
  optimize "query"     Run persona-assisted prompts
  sdd spec "desc"      Create specifications
  sdd plan "desc"      Create implementation plans
  sdd tasks "desc"     Break down into tasks
  sdd implement "desc" Start implementation

For full functionality, use the 'super-prompt' binary.
Run 'super-prompt --help' for detailed usage.

  `);
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }

  // Try to execute the Python CLI
  try {
    const cliPath = path.join(__dirname, 'scripts', 'super_prompt', 'cli.py');
    execSync(`python3 "${cliPath}" ${args.join(' ')}`, {
      stdio: 'inherit',
      cwd: process.cwd()
    });
  } catch (error) {
    console.error('❌ Failed to execute Python CLI. Make sure Python 3.7+ is installed.');
    console.error('Try: python3 --version');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, showHelp };
