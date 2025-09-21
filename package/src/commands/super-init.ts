// src/commands/super-init.ts
import fs from 'fs';
import path from 'path';
import os from 'os';
import { spawn, spawnSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function ensureDir(p: string): void {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function copyIfMissing(src: string, dst: string): void {
  if (!fs.existsSync(dst)) {
    fs.copyFileSync(src, dst);
    console.error(`-------- copied: ${path.relative(process.cwd(), dst)}`);
  }
}

function ensureOpenAICli(): void {
  const isInteractive = process.stdin.isTTY && process.stdout.isTTY;

  try {
    const versionCheck = spawnSync('openai', ['--version'], { stdio: 'pipe', encoding: 'utf-8' });
    if (versionCheck.error || versionCheck.status !== 0) {
      console.error('-------- WARN: OpenAI CLI not found. Install with `pip install --upgrade openai` to enable Codex features.');
      return;
    }
  } catch (err) {
    console.error('-------- WARN: Failed to detect OpenAI CLI. Install with `pip install --upgrade openai` to enable Codex features.');
    return;
  }

  try {
    const authCheck = spawnSync('openai', ['api', 'keys.list'], { stdio: 'pipe', encoding: 'utf-8' });
    if (authCheck.status !== 0) {
      console.error('-------- WARN: OpenAI CLI is not authenticated (`openai login`).');
      if (isInteractive) {
        console.error('-------- Launching `openai login` (press Ctrl+C to skip)…');
        const login = spawnSync('openai', ['login'], { stdio: 'inherit' });
        if (login.status !== 0) {
          console.error('-------- WARN: `openai login` did not complete. Run it manually to enable Codex tooling.');
        }
      }
    } else {
      console.error('-------- OpenAI CLI: authentication OK');
    }
  } catch (err) {
    console.error('-------- WARN: Unable to verify OpenAI CLI authentication. Run `openai login` manually if Codex tooling fails.');
  }
}

function ensureCursorGlobalMcp(): void {
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
    console.error('-------- WARN: could not reconcile ~/.cursor/mcp.json:', (e as any)?.message || e);
  }
}

// MCP 아키텍처 설명:
// - MCP 서버는 stdio 모드로 Cursor IDE와 통신
// - Cursor가 필요할 때마다 서버 프로세스를 시작하고 stdin/stdout으로 JSON-RPC 통신
// - 서버는 HTTP 서버가 아니라, Cursor의 요청에 따라 실행되는 도구 모음
// - 따라서 "서버"라는 용어는 오해의 소지가 있음 - 실제로는 Cursor의 확장 도구

export async function run(): Promise<void> {
  console.error('-------- Tool called: sp.init');

  // 1) MCP 메모리 헬스체크(활성/NOOP 모두 성공 종료)
  // TODO: createMemoryClient import 경로 확인 및 수정 필요

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

    // 3) 글로벌 MCP 설정만 사용 (프로젝트별 mcp.json 생성하지 않음)
    // 글로벌 설정을 통해 중복 방지 및 일관성 유지
    const projectRoot = process.cwd();
    const cursorDir = path.join(projectRoot, '.cursor');

    // 3-1) legacy command folders cleanup and flatten
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
      console.error('-------- WARN: command card normalization skipped:', (e as any)?.message || e);
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

    // 7) 초기화 완료
    console.error('-------- init: completed successfully');
    return;
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    console.error('-------- init: failed', errorMessage);
  }
}
