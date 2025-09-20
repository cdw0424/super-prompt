# packages/core-py/super_prompt/analysis/project_analyzer.py
"""
프로젝트 분석 관련 기능
"""

import json
import time
from pathlib import Path
from typing import Dict, Any


def analyze_and_store_project_data(project_root: Path) -> None:
    """Perform comprehensive project analysis and store results in database"""
    from ..memory.store import MemoryStore

    try:
        # Initialize memory store
        store = MemoryStore.open(project_root)

        # 1. 프로젝트 구조 분석
        project_structure = analyze_project_structure(project_root)
        store.set_kv("project_structure", project_structure)

        # 2. 의존성 분석
        dependencies = analyze_dependencies(project_root)
        store.set_kv("project_dependencies", dependencies)

        # 3. 코드베이스 통계
        codebase_stats = analyze_codebase_stats(project_root)
        store.set_kv("codebase_statistics", codebase_stats)

        # 4. 설정 파일 분석
        config_files = analyze_config_files(project_root)
        store.set_kv("project_config", config_files)

        # 5. 프로젝트 메타데이터
        metadata = collect_project_metadata(project_root)
        store.set_kv("project_metadata", metadata)

        print("-------- project analysis: stored comprehensive data in memory", file=sys.stderr, flush=True)

    except Exception as e:
        print(f"-------- project analysis: error during analysis: {e}", file=sys.stderr, flush=True)
        raise


def analyze_project_structure(project_root: Path) -> dict:
    """Analyze project directory structure"""
    structure = {
        "root_path": str(project_root),
        "directories": [],
        "files": [],
        "file_types": {},
        "total_files": 0,
        "total_dirs": 0
    }

    try:
        for path in project_root.rglob("*"):
            if path.is_file():
                structure["files"].append(str(path.relative_to(project_root)))
                structure["total_files"] += 1

                # 파일 타입별 카운트
                ext = path.suffix.lower()
                if ext:
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1

            elif path.is_dir() and not path.name.startswith('.'):
                structure["directories"].append(str(path.relative_to(project_root)))
                structure["total_dirs"] += 1

    except Exception as e:
        structure["error"] = f"Structure analysis failed: {e}"

    return structure


def analyze_dependencies(project_root: Path) -> dict:
    """Analyze project dependencies"""
    deps = {
        "python": [],
        "node": [],
        "other": []
    }

    try:
        # Python dependencies
        req_files = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
        for req_file in req_files:
            req_path = project_root / req_file
            if req_path.exists():
                deps["python"].append({
                    "file": req_file,
                    "exists": True,
                    "size": req_path.stat().st_size
                })

        # Node.js dependencies
        package_path = project_root / "package.json"
        if package_path.exists():
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                deps["node"] = {
                    "name": package_data.get("name", "unknown"),
                    "version": package_data.get("version", "unknown"),
                    "dependencies_count": len(package_data.get("dependencies", {})),
                    "dev_dependencies_count": len(package_data.get("devDependencies", {}))
                }
            except Exception:
                deps["node"] = {"error": "Failed to parse package.json"}

    except Exception as e:
        deps["error"] = f"Dependency analysis failed: {e}"

    return deps


def analyze_codebase_stats(project_root: Path) -> dict:
    """Analyze codebase statistics"""
    stats = {
        "total_lines": 0,
        "total_files": 0,
        "languages": {},
        "largest_files": [],
        "oldest_files": [],
        "newest_files": []
    }

    try:
        file_stats = []

        for path in project_root.rglob("*"):
            if path.is_file() and not path.name.startswith('.') and path.suffix not in ['.pyc', '.pyo', '__pycache__']:
                try:
                    # 파일 크기 및 수정 시간
                    stat = path.stat()
                    size = stat.st_size
                    mtime = stat.st_mtime

                    # 라인 수 계산 (텍스트 파일만)
                    lines = 0
                    if path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.md', '.txt', '.json', '.yaml', '.yml']:
                        try:
                            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = sum(1 for _ in f)
                        except:
                            pass

                    file_info = {
                        "path": str(path.relative_to(project_root)),
                        "size": size,
                        "lines": lines,
                        "mtime": mtime,
                        "extension": path.suffix
                    }

                    file_stats.append(file_info)
                    stats["total_lines"] += lines
                    stats["total_files"] += 1

                    # 언어 통계
                    lang = path.suffix.lstrip('.')
                    if lang:
                        stats["languages"][lang] = stats["languages"].get(lang, 0) + 1

                except Exception:
                    continue

        # 상위 파일들 추출
        if file_stats:
            # 크기별 정렬
            by_size = sorted(file_stats, key=lambda x: x["size"], reverse=True)
            stats["largest_files"] = by_size[:5]

            # 수정 시간별 정렬
            by_mtime = sorted(file_stats, key=lambda x: x["mtime"], reverse=True)
            stats["newest_files"] = by_mtime[:5]
            stats["oldest_files"] = by_mtime[-5:]

    except Exception as e:
        stats["error"] = f"Codebase stats analysis failed: {e}"

    return stats


def analyze_config_files(project_root: Path) -> dict:
    """Analyze configuration files"""
    config = {
        "git": {},
        "docker": {},
        "ci_cd": [],
        "editors": {},
        "other": []
    }

    try:
        # Git 설정
        gitignore = project_root / ".gitignore"
        if gitignore.exists():
            config["git"]["has_gitignore"] = True
            with open(gitignore, 'r', encoding='utf-8', errors='ignore') as f:
                config["git"]["gitignore_lines"] = len(f.readlines())

        # Docker 파일들
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        for docker_file in docker_files:
            if (project_root / docker_file).exists():
                config["docker"][docker_file] = True

        # CI/CD 파일들
        ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml"]
        for ci_file in ci_files:
            if (project_root / ci_file).exists():
                config["ci_cd"].append(ci_file)

        # 에디터 설정
        editor_configs = [".vscode", ".idea", ".cursor"]
        for editor in editor_configs:
            if (project_root / editor).exists():
                config["editors"][editor] = True

    except Exception as e:
        config["error"] = f"Config analysis failed: {e}"

    return config


def collect_project_metadata(project_root: Path) -> dict:
    """Collect project metadata"""
    metadata = {
        "name": "unknown",
        "type": "unknown",
        "frameworks": [],
        "languages": [],
        "analysis_timestamp": time.time()
    }

    try:
        # 프로젝트 타입 감지
        if (project_root / "package.json").exists():
            metadata["type"] = "node"
            metadata["languages"].append("javascript")

        if any(project_root.glob("*.py")) or (project_root / "requirements.txt").exists():
            metadata["type"] = "python" if metadata["type"] == "unknown" else metadata["type"]
            metadata["languages"].append("python")

        if any(project_root.glob("*.java")):
            metadata["languages"].append("java")

        if any(project_root.glob("*.cpp")) or any(project_root.glob("*.c")):
            metadata["languages"].append("c/c++")

        # 프로젝트 이름 추출
        if metadata["type"] == "node":
            try:
                with open(project_root / "package.json", 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                    metadata["name"] = pkg.get("name", "unknown")
            except:
                pass

        elif metadata["type"] == "python":
            # setup.py나 pyproject.toml에서 이름 추출
            setup_files = ["setup.py", "pyproject.toml"]
            for setup_file in setup_files:
                if (project_root / setup_file).exists():
                    metadata["name"] = setup_file
                    break

    except Exception as e:
        metadata["error"] = f"Metadata collection failed: {e}"

    return metadata


def analyze_project_context(project_dir: Path, query: str) -> Dict[str, Any]:
    """Return minimal metadata for persona pipelines."""
    info: Dict[str, Any] = {"patterns": [], "query_relevance": []}
    try:
        root = Path(project_dir)
        if (root / ".cursor" / "mcp.json").exists():
            info["query_relevance"].append("cursor-mcp-config")
        if (root / "bin" / "sp-mcp").exists():
            info["query_relevance"].append("local-sp-mcp")
        lowered = (query or "").lower()
        for needle, tag in (
            ("mcp", "mcp"),
            ("cursor", "cursor"),
            ("tool", "tooling"),
            ("permission", "permissions"),
        ):
            if needle in lowered:
                info["patterns"].append(tag)
    except Exception:
        pass
    return info
