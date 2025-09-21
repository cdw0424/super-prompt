// src/commands/super-init.ts
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn, spawnSync } from 'node:child_process';
import { createMemoryClient } from '../mcp/memory';

function ensureDir(p: string) { if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }
function copyIfMissing(src: string, dst: string) {
  if (!fs.existsSync(dst)) {
    fs.copyFileSync(src, dst);
    console.error(`-------- copied: ${path.relative(process.cwd(), dst)}`);
  }
}

function ensureOpenAICli() {
  const isInteractive = process.stdin.isTTY && process.stdout.isTTY;

  try {
    const versionCheck = spawnSync('openai', ['--version'], { stdio: 'pipe', encoding: 'utf-8' });
    if (versionCheck.error || versionCheck.status !== 0) {
      console.warn('-------- WARN: OpenAI CLI not found. Install with `pip install --upgrade openai` to enable Codex features.');
      return;
    }
  } catch (err) {
    console.warn('-------- WARN: Failed to detect OpenAI CLI. Install with `pip install --upgrade openai` to enable Codex features.');
    return;
  }

  try {
    const authCheck = spawnSync('openai', ['api', 'keys.list'], { stdio: 'pipe', encoding: 'utf-8' });
    if (authCheck.status !== 0) {
      console.warn('-------- WARN: OpenAI CLI is not authenticated (`openai login`).');
      if (isInteractive) {
        console.error('-------- Launching `openai login` (press Ctrl+C to skip)…');
        const login = spawnSync('openai', ['login'], { stdio: 'inherit' });
        if (login.status !== 0) {
          console.warn('-------- WARN: `openai login` did not complete. Run it manually to enable Codex tooling.');
        }
      } else {
      }
    } else {
      console.error('-------- OpenAI CLI: authentication OK');
    }
  } catch (err) {
    console.warn('-------- WARN: Unable to verify OpenAI CLI authentication. Run `openai login` manually if Codex tooling fails.');
  }
}

function ensureCursorGlobalMcp() {
  try {
    const home = os.homedir();
    const globalDir = path.join(home, '.cursor');
    const cfgPath = path.join(globalDir, 'mcp.json');
    if (!fs.existsSync(cfgPath)) return;

    const raw = fs.readFileSync(cfgPath, 'utf-8') || '{}';
    const data = JSON.parse(raw);
    const servers = (data && data.mcpServers) || {};
    const globalEntry = servers['super-prompt'];
    if (!globalEntry || typeof globalEntry !== 'object') return;

    // 충돌 방지: 전역 super-prompt를 다른 이름으로 이동(중복 활성화를 막아 Cursor의 flapping 해소)
    servers['super-prompt-global'] = globalEntry;
    delete servers['super-prompt'];
    data.mcpServers = servers;
    fs.mkdirSync(globalDir, { recursive: true });
    fs.writeFileSync(cfgPath, JSON.stringify(data, null, 2));
    console.error('-------- fixed: ~/.cursor/mcp.json (renamed super-prompt → super-prompt-global)');
  } catch (e) {
    console.warn('-------- WARN: could not reconcile ~/.cursor/mcp.json:', (e as any)?.message || e);
  }
}

// MCP 아키텍처 설명:
// - MCP 서버는 stdio 모드로 Cursor IDE와 통신
// - Cursor가 필요할 때마다 서버 프로세스를 시작하고 stdin/stdout으로 JSON-RPC 통신
// - 서버는 HTTP 서버가 아니라, Cursor의 요청에 따라 실행되는 도구 모음
// - 따라서 "서버"라는 용어는 오해의 소지가 있음 - 실제로는 Cursor의 확장 도구

export async function run(_ctx?: any) {
  console.error('-------- Tool called: sp.init');

  // 1) MCP 메모리 헬스체크(활성/NOOP 모두 성공 종료)
  const memory = await createMemoryClient();
  const span = await memory.startSpan({ commandId: 'super:init' });
  await memory.write(span, { type: 'init:start', ts: Date.now() });

  try {
    // 2) 사용자 홈 설정
    const home = os.homedir();
    const appHome = path.join(home, '.super-prompt');
    ensureDir(appHome);
    const cfgDst = path.join(appHome, 'config.json');

    const tplRoot = path.join(__dirname, '..', '..', 'templates');
    const cfgTpl = path.join(tplRoot, 'config', 'super-prompt.config.json');
    if (fs.existsSync(cfgTpl)) {
      copyIfMissing(cfgTpl, cfgDst);
    } else {
      // 최소 기본 설정 생성
      if (!fs.existsSync(cfgDst)) {
        fs.writeFileSync(cfgDst, JSON.stringify({
          createdAt: new Date().toISOString(),
          mode: process.env.LLM_MODE || 'gpt'
        }, null, 2));
        console.error('-------- wrote: ~/.super-prompt/config.json');
      }
    }

    // 3) 프로젝트 루트에 Cursor/Codex 템플릿 배치(존재하면 건너뜀)
    const cwd = process.cwd();
    const cursorDir = path.join(cwd, '.cursor');
    console.error(`-------- DEBUG: cwd=${cwd}, cursorDir=${cursorDir}`);
    ensureDir(cursorDir);
    console.error(`-------- DEBUG: cursorDir exists=${fs.existsSync(cursorDir)}`);

    // 3-0) MCP 설정: 항상 올바른 로컬 경로로 설정
    const mcpCfg = path.join(cursorDir, 'mcp.json');
    const projectRoot = process.cwd();
    const mcpScriptPath = './bin/sp-mcp'; // 항상 상대 경로 사용
    const cfg = {
      mcpServers: {
        'super-prompt': {
          type: 'stdio',
          command: mcpScriptPath,
          args: [],
          env: {
            SUPER_PROMPT_ALLOW_INIT: 'true',
            SUPER_PROMPT_REQUIRE_MCP: '1',
            SUPER_PROMPT_PROJECT_ROOT: projectRoot,
            PYTHONUNBUFFERED: '1',
            PYTHONUTF8: '1',
          }
        }
      }
    } as any;
    fs.writeFileSync(mcpCfg, JSON.stringify(cfg, null, 2));
    console.error(`-------- wrote: ${path.relative(process.cwd(), mcpCfg)}`);
    console.error(`-------- MCP: configured to run from ${mcpScriptPath} (relative path)`);

    // 3-1) Copy command files from packages/cursor-assets/commands/super-prompt/
    try {
      // Try multiple possible paths for cursor-assets (development vs published package)
      let commandsTplDir = null;
      const possiblePaths = [
        // Development path
        path.join(tplRoot, '..', 'packages', 'cursor-assets', 'commands', 'super-prompt'),
        // Published package path (nested in core-py)
        path.join(tplRoot, '..', 'packages', 'core-py', 'packages', 'cursor-assets', 'commands', 'super-prompt'),
        // Alternative published path
        path.join(__dirname, '..', '..', 'packages', 'core-py', 'packages', 'cursor-assets', 'commands', 'super-prompt')
      ];

      for (const testPath of possiblePaths) {
        if (fs.existsSync(testPath)) {
          commandsTplDir = testPath;
          break;
        }
      }

      if (commandsTplDir) {
        const commandsDstDir = path.join(cursorDir, 'commands', 'super-prompt');
        ensureDir(commandsDstDir);

        for (const name of fs.readdirSync(commandsTplDir).filter(f => f.endsWith('.md'))) {
          const src = path.join(commandsTplDir, name);
          const dst = path.join(commandsDstDir, name);
          if (!fs.existsSync(dst)) {
            copyIfMissing(src, dst);
            console.error(`-------- copied command: ${path.relative(process.cwd(), dst)}`);
          }
        }
      } else {
        console.error('-------- warning: command templates not found in any expected location');
      }
    } catch (e) {
      console.error('-------- warning: command copy failed:', e.message);
    }

    // 3-2) Copy rule files from packages/cursor-assets/rules/
    try {
      // Try multiple possible paths for cursor-assets rules
      let rulesTplDir = null;
      const possibleRulePaths = [
        // Development path
        path.join(tplRoot, '..', 'packages', 'cursor-assets', 'rules'),
        // Published package path (nested in core-py)
        path.join(tplRoot, '..', 'packages', 'core-py', 'packages', 'cursor-assets', 'rules'),
        // Alternative published path
        path.join(__dirname, '..', '..', 'packages', 'core-py', 'packages', 'cursor-assets', 'rules')
      ];

      for (const testPath of possibleRulePaths) {
        if (fs.existsSync(testPath)) {
          rulesTplDir = testPath;
          break;
        }
      }

      if (rulesTplDir) {
        const rulesDstDir = path.join(cursorDir, 'rules');
        ensureDir(rulesDstDir);

        for (const name of fs.readdirSync(rulesTplDir).filter(f => f.endsWith('.mdc'))) {
          const src = path.join(rulesTplDir, name);
          const dst = path.join(rulesDstDir, name);
          if (!fs.existsSync(dst)) {
            copyIfMissing(src, dst);
            console.error(`-------- copied rule: ${path.relative(process.cwd(), dst)}`);
          }
        }
      } else {
        console.error('-------- warning: rule templates not found in any expected location');
      }
    } catch (e) {
      console.error('-------- warning: rule copy failed:', e.message);
    }

    // 3-3) legacy command folders cleanup and flatten
    try {
      const commandsDir = path.join(cursorDir, 'commands');
      const nested = path.join(commandsDir, 'super-prompt');
      const typo = path.join(commandsDir, 'super-promt'); // legacy misspelling
      if (fs.existsSync(typo)) {
        fs.rmSync(typo, { recursive: true, force: true });
        console.error('-------- cleaned: .cursor/commands/super-promt');
      }
      if (fs.existsSync(nested) && fs.statSync(nested).isDirectory()) {
        const entries = fs.readdirSync(nested).filter(f => f.endsWith('.md'));
        for (const name of entries) {
          const src = path.join(nested, name);
          const dst = path.join(commandsDir, name);
          if (!fs.existsSync(dst)) {
            fs.copyFileSync(src, dst);
          }
        }
        fs.rmSync(nested, { recursive: true, force: true });
        console.error('-------- normalized: moved super-prompt/* → .cursor/commands');
      }
    } catch (e) {
      console.warn('-------- WARN: command card normalization skipped:', (e as any)?.message || e);
    }

    // 4) SSOT: Do NOT seed extra persona configs (manifest is the only SSOT)

    // Project virtualenv bootstrap removed; rely on system Python instead

    // 5) 모드 토큰/모델 안내(검증은 선택: 토큰 없으면 경고만)
    // No external API keys are required for internal MCP tools.

    // 5-1) OpenAI CLI 로그인 상태 점검 (Codex 파이프라인 사용 시 필요)
    ensureOpenAICli();

    // 5-2) 전역 Cursor MCP 설정에 남아있는 깨진 super-prompt 엔트리를 안전한 npx 형식으로 교정
    ensureCursorGlobalMcp();

    // 6) MCP 서버 설정 검증 및 안내
    console.error('-------- MCP: stdio mode configured (auto-started by Cursor)');
    console.error('-------- Commands ready: /plan, /review, /dev, /doc-master …');

    // 7) 메모리 스팬 종료
    await memory.write(span, { type: 'init:done', ts: Date.now() });
    await memory.endSpan(span, 'ok');
    console.error('-------- init: completed successfully');
    process.exitCode = 0;
    return;
  } catch (err: any) {
    await memory.write(span, { type: 'error', message: String(err?.message || err) });
    await memory.endSpan(span, 'error', { stack: err?.stack });
    console.error('-------- init: failed', err?.message || err);
    process.exitCode = 1;
  } finally {
    if (typeof (memory as any).dispose === 'function') await (memory as any).dispose();
  }
}
