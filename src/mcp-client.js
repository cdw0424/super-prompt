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

  // MCP graceful fallback
  const explicitlyDisabled = process.env.MCP_CLIENT_DISABLED === 'true';
  if (explicitlyDisabled) {
    console.warn('-------- MCP memory: NOOP mode (enabled without persistence)');
    console.log('-------- Tool called:', tool);
    console.log('-------- Args:', JSON.stringify(kv, null, 2));
    // NOOP 모드에서도 성공으로 종료
    process.exit(0);
  } else {
    // 정상 MCP 클라이언트 생성 경로 (향후 구현)
    console.warn('-------- MCP client: full implementation pending');
    console.log('-------- Tool called:', tool);
    console.log('-------- Args:', JSON.stringify(kv, null, 2));
    process.exit(0);
  }
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
