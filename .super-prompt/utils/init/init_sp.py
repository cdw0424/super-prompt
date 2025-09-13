#!/usr/bin/env python3
"""
Project Initializer for Super Prompt Memory (MCI)
- Scans the current project, summarizes structure and tech stack
- Stores summary into MCI (JSON) via MemoryController (fallback available)
- Optionally refreshes (re-init) to update snapshot
"""
from __future__ import annotations
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from reasoning_delegate import ReasoningDelegate  # type: ignore

# Memory controller with safe fallback
try:
    repo_root = Path(__file__).resolve().parents[3]
    core_py = repo_root / 'packages' / 'core-py'
    if str(core_py) not in sys.path:
        sys.path.append(str(core_py))
    from super_prompt.memory.controller import MemoryController  # type: ignore
except Exception:
    from fallback_memory import MemoryController  # type: ignore


IGNORE_DIRS = {
    '.git', 'node_modules', '.venv', '.env', '__pycache__', 'dist', 'build', '.next', '.cache'
}

EXT_LANG = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'typescript', '.jsx': 'javascript',
    '.json': 'json', '.md': 'markdown', '.sh': 'shell', '.yml': 'yaml', '.yaml': 'yaml',
}


def walk_project(root: Path, max_files: int = 5000) -> Tuple[List[Path], List[Path]]:
    files: List[Path] = []
    dirs: List[Path] = []
    for dp, dn, fn in os.walk(root):
        rel = Path(dp).relative_to(root)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        dirs.append(Path(dp))
        for name in fn:
            p = Path(dp) / name
            files.append(p)
            if len(files) >= max_files:
                return dirs, files
    return dirs, files


def summarize(root: Path) -> Dict[str, Any]:
    dirs, files = walk_project(root)
    lang_counts: Dict[str, int] = {}
    for f in files:
        ext = f.suffix.lower()
        lang = EXT_LANG.get(ext)
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    pkg_json = None
    pkg_path = root / 'package.json'
    if pkg_path.exists():
        try:
            pkg_json = json.loads(pkg_path.read_text(encoding='utf-8'))
        except Exception:
            pkg_json = None

    deps = list((pkg_json or {}).get('dependencies', {}).keys()) if pkg_json else []
    dev_deps = list((pkg_json or {}).get('devDependencies', {}).keys()) if pkg_json else []

    try:
        import subprocess
        git_head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=str(root), capture_output=True, text=True)
        head = git_head.stdout.strip() if git_head.returncode == 0 else ''
    except Exception:
        head = ''

    summary = {
        'root': str(root),
        'dirs': len(dirs),
        'files': len(files),
        'top_langs': sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        'has_package_json': bool(pkg_json),
        'dependencies': deps[:20],
        'devDependencies': dev_deps[:20],
        'git_head': head,
        'timestamp': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime()),
    }
    return summary


def summarize_text(s: Dict[str, Any]) -> str:
    lines = []
    lines.append("Project Analysis Summary")
    lines.append(f"Root: {s['root']}")
    lines.append(f"Files: {s['files']} | Dirs: {s['dirs']}")
    if s['top_langs']:
        langs = ', '.join(f"{k}:{v}" for k, v in s['top_langs'])
        lines.append(f"Top languages: {langs}")
    if s['has_package_json']:
        if s['dependencies']:
            lines.append("Dependencies: " + ', '.join(s['dependencies']))
        if s['devDependencies']:
            lines.append("DevDeps: " + ', '.join(s['devDependencies']))
    if s['git_head']:
        lines.append(f"Git HEAD: {s['git_head']}")
    lines.append(f"Timestamp: {s['timestamp']}")
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description="Initialize/refresh Super Prompt memory with project analysis")
    ap.add_argument('--mode', choices=['init', 'reinit'], default='init')
    ap.add_argument('--project-root', default='.')
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    mem = MemoryController(root)

    # Analyze project
    s = summarize(root)
    text = summarize_text(s)

    # Store in MCI
    tag = '/init-sp' if args.mode == 'init' else '/re-init-sp'
    mem.append_interaction(f"{tag}", text)

    # Optional: enrich memory via Codex JSON extraction
    try:
        rd = ReasoningDelegate()
        prompt = f"""
You are GPT-5 Project Extractor. Think internally. Output JSON only.
Extract concise entities and key facts from this project summary.

SUMMARY:\n{text}

SCHEMA:
{{
  "entities": {{"<name>": {{"type": "library|framework|service|tool|lang|other", "notes": "..."}}}},
  "key_memories": ["short fact", "…"],
  "notes": ["optional"]
}}
Return only JSON.
"""
        res = rd.request_plan(prompt, timeout=120)
        if res.get('ok') and res.get('plan'):
            mem.update_from_extraction(res['plan'])
            print("-------- Memory enriched from project extraction")
    except Exception as e:
        print(f"-------- Extraction skipped: {e}")

    print("-------- Project analysis stored in Super Prompt memory")

if __name__ == '__main__':
    main()
