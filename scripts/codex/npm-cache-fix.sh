#!/usr/bin/env zsh
set -euo pipefail

# Detect npm cache path and optionally relocate it to ~/.npm
fix=0
if [[ ${1-} == "--fix" ]]; then
  fix=1
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cache_path="$(npm config get cache 2>/dev/null | tr -d '\n')"

echo "--------npm-cache: current=${cache_path}"

if [[ -z "${cache_path}" ]]; then
  echo "--------npm-cache: unknown cache path"
  exit 0
fi

if [[ "${cache_path}" == ${repo_root}/* || "${cache_path}" == ./* ]]; then
  echo "--------npm-cache: cache is inside repo (churn risk)"
  if [[ ${fix} -eq 1 ]]; then
    echo "--------npm-cache: setting global cache to ~/.npm"
    npm config set cache ~/.npm --global
    echo "--------npm-cache: adding .npm-cache/ to .gitignore"
    if [[ -f "${repo_root}/.gitignore" ]]; then
      if ! grep -q '^\.npm-cache/' "${repo_root}/.gitignore"; then
        echo ".npm-cache/" >> "${repo_root}/.gitignore"
      fi
    else
      echo ".npm-cache/" > "${repo_root}/.gitignore"
    fi
    echo "--------npm-cache: removing cached .npm-cache from index if present"
    (cd "${repo_root}" && git rm -r --cached .npm-cache 2>/dev/null || true)
    echo "--------npm-cache: done"
  else
    echo "--------npm-cache: pass --fix to relocate and ignore"
  fi
else
  echo "--------npm-cache: cache is outside repo (OK)"
fi
