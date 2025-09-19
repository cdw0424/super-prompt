#!/usr/bin/env node
'use strict';

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

async function run() {
  const sub = process.argv[2]; // 'call'
  const tool = process.argv[3]; // e.g. 'sp.init'
  const kv = Object.fromEntries(
    process.argv.slice(4).map(arg => {
      const [k, v = 'true'] = arg.replace(/^--/, '').split('=');
      // boolean/number 감지
      if (v === 'true' || v === 'false') return [k, v === 'true'];
      if (!Number.isNaN(Number(v))) return [k, Number(v)];
      return [k, v];
    })
  );

  if (sub !== 'call' || !tool) {
    console.error('-------- Usage: mcp-client call <toolName> [--key=value ...]');
    process.exit(2);
  }

  // 강제 MCP 전용 모드 (백도어 금지)
  process.env.SUPER_PROMPT_REQUIRE_MCP = '1';

  // 프로젝트 루트 기본값
  if (!process.env.SUPER_PROMPT_PROJECT_ROOT) {
    process.env.SUPER_PROMPT_PROJECT_ROOT = process.cwd();
  }

  // 간단한 버전 정보 출력 (임시)
  if (tool === 'sp.version') {
    console.log(safePkgVersion());
    return;
  }

  // If MCP client is explicitly disabled, run NOOP
  const explicitlyDisabled = process.env.MCP_CLIENT_DISABLED === 'true';
  if (explicitlyDisabled) {
    console.warn('-------- MCP memory: NOOP mode (enabled without persistence)');
    console.log('-------- Tool called:', tool);
    console.log('-------- Args:', JSON.stringify(kv, null, 2));
    process.exit(0);
    return;
  }

  // Enforce MCP-only execution unless explicitly whitelisted for bootstrap or development override
  const allowDirect = process.env.SUPER_PROMPT_ALLOW_DIRECT === 'true';
  const allowBootstrap = isBootstrapTool(tool);
  if (!allowDirect && !allowBootstrap) {
    console.error('-------- ERROR: Persona/tools must run via Cursor MCP integration');
    console.error('-------- Hint: Use Cursor command cards (run: mcp, server: super-prompt)');
    process.exit(3);
    return;
  }

  // Development override or bootstrap allowance: direct-call path via Python module
  await directCall(tool, kv);
  process.exit(0);
}

function safePkgVersion() {
  try {
    const p = path.join(__dirname, '..', 'package.json');
    return JSON.parse(fs.readFileSync(p, 'utf-8')).version || '0.0.0';
  } catch {
    return '0.0.0';
  }
}

run();

async function directInit() {
  const root = process.env.SUPER_PROMPT_PROJECT_ROOT || process.cwd();
  const tplRoot = path.join(__dirname, '..', 'templates');
  const appHome = path.join(__dirname, '..');

  // Display protection notice and ASCII art
  console.log('\x1b[31m\x1b[1m🚨 CRITICAL PROTECTION NOTICE:\x1b[0m');
  console.log('\x1b[33mPersonas and user commands MUST NEVER modify files in:\x1b[0m');
  console.log('\x1b[33m  - .cursor/ (Cursor IDE configuration)\x1b[0m');
  console.log('\x1b[33m  - .super-prompt/ (Super Prompt internal files)\x1b[0m');
  console.log('\x1b[33m  - .codex/ (Codex CLI configuration)\x1b[0m');
  console.log('\x1b[36mThis official installation process is authorized to create these directories.\x1b[0m');
  console.log('');

  // Display Super Prompt ASCII Art
  const currentVersion = safePkgVersion();
  const logo = `\x1b[36m\x1b[1m
   ███████╗██╗   ██╗██████╗ ███████╗██████╗
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝

   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝
\x1b[0m
\x1b[2m              Dual IDE Prompt Engineering Toolkit\x1b[0m
\x1b[2m                     v${currentVersion} | @cdw0424/super-prompt\x1b[0m
\x1b[2m                          Made by \x1b[0m\x1b[35mDaniel Choi from Korea\x1b[0m`;
  console.log(logo);
  console.log('');

  // Ensure .cursor exists
  const cursorDir = path.join(root, '.cursor');
  try { fs.mkdirSync(cursorDir, { recursive: true }); } catch {}

  // Write mcp.json and tools.json using templates (or sane defaults)
  const files = [
    { tpl: path.join(tplRoot, 'cursor', 'mcp.json'), dst: path.join(cursorDir, 'mcp.json') },
    { tpl: path.join(tplRoot, 'cursor', 'tools.json'), dst: path.join(cursorDir, 'tools.json') },
  ];
  for (const { tpl, dst } of files) {
    try {
      if (fs.existsSync(tpl)) {
        if (!fs.existsSync(dst)) {
          fs.copyFileSync(tpl, dst);
          console.log('-------- wrote:', path.relative(root, dst));
          // Post-process copied mcp.json to pin npm spec
          if (path.basename(dst) === 'mcp.json') {
            try {
              const json = JSON.parse(fs.readFileSync(dst, 'utf-8'));
              const entry = json?.mcpServers?.['super-prompt'];
              if (entry) {
                entry.type = 'stdio';
                entry.command = '${workspaceFolder}/bin/sp-mcp';
                entry.args = [];
                entry.env = {
                  ...(entry.env || {}),
                  SUPER_PROMPT_ALLOW_INIT: 'true',
                  SUPER_PROMPT_REQUIRE_MCP: '1',
                  SUPER_PROMPT_PROJECT_ROOT: '${workspaceFolder}',
                  PYTHONUNBUFFERED: '1',
                  PYTHONUTF8: '1',
                };
                delete entry.env.SUPER_PROMPT_NPM_SPEC;
                fs.writeFileSync(dst, JSON.stringify(json, null, 2));
                console.log('-------- normalized .cursor/mcp.json to local sp-mcp launcher');
              }
            } catch (e) {
              // best-effort
            }
          }
        }
      } else {
        // Fallback defaults
        if (!fs.existsSync(dst)) {
          const defaultContent = defaultCursorFile(path.basename(dst));
          fs.writeFileSync(dst, JSON.stringify(defaultContent, null, 2));
          console.log('-------- wrote:', path.relative(root, dst));
        }
      }
    } catch (e) {
      console.error('-------- init: failed to write', path.basename(dst), '-', (e && e.message) || e);
      throw e;
    }
  }
  // Try to generate full Cursor assets (commands/rules) via Python adapter
  try {
    await generateCursorAssets(root, appHome);
  } catch (e) {
    console.warn('-------- init: skipped generating commands/rules (', (e && e.message) || e, ')');
  }

  console.log('✅ Super Prompt initialized!');
  console.log(`   Project root: ${root}`);
  console.log(`   Version: ${safePkgVersion()}`);
  console.log('   Created directories:');
  console.log('     - .cursor/ (with MCP server configuration)');
  console.log('   Next steps:');
  console.log('   1. Restart Cursor IDE to load MCP server');
  console.log('   2. Use sp.init, sp.refresh, sp.list_commands tools');
  console.log('   3. Access Super Prompt via MCP integration');
}

async function directCall(toolName, argsObj) {
  const root = process.env.SUPER_PROMPT_PROJECT_ROOT || process.cwd();
  const appHome = path.join(__dirname, '..');

  const py = await resolvePython(root, appHome);
  const env = {
    ...process.env,
    MCP_SERVER_MODE: '1',
    SUPER_PROMPT_PROJECT_ROOT: root,
    SUPER_PROMPT_PACKAGE_ROOT: appHome,
    PYTHONPATH: `${appHome}/packages/core-py:${process.env.PYTHONPATH || ''}`,
    PYTHONUNBUFFERED: '1',
    PYTHONUTF8: '1',
    SP_DIRECT_TOOL: toolName,
    SP_DIRECT_ARGS_JSON: JSON.stringify(argsObj || {}),
  };

  await new Promise((resolve, reject) => {
    const proc = spawn(py, ['-m', 'super_prompt.mcp_server'], { env, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    proc.stdout.on('data', d => { out += d.toString(); });
    proc.stderr.on('data', d => { err += d.toString(); });
    proc.on('close', code => {
      if (err.trim()) process.stderr.write(err);
      if (code === 0) {
        if (out) process.stdout.write(out);
        resolve(undefined);
      } else {
        reject(new Error(`direct call failed (code ${code})`));
      }
    });
  });
}

async function resolvePython(projectRoot, appHome) {
  // Prefer project venv, then package venv, then system python3
  const candidates = [];
  const isWin = process.platform === 'win32';
  const join = (...p) => path.join(...p);
  if (isWin) {
    candidates.push(join(projectRoot, '.super-prompt', 'venv', 'Scripts', 'python.exe'));
    candidates.push(join(appHome, '.super-prompt', 'venv', 'Scripts', 'python.exe'));
  } else {
    candidates.push(join(projectRoot, '.super-prompt', 'venv', 'bin', 'python'));
    candidates.push(join(appHome, '.super-prompt', 'venv', 'bin', 'python'));
  }
  candidates.push(process.env.PYTHON || 'python3');

  for (const c of candidates) {
    try {
      if (c === 'python3' || c === process.env.PYTHON) {
        return c;
      }
      if (fs.existsSync(c)) return c;
    } catch {}
  }
  return 'python3';
}

function defaultCursorFile(name) {
  if (name === 'mcp.json') {
    return {
      mcpServers: {
        'super-prompt': {
          type: 'stdio',
          command: './bin/sp-mcp',
          args: [],
          env: {
            SUPER_PROMPT_ALLOW_INIT: 'true',
            SUPER_PROMPT_REQUIRE_MCP: '1',
            SUPER_PROMPT_PROJECT_ROOT: '${workspaceFolder}',
            PYTHONUNBUFFERED: '1',
            PYTHONUTF8: '1',
          },
        },
      },
    };
  }
  if (name === 'tools.json') {
    return {
      tools: {
        'super-prompt': {
          command: 'npx',
          args: ['-y', '@cdw0424/super-prompt@latest', 'super:init'],
          description: 'Initialize Super Prompt in the current project',
        },
      },
    };
  }
  return {};
}

async function generateCursorAssets(projectRoot, appHome) {
  const isWin = process.platform === 'win32';
  const join = (...p) => path.join(...p);
  const candidates = [];
  // Prefer project venv then package venv
  if (isWin) {
    candidates.push(join(projectRoot, '.super-prompt', 'venv', 'Scripts', 'python.exe'));
    candidates.push(join(appHome, '.super-prompt', 'venv', 'Scripts', 'python.exe'));
  } else {
    candidates.push(join(projectRoot, '.super-prompt', 'venv', 'bin', 'python'));
    candidates.push(join(appHome, '.super-prompt', 'venv', 'bin', 'python'));
  }
  candidates.push('python3');

  let py = null;
  for (const c of candidates) {
    try {
      if (c === 'python3') {
        py = c; break;
      }
      if (fs.existsSync(c)) { py = c; break; }
    } catch {}
  }
  if (!py) throw new Error('venv python not found');

  const code = `from pathlib import Path\nimport os\nfrom super_prompt.adapters.cursor_adapter import CursorAdapter\npr = Path(os.environ.get('PROJECT_ROOT') or '.')\nca = CursorAdapter()\nca.generate_commands(pr)\nca.generate_rules(pr)\nprint('OK')\n`;

  await new Promise((resolve, reject) => {
    const proc = spawn(py, ['-c', code], {
      env: {
        ...process.env,
        PROJECT_ROOT: projectRoot,
        SUPER_PROMPT_PACKAGE_ROOT: appHome,
        PYTHONPATH: `${appHome}/packages/core-py:${process.env.PYTHONPATH || ''}`,
        PYTHONUNBUFFERED: '1',
        PYTHONUTF8: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let out = '';
    let err = '';
    proc.stdout.on('data', d => { out += d.toString(); });
    proc.stderr.on('data', d => { err += d.toString(); });
    proc.on('close', code => {
      if (code === 0) {
        console.log('-------- cursor: commands/rules generated');
        resolve(undefined);
      } else {
        console.warn('-------- cursor: generator exit', code);
        if (err) console.warn(err.trim());
        reject(new Error('cursor assets generation failed'));
      }
    });
  });
}

function isBootstrapTool(toolName) {
  if (toolName === 'sp.init' && process.env.SUPER_PROMPT_ALLOW_INIT === 'true') return true;
  if (toolName === 'sp.refresh' && process.env.SUPER_PROMPT_ALLOW_REFRESH === 'true') return true;
  return false;
}
