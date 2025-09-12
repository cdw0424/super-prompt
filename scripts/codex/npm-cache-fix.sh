#!/bin/bash
# npm-cache-fix.sh - Fix infinite git loop caused by local npm cache
# Author: Super Prompt Toolkit
# Description: Detects and fixes npm cache misconfiguration that causes git analysis loops

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Get current npm cache location
get_npm_cache() {
    npm config get cache 2>/dev/null || echo ""
}

# Check if npm cache is local to project
is_cache_local() {
    local cache_path="$1"
    local cwd="$(pwd)"

    # Check if cache path starts with current directory
    if [[ "$cache_path" == ./* ]] || [[ "$cache_path" == .\\* ]] || [[ "$cache_path" == "$cwd"/* ]]; then
        return 0  # true
    fi
    return 1  # false
}

# Check if git is tracking npm cache files
are_cache_files_tracked() {
    if git ls-files 2>/dev/null | grep -q "^\.npm-cache/\|^node_modules/"; then
        return 0  # true
    fi
    return 1  # false
}

# Fix npm cache location
fix_npm_cache_location() {
    log_info "Setting npm cache to global location..."
    npm config set cache ~/.npm
    log_success "npm cache location updated to: $(npm config get cache)"
}

# Remove tracked cache files from git
remove_tracked_cache_files() {
    log_info "Removing tracked npm cache files from git index..."

    # Remove .npm-cache directory if tracked
    if git ls-files 2>/dev/null | grep -q "^\.npm-cache/"; then
        git rm -r --cached .npm-cache 2>/dev/null || true
        log_success "Removed .npm-cache from git tracking"
    fi

    # Remove node_modules if tracked (less common but possible)
    if git ls-files 2>/dev/null | grep -q "^node_modules/"; then
        git rm -r --cached node_modules 2>/dev/null || true
        log_success "Removed node_modules from git tracking"
    fi
}

# Ensure .gitignore has proper entries
ensure_gitignore() {
    local gitignore=".gitignore"

    if [[ ! -f "$gitignore" ]]; then
        log_info "Creating .gitignore file..."
        touch "$gitignore"
    fi

    # Check and add entries if missing
    if ! grep -q "^\.npm-cache/" "$gitignore" 2>/dev/null; then
        echo ".npm-cache/" >> "$gitignore"
        log_success "Added .npm-cache/ to .gitignore"
    fi

    if ! grep -q "^\.npm/" "$gitignore" 2>/dev/null; then
        echo ".npm/" >> "$gitignore"
        log_success "Added .npm/ to .gitignore"
    fi

    if ! grep -q "^node_modules/" "$gitignore" 2>/dev/null; then
        echo "node_modules/" >> "$gitignore"
        log_success "Added node_modules/ to .gitignore"
    fi
}

# Main diagnostic function
diagnose_issue() {
    echo
    echo "🔍 NPM Cache Git Loop Diagnostic"
    echo "=================================="

    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository. This script is for fixing npm cache issues in git repos."
        exit 1
    fi

    # Get npm cache location
    local cache_path="$(get_npm_cache)"
    log_info "Current npm cache location: $cache_path"

    # Check if cache is local
    local issues_found=0
    if is_cache_local "$cache_path"; then
        log_error "NPM CACHE IS LOCAL TO PROJECT"
        log_error "This causes git to track cache files, leading to infinite analysis loops."
        ((issues_found++))
    else
        log_success "npm cache location is properly global"
    fi

    # Check if cache files are tracked by git
    if are_cache_files_tracked; then
        log_error "CACHE FILES ARE TRACKED BY GIT"
        log_error "Git is tracking .npm-cache/ or node_modules/ files despite .gitignore"
        ((issues_found++))
    else
        log_success "No cache files are tracked by git"
    fi

    # Check .gitignore
    if [[ -f ".gitignore" ]]; then
        local missing_entries=()
        if ! grep -q "^\.npm-cache/" .gitignore 2>/dev/null; then
            missing_entries+=(".npm-cache/")
        fi
        if ! grep -q "^\.npm/" .gitignore 2>/dev/null; then
            missing_entries+=(".npm/")
        fi
        if ! grep -q "^node_modules/" .gitignore 2>/dev/null; then
            missing_entries+=(node_modules/)
        fi

        if [[ ${#missing_entries[@]} -gt 0 ]]; then
            log_warn ".gitignore is missing entries: ${missing_entries[*]}"
            ((issues_found++))
        else
            log_success ".gitignore has proper cache exclusions"
        fi
    else
        log_warn "No .gitignore file found"
        ((issues_found++))
    fi

    return $issues_found
}

# Main fix function
apply_fixes() {
    echo
    echo "🔧 Applying Fixes"
    echo "================="

    local fixes_applied=0

    # Fix npm cache location
    local cache_path="$(get_npm_cache)"
    if is_cache_local "$cache_path"; then
        fix_npm_cache_location
        ((fixes_applied++))
    fi

    # Remove tracked cache files
    if are_cache_files_tracked; then
        remove_tracked_cache_files
        ((fixes_applied++))
    fi

    # Ensure .gitignore is proper
    ensure_gitignore
    ((fixes_applied++))

    if [[ $fixes_applied -gt 0 ]]; then
        echo
        log_success "Fixes applied! You may want to:"
        echo "  1. Clear local npm cache: rm -rf .npm-cache/"
        echo "  2. Commit changes: git add .gitignore && git commit -m 'Fix npm cache git tracking issues'"
        echo "  3. Test npm install in another terminal"
    else
        log_info "No fixes were needed"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Fix npm cache misconfiguration that causes infinite git analysis loops."
    echo
    echo "OPTIONS:"
    echo "  --diagnose    Only diagnose issues (default)"
    echo "  --fix         Apply fixes automatically"
    echo "  --help        Show this help message"
    echo
    echo "EXAMPLES:"
    echo "  $0 --diagnose    # Check for issues"
    echo "  $0 --fix         # Diagnose and fix issues"
    echo
    echo "The issue occurs when:"
    echo "1. npm cache is configured locally (npm config set cache ./.npm-cache)"
    echo "2. Cache files get committed to git before .gitignore is updated"
    echo "3. npm install modifies cache files, triggering git analysis loops"
}

# Main script
main() {
    local action="diagnose"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --diagnose)
                action="diagnose"
                shift
                ;;
            --fix)
                action="fix"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    case $action in
        diagnose)
            diagnose_issue
            local issues=$?
            if [[ $issues -gt 0 ]]; then
                echo
                log_info "Issues found! Run '$0 --fix' to apply fixes."
                exit 1
            else
                echo
                log_success "No issues detected."
                exit 0
            fi
            ;;
        fix)
            diagnose_issue >/dev/null 2>&1
            local issues=$?
            if [[ $issues -gt 0 ]]; then
                apply_fixes
                echo
                log_success "Fixes completed. Re-run '$0 --diagnose' to verify."
            else
                log_info "No issues to fix."
            fi
            ;;
    esac
}

main "$@"
