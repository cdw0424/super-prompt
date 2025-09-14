// scripts/audit-all.mjs
// NPM 패키징 / CLI / 모드 토글 / MCP 메모리 래핑 여부 자동 점검
import fs from 'node:fs';
import path from 'node:path';
import {execSync, spawnSync} from 'node:child_process';

const log = (m) => console.log(`-------- ${m}`);
const error = (m) => console.error(`-------- [ERROR] ${m}`);

// 1) package.json 로드
const ROOT = process.cwd();
const pkgPath = path.join(ROOT, 'package.json');
if (!fs.existsSync(pkgPath)) {
  error('package.json 없음');
  process.exit(1);
}
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

// 2) NPM 배포 메타 점검
(function checkPackage() {
  log('NPM 메타 점검 시작');
  if (!pkg.name) error('name 누락');
  if (!pkg.version) error('version 누락');
  if (pkg.private === true) error('private:true → 퍼블릭 배포 불가');

  // bin 필드 검증
  if (!pkg.bin) {
    log('bin 필드 없음 → CLI 기능 확인 필요');
  } else {
    const entries = typeof pkg.bin === 'string' ? [pkg.bin] : Object.values(pkg.bin);
    for (const rel of entries) {
      const p = path.join(ROOT, rel);
      if (!fs.existsSync(p)) {
        error(`bin 파일 누락: ${rel}`);
      } else {
        const first = fs.readFileSync(p, 'utf8').split('\n')[0];
        if (!first.includes('#!/usr/bin/env')) {
          error(`bin shebang 누락 또는 잘못됨: ${rel}`);
        }
      }
    }
  }

  // files 필드 검증
  if (!pkg.files) {
    log('files 필드 없음 → npm pack에 포함될 파일이 많을 수 있음');
  } else {
    log(`files에 포함된 항목: ${pkg.files.join(', ')}`);
  }

  // prepack 스크립트 검증
  if (!pkg.scripts?.prepack) {
    log('prepack 스크립트 없음 → 배포 시 빌드 자동화 권장');
  } else {
    log(`prepack: ${pkg.scripts.prepack}`);
  }

  // publishConfig 검증
  if (!pkg.publishConfig?.access) {
    log('publishConfig.access 없음 → 퍼블릭 배포 시 access: public 필요');
  } else {
    log(`publish access: ${pkg.publishConfig.access}`);
  }

  log('NPM 메타 점검 완료');
})();

// 3) npm pack --dry-run
(function packDryRun() {
  try {
    const out = execSync('npm pack --dry-run', {cwd: ROOT, stdio: 'pipe'}).toString();
    log('npm pack --dry-run 결과:\n' + out);
  } catch (e) {
    error('npm pack 실패: ' + e.message);
  }
})();

// 4) CLI help/명령 노출 점검
function resolveBin() {
  if (typeof pkg.bin === 'string') return pkg.bin;
  if (typeof pkg.bin === 'object') {
    const first = Object.values(pkg.bin)[0];
    if (first) return first;
  }
  return null;
}

const binRel = resolveBin();
if (binRel) {
  const binAbs = path.join(ROOT, binRel);
  log(`CLI 실행 파일: ${binAbs}`);

  // --version 테스트
  const versionRes = spawnSync(binAbs, ['--version'], {encoding: 'utf8'});
  log(`--version exit=${versionRes.status}`);
  if (versionRes.stdout) log(`stdout: ${versionRes.stdout.trim()}`);
  if (versionRes.stderr) log(`stderr: ${versionRes.stderr.trim()}`);

  // super:init 테스트
  const initRes = spawnSync(binAbs, ['super:init'], {encoding: 'utf8'});
  log(`super:init exit=${initRes.status}`);
  if (initRes.stdout) log(`stdout: ${initRes.stdout.trim()}`);
  if (initRes.stderr) log(`stderr: ${initRes.stderr.trim()}`);

} else {
  log('CLI bin 추정 실패');
}

// 5) Python MCP 서버 구조 검증
(function checkPythonStructure() {
  const pythonPkg = path.join(ROOT, 'packages/core-py');
  if (!fs.existsSync(pythonPkg)) {
    error('Python 패키지 디렉토리 없음: packages/core-py');
    return;
  }

  const mcpServer = path.join(pythonPkg, 'super_prompt/mcp_server.py');
  if (!fs.existsSync(mcpServer)) {
    error('MCP 서버 파일 없음: packages/core-py/super_prompt/mcp_server.py');
  } else {
    log('MCP 서버 파일 존재');
  }

  const pyprojectToml = path.join(pythonPkg, 'pyproject.toml');
  if (!fs.existsSync(pyprojectToml)) {
    error('Python 프로젝트 설정 파일 없음: pyproject.toml');
  } else {
    log('pyproject.toml 존재');
  }
})();

// 6) Node.js MCP 클라이언트 검증
(function checkNodeClient() {
  const mcpClient = path.join(ROOT, 'src/mcp-client.js');
  if (!fs.existsSync(mcpClient)) {
    error('MCP 클라이언트 파일 없음: src/mcp-client.js');
  } else {
    log('MCP 클라이언트 파일 존재');
    const content = fs.readFileSync(mcpClient, 'utf8');
    if (content.includes('@modelcontextprotocol/sdk')) {
      log('MCP SDK 사용 확인');
    } else {
      log('MCP SDK 사용 여부 불확실');
    }
  }
})();

// 7) 페르소나/커맨드 구조 검증
(function checkAssets() {
  const cursorAssets = path.join(ROOT, 'packages/cursor-assets');
  const codexAssets = path.join(ROOT, 'packages/codex-assets');

  if (!fs.existsSync(cursorAssets)) {
    log('Cursor assets 디렉토리 없음');
  } else {
    log('Cursor assets 디렉토리 존재');
  }

  if (!fs.existsSync(codexAssets)) {
    log('Codex assets 디렉토리 없음');
  } else {
    log('Codex assets 디렉토리 존재');
  }

  // 페르소나 매니페스트 확인
  const personaManifest = path.join(ROOT, 'personas/manifest.yaml');
  if (!fs.existsSync(personaManifest)) {
    log('페르소나 매니페스트 없음: personas/manifest.yaml');
  } else {
    log('페르소나 매니페스트 존재');
  }
})();

// 8) 모드 토글 관련 환경변수/설정 검증
(function checkModeToggle() {
  const binAbs = path.join(ROOT, binRel);

  // 환경변수 기반 모드 테스트
  const testModes = [
    {env: {}, desc: '기본 모드', expectMode: 'gpt'},
    {env: {LLM_MODE: 'gpt'}, desc: 'GPT 모드', expectMode: 'gpt'},
    {env: {LLM_MODE: 'grok'}, desc: 'Grok 모드', expectMode: 'grok'},
    {env: {ENABLE_GPT: 'true'}, desc: 'ENABLE_GPT 플래그', expectMode: 'gpt'},
    {env: {ENABLE_GROK: 'true'}, desc: 'ENABLE_GROK 플래그', expectMode: 'grok'},
    {env: {ENABLE_GPT: 'true', ENABLE_GROK: 'true'}, desc: '동시 활성화 (충돌 테스트)', expectError: true}
  ];

  testModes.forEach(({env, desc, expectMode, expectError}) => {
    const res = spawnSync(binAbs, ['--version'], {
      encoding: 'utf8',
      env: {...process.env, ...env},
    });
    log(`${desc} 테스트: exit=${res.status}`);

    if (expectError && res.status === 0) {
      error(`  예상된 에러가 발생하지 않음`);
    } else if (!expectError && res.status !== 0) {
      error(`  예상치 못한 에러 발생`);
    } else if (expectMode && res.stderr && res.stderr.includes(`mode: resolved to ${expectMode}`)) {
      log(`  모드 확인: ${expectMode}`);
    }

    if (res.stderr && (res.stderr.includes('ERROR') || res.stderr.includes('error'))) {
      log(`  stderr: ${res.stderr.trim()}`);
    }
  });

  // CLI 플래그 테스트
  const cliFlagTests = [
    {args: ['--gpt', '--version'], desc: '--gpt 플래그', expectMode: 'gpt'},
    {args: ['--grok', '--version'], desc: '--grok 플래그', expectMode: 'grok'},
    {args: ['--mode=gpt', '--version'], desc: '--mode=gpt 플래그', expectMode: 'gpt'},
    {args: ['--mode=grok', '--version'], desc: '--mode=grok 플래그', expectMode: 'grok'}
  ];

  cliFlagTests.forEach(({args, desc, expectMode}) => {
    const res = spawnSync(binAbs, args, {
      encoding: 'utf8',
      env: process.env,
    });
    log(`${desc} 테스트: exit=${res.status}`);

    if (expectMode && res.stderr && res.stderr.includes(`mode: resolved to ${expectMode}`)) {
      log(`  모드 확인: ${expectMode}`);
    }

    if (res.stderr && (res.stderr.includes('ERROR') || res.stderr.includes('error'))) {
      log(`  stderr: ${res.stderr.trim()}`);
    }
  });
})();

// 9) 메모리/MCP 통합 검증 (휴리스틱)
(function checkMemoryIntegration() {
  const mcpServerPath = path.join(ROOT, 'packages/core-py/super_prompt/mcp_server.py');
  if (fs.existsSync(mcpServerPath)) {
    const content = fs.readFileSync(mcpServerPath, 'utf8');
    if (content.includes('memory') || content.includes('Memory')) {
      log('MCP 서버에 메모리 관련 코드 발견');
    } else {
      log('MCP 서버에 메모리 관련 코드 미발견');
    }

    if (content.includes('span') || content.includes('Span')) {
      log('MCP 서버에 span 관련 코드 발견');
    } else {
      log('MCP 서버에 span 관련 코드 미발견');
    }
  }

  // Node.js 클라이언트에서도 메모리 검증
  const mcpClientPath = path.join(ROOT, 'src/mcp-client.js');
  if (fs.existsSync(mcpClientPath)) {
    const content = fs.readFileSync(mcpClientPath, 'utf8');
    if (content.includes('memory') || content.includes('Memory')) {
      log('MCP 클라이언트에 메모리 관련 코드 발견');
    }
  }
})();

log('검수 스크립트 종료 - super-promt 프로젝트용');
