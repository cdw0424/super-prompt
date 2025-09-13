# Project Cleanup Plan - v2 → v3 Transition

## 🎯 Cleanup Strategy

### Phase 1: Remove Redundant Files (Safe)
- ✅ Old package archive: `cdw0424-super-prompt-2.9.26.tgz`
- ✅ macOS system files: `.DS_Store`
- ✅ Duplicate processor files in `.cursor/commands/super-prompt/` (43 files)
- ✅ Redundant utils in `.super-prompt/utils/` (15 files)

### Phase 2: Consolidate Legacy Code (Medium Risk)
- 📦 Monolithic CLI: `.super-prompt/cli.py` (1441 lines) → Extract to v3 modules
- 🔄 Duplicate processor patterns → Migrate to YAML manifests
- 📁 Scattered JS files in `src/` → Consolidate or remove

### Phase 3: Structure Optimization (Low Risk)
- 🗂️ Move legacy files to `/legacy/` directory
- 📋 Update documentation references
- 🧪 Preserve existing tests during transition

## 📊 Cleanup Assessment

### Files to Remove (12 files, ~144KB)
```
./cdw0424-super-prompt-2.9.26.tgz           (~143KB)
./.DS_Store                                  (~6KB)
.cursor/commands/super-prompt/*.py           (43 files - duplicates)
.super-prompt/utils/*                        (15 files - redundant)
```

### Files to Migrate (8 files, ~1.5MB)
```
.super-prompt/cli.py                         (1441 lines → v3 modules)
src/amr/router.js                           → packages/core-py/engine/
src/state-machine/index.js                 → packages/core-py/engine/
templates/*.py                              → packages/assets/
```

### Files to Preserve
```
bin/super-prompt                            (entry point)
install.js                                  (installation)
package.json                                (npm config)
README.md                                   (documentation)
```

## 🚨 Safety Measures
- Create backup before cleanup
- Preserve original structure in `/legacy/`
- Maintain working entry points during transition
- Test basic functionality after each phase