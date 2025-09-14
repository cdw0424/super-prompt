// src/commands/super-init.ts
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createMemoryClient } from '../mcp/memory';

function ensureDir(p: string) { if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }
function copyIfMissing(src: string, dst: string) {
  if (!fs.existsSync(dst)) {
    fs.copyFileSync(src, dst);
    console.log(`-------- copied: ${path.relative(process.cwd(), dst)}`);
  }
}

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
      const cfg = {
        mcpServers: {
          'super-prompt': {
            command: 'npx',
            args: ['-y', '@cdw0424/super-prompt@latest', 'sp-mcp'],
            env: {
              SUPER_PROMPT_ALLOW_INIT: 'true',
              SUPER_PROMPT_PROJECT_ROOT: '${workspaceFolder}'
            }
          }
        }
      } as any;
      fs.writeFileSync(mcpCfg, JSON.stringify(cfg, null, 2));
      console.log(`-------- wrote: ${path.relative(process.cwd(), mcpCfg)}`);
    }

    // 4) 페르소나 기본 템플릿(필요 시)
    const personasDst = path.join(cwd, 'personas');
    ensureDir(personasDst);
    const personasTplDir = path.join(tplRoot, 'personas');
    const defaultPersona = path.join(personasTplDir, 'default.json');
    if (fs.existsSync(defaultPersona)) {
      copyIfMissing(defaultPersona, path.join(personasDst, 'default.json'));
    }

    // 5) 모드 토큰/모델 안내(검증은 선택: 토큰 없으면 경고만)
    // No external API keys are required for internal MCP tools.

    // 6) 메모리 스팬 종료
    await memory.write(span, { type: 'init:done', ts: Date.now() });
    await memory.endSpan(span, 'ok');
    console.log('-------- MCP memory: healthcheck OK');
    console.log('-------- init: completed');
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
