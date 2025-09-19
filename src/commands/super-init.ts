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
    console.log(`-------- copied: ${path.relative(process.cwd(), dst)}`);
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
        console.log('-------- Launching `openai login` (press Ctrl+C to skip)…');
        const login = spawnSync('openai', ['login'], { stdio: 'inherit' });
        if (login.status !== 0) {
          console.warn('-------- WARN: `openai login` did not complete. Run it manually to enable Codex tooling.');
        }
      } else {
        console.warn('-------- INFO: Run `openai login` in a terminal to enable Codex tooling.');
      }
    } else {
      console.log('-------- OpenAI CLI: authentication OK');
    }
  } catch (err) {
    console.warn('-------- WARN: Unable to verify OpenAI CLI authentication. Run `openai login` manually if Codex tooling fails.');
  }
}

function ensurePythonVenv(projectRoot: string) {
  const candidates = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  let pythonCmd: string | undefined;
  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ['--version'], { stdio: 'ignore' });
    if (probe.status === 0) {
      pythonCmd = candidate;
      break;
    }
  }

  if (!pythonCmd) {
    console.warn('-------- venv: no Python interpreter found (skipping project venv setup)');
    return;
  }

  const packageRoot = path.join(__dirname, '..', '..');
  const corePyPath = path.join(packageRoot, 'packages', 'core-py');
  const env = { ...process.env, SUPER_PROMPT_PROJECT_ROOT: projectRoot } as NodeJS.ProcessEnv;
  env.PYTHONPATH = env.PYTHONPATH
    ? `${corePyPath}${path.delimiter}${env.PYTHONPATH}`
    : corePyPath;

  const result = spawnSync(
    pythonCmd,
    ['-m', 'super_prompt.venv', '--project-root', projectRoot],
    { stdio: 'inherit', env }
  );

  if (result.status !== 0) {
    console.warn('-------- venv: setup command reported an error; continuing with system Python');
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
    console.log('-------- fixed: ~/.cursor/mcp.json (renamed super-prompt → super-prompt-global)');
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
  console.log('-------- Tool called: sp.init');

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
        console.log('-------- wrote: ~/.super-prompt/config.json');
      }
    }

    // 3) 프로젝트 루트에 Cursor/Codex 템플릿 배치(존재하면 건너뜀)
    const cwd = process.cwd();
    const cursorDir = path.join(cwd, '.cursor');
    ensureDir(cursorDir);
    const cursorTplDir = path.join(tplRoot, 'cursor');
    for (const name of ['mcp.json', 'tools.json']) {
      const src = path.join(cursorTplDir, name);
      const dst = path.join(cursorDir, name);
      if (fs.existsSync(src)) copyIfMissing(src, dst);
    }
    // Fallback: author a default .cursor/mcp.json if template missing
    const mcpCfg = path.join(cursorDir, 'mcp.json');
    if (!fs.existsSync(mcpCfg)) {
      // 절대 경로를 사용해서 안정적인 실행 보장
      const projectRoot = process.cwd();
      const mcpScriptPath = path.join(projectRoot, 'bin', 'sp-mcp');

      const cfg = {
        mcpServers: {
          'super-prompt': {
            type: 'stdio',
            command: 'node',
            args: [mcpScriptPath],
            env: {
              SUPER_PROMPT_ALLOW_INIT: 'true',
              SUPER_PROMPT_REQUIRE_MCP: '1',
              SUPER_PROMPT_PROJECT_ROOT: projectRoot,
              MCP_SERVER_MODE: '1',
              PYTHONUNBUFFERED: '1',
              PYTHONUTF8: '1',
              NODE_ENV: 'production'
            }
          }
        }
      } as any;
      fs.writeFileSync(mcpCfg, JSON.stringify(cfg, null, 2));
      console.log(`-------- wrote: ${path.relative(process.cwd(), mcpCfg)}`);
      console.log(`-------- MCP: configured to run from ${mcpScriptPath}`);
    }

    // 4) 페르소나 기본 템플릿(필요 시)
    const personasDst = path.join(cwd, 'personas');
    ensureDir(personasDst);
    const personasTplDir = path.join(tplRoot, 'personas');
    const defaultPersona = path.join(personasTplDir, 'default.json');
    if (fs.existsSync(defaultPersona)) {
      copyIfMissing(defaultPersona, path.join(personasDst, 'default.json'));
    }

    // Ensure project-specific Python virtual environment is ready
    ensurePythonVenv(cwd);

    // 5) 모드 토큰/모델 안내(검증은 선택: 토큰 없으면 경고만)
    // No external API keys are required for internal MCP tools.

    // 5-1) OpenAI CLI 로그인 상태 점검 (Codex 파이프라인 사용 시 필요)
    ensureOpenAICli();

    // 5-2) 전역 Cursor MCP 설정에 남아있는 깨진 super-prompt 엔트리를 안전한 npx 형식으로 교정
    ensureCursorGlobalMcp();

    // 6) MCP 서버 설정 검증 및 안내
    console.log('-------- MCP server: configured for stdio mode (auto-started by Cursor)');
    console.log('-------- Usage: Use /super-prompt/* commands in Cursor chat');
    console.log('-------- Note: MCP server runs on-demand via Cursor, not as daemon');

    // 7) 메모리 스팬 종료
    await memory.write(span, { type: 'init:done', ts: Date.now() });
    await memory.endSpan(span, 'ok');
    console.log('-------- MCP memory: healthcheck OK');
    console.log('-------- init: completed successfully');
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
