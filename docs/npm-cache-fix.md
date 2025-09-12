# NPM Cache Git Loop Fix

## Problem

When npm cache is configured to be stored locally within a git repository (e.g., `.npm-cache/`), it can cause infinite git analysis loops during `npm install`. This happens because:

1. npm modifies cache files during package installation
2. Git detects these changes and tries to analyze them with `git ls-tree`, `git diff`, `git show --textconv`
3. The constant file modifications create an endless cycle of git analysis

## Symptoms

- Infinite git commands appearing during npm install:
  ```
  git ls-tree -l -r <commit> -- .npm-cache/_cacache/...
  git diff <commit> -- .npm-cache/_cacache/...
  git show --textconv <commit>:.npm-cache/_cacache/...
  ```
- IDE/git watchers getting stuck analyzing cache files
- Slow or hanging npm installations

## Root Cause

The issue occurs when:
1. `npm config get cache` returns a local path (e.g., `./.npm-cache`)
2. Cache files were committed to git before `.gitignore` was updated
3. Git continues tracking these files despite `.gitignore` entries

## Solution

Use the diagnostic and fix script:

```bash
# Diagnose the issue
./scripts/codex/npm-cache-fix.sh --diagnose

# Apply automatic fixes
./scripts/codex/npm-cache-fix.sh --fix
```

### Manual Fix Steps

1. **Change npm cache location:**
   ```bash
   npm config set cache ~/.npm
   ```

2. **Remove tracked cache files from git:**
   ```bash
   git rm -r --cached .npm-cache/ 2>/dev/null || true
   git rm -r --cached .npm/ 2>/dev/null || true
   git rm -r --cached node_modules/ 2>/dev/null || true
   ```

3. **Ensure .gitignore excludes cache directories:**
   ```bash
   echo ".npm-cache/" >> .gitignore
   echo ".npm/" >> .gitignore
   echo "node_modules/" >> .gitignore
   ```

4. **Clean up local cache (optional):**
   ```bash
   rm -rf .npm-cache/
   ```

5. **Commit the changes:**
   ```bash
   git add .gitignore
   git commit -m "Fix npm cache git tracking issues"
   ```

## Prevention

- Always configure npm cache globally: `npm config set cache ~/.npm`
- Never commit cache directories to git
- Keep `.npm`, `.npm-cache`, and `node_modules` in `.gitignore`

## Related Files

- `scripts/codex/npm-cache-fix.sh` - Diagnostic and fix script
- `install.js` - Installation script with proactive warnings
