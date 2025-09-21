#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, spawn } = require('child_process');
const pkg = require('./package.json');

// Handle npm cache permission issues proactively
function ensureNpmCachePermissions() {
  try {
    const cacheDir = process.env.NPM_CONFIG_CACHE || '/tmp/.npm-cache';

    // Create cache directory if it doesn't exist
    if (!fs.existsSync(cacheDir)) {
      fs.mkdirSync(cacheDir, { recursive: true, mode: 0o755 });
      console.error(`✅ Created npm cache directory: ${cacheDir}`);
    }

    // Fix permissions on cache directory
    try {
      execSync(`chmod -R 755 "${cacheDir}"`, { stdio: 'ignore' });
      console.error('✅ Fixed npm cache permissions');
    } catch (permError) {
      console.error('⚠️  Cache permission fix skipped (non-critical)');
    }
  } catch (error) {
    console.error('⚠️  Cache setup skipped:', error.message);
  }
}

// Run cache permission fix first
ensureNpmCachePermissions();

// ASCII Art and styled installation
const colors = {
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    red: '\x1b[31m',
    magenta: '\x1b[35m',
    blue: '\x1b[34m',
    bold: '\x1b[1m',
    dim: '\x1b[2m',
    reset: '\x1b[0m'
};

const logo = `
${colors.cyan}${colors.bold}
   ███████╗██╗   ██╗██████╗ ███████╗██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗
   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝
   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗
   ███████║╚██████╔╝██║     ███████╗██║  ██║
   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝
   
   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║   
   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║   
   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║   
   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝   
${colors.reset}
${colors.dim}              Dual IDE Prompt Engineering Toolkit${colors.reset}
${colors.dim}                     v${pkg.version} | @cdw0424/super-prompt${colors.reset}
${colors.dim}                          Made by ${colors.reset}${colors.magenta}Daniel Choi${colors.reset}
`;

console.error(logo);

// Progress animation
let dots = 0;
const progressChars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
let progressIndex = 0;

function showProgress(message) {
    process.stderr.write(`${colors.cyan}${progressChars[progressIndex]} ${message}${colors.reset}\r`);
    progressIndex = (progressIndex + 1) % progressChars.length;
}

function completedStep(step, message) {
    console.error(`${colors.green}✓${colors.reset} ${colors.bold}Step ${step}:${colors.reset} ${message}`);
}

// Start installation
console.error(`${colors.yellow}${colors.bold}🚀 Starting installation...${colors.reset}\n`);

// Check platform
const platform = os.platform();
console.error(`${colors.cyan}⚙️  Checking platform compatibility...${colors.reset}`);

if (platform !== 'darwin' && platform !== 'linux' && platform !== 'win32') {
    console.error(`${colors.red}❌ Unsupported platform: ${platform}${colors.reset}`);
    process.exit(1);
}

completedStep(1, `Platform check passed (${platform})`);

function ensureDir(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function isGlobalInstall() {
    // Common signals for global install
    if (String(process.env.npm_config_global || '').toLowerCase() === 'true') return true;
    const dir = __dirname.replace(/\\/g, '/');
    return /(^|\/)lib\/node_modules\//.test(dir);
}

function findProjectRoot() {
    // Prefer INIT_CWD which points to the original cwd for the install
    const initCwd = process.env.INIT_CWD;
    if (initCwd) {
        try {
            const pj = path.join(initCwd, 'package.json');
            if (fs.existsSync(pj)) {
                const p = JSON.parse(fs.readFileSync(pj, 'utf8'));
                if (p && p.name !== '@cdw0424/super-prompt') return initCwd;
            }
        } catch (_) {}
    }

    // If we're in node_modules, walk up until just above node_modules
    const parts = __dirname.split(path.sep);
    const nmIndex = parts.lastIndexOf('node_modules');
    if (nmIndex !== -1) {
        // Parent of node_modules is the project root for local installs
        return parts.slice(0, nmIndex).join(path.sep) || path.sep;
    }

    // npm user dir (fallback)
    if (process.env.npm_config_user_dir) {
        return process.env.npm_config_user_dir;
    }

    // PWD fallback
    if (process.env.PWD && process.env.PWD !== process.cwd()) {
        return process.env.PWD;
    }

    // Walk up from cwd and choose first package.json that isn't ours
    let projectRoot = process.cwd();
    let currentDir = projectRoot;
    while (currentDir !== path.dirname(currentDir)) {
        const pj = path.join(currentDir, 'package.json');
        if (fs.existsSync(pj)) {
            try {
                const p = JSON.parse(fs.readFileSync(pj, 'utf8'));
                if (p.name !== '@cdw0424/super-prompt') {
                    projectRoot = currentDir;
                    break;
                }
            } catch (_) {}
        }
        currentDir = path.dirname(currentDir);
    }
    return projectRoot;
}

function copyFile(src, dest, description) {
    try {
        fs.copyFileSync(src, dest);
        fs.chmodSync(dest, '755');
        console.error(`   ${colors.dim}→ ${description}${colorsreset}`);
    } catch (error) {
        console.error(`${colors.red}❌ Failed to copy ${src}: ${error.message}${colors.reset}`);
        throw error;
    }
}

function copyDirectory(src, dest, description) {
    try {
        ensureDir(dest);
        const items = fs.readdirSync(src, { withFileTypes: true });
        
        for (const item of items) {
            const srcPath = path.join(src, item.name);
            const destPath = path.join(dest, item.name);
            
            if (item.isDirectory()) {
                copyDirectory(srcPath, destPath, `${item.name}/`);
            } else {
                fs.copyFileSync(srcPath, destPath);
                // Make Python files executable
                if (item.name.endsWith('.py')) {
                    fs.chmodSync(destPath, '755');
                }
            }
        }
        console.error(`   ${colors.dim}→ ${description}${colorsreset}`);
    } catch (error) {
        console.error(`${colors.red}❌ Failed to copy directory ${src}: ${error.message}${colors.reset}`);
        throw error;
    }
}

function writeFile(filePath, content, description) {
    try {
        ensureDir(path.dirname(filePath));
        fs.writeFileSync(filePath, content, 'utf8');
        fs.chmodSync(filePath, '755');
        console.error(`   ${colors.dim}→ ${description}${colorsreset}`);
    } catch (error) {
        console.error(`${colors.red}❌ Failed to write ${filePath}: ${error.message}${colors.reset}`);
        throw error;
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function migrateLegacyInstallation() {
    const globalInstall = isGlobalInstall();
    if (!globalInstall) {
        console.error(`${colors.dim}   → Skipping legacy migration for local install${colorsreset}`);
        return;
    }

    try {
        // Check for legacy Homebrew symlinks and clean them up
        const legacyPaths = [
            '/opt/homebrew/bin/super-prompt',
            '/usr/local/bin/super-prompt'
        ];

        let legacyFound = false;
        for (const legacyPath of legacyPaths) {
            if (fs.existsSync(legacyPath)) {
                try {
                    const linkTarget = fs.readlinkSync(legacyPath);
                    if (linkTarget && linkTarget.includes('node_modules/@cdw0424/super-prompt')) {
                        console.error(`${colors.yellow}   → Found legacy symlink: ${legacyPath}${colorsreset}`);
                        legacyFound = true;

                        // Remove legacy symlink
                        try {
                            fs.unlinkSync(legacyPath);
                            console.error(`${colors.green}   ✓ Removed legacy symlink: ${legacyPath}${colorsreset}`);
                        } catch (removeError) {
                            // If we can't remove it directly, it might be owned by root
                            console.error(`${colors.yellow}   ⚠ Legacy symlink detected but couldn't remove automatically${colorsreset}`);
                            console.error(`${colors.dim}     Run: sudo rm ${legacyPath}${colorsreset}`);
                        }
                    }
                } catch (readError) {
                    // Not a symlink or other error, continue
                }
            }
        }

        if (legacyFound) {
            console.error(`${colors.green}   ✓ Legacy symlink cleanup completed${colorsreset}`);
        } else {
            console.error(`${colors.dim}   → No legacy installation found${colorsreset}`);
        }

    } catch (error) {
        console.error(`${colors.yellow}   ⚠ Legacy migration skipped: ${error.message}${colorsreset}`);
    }
}

async function animatedInstall() {
    try {
        // Step 0: Diagnose npm cache path to avoid repo-local .npm-cache churn
        try {
            const cwd = process.cwd();
            const cachePath = execSync('npm config get cache', { encoding: 'utf8' }).trim();
            const isRepoLocalCache = cachePath && (cachePath.startsWith(cwd) || cachePath.startsWith('./') || cachePath.startsWith('.\\'));
            if (isRepoLocalCache) {
                console.warn(`${colors.yellow}🚨 CRITICAL: npm cache configured locally - this causes infinite git analysis loops!${colors.reset}`);
                console.warn(`${colors.red}   Cache path: ${cachePath}${colors.reset}`);
                console.warn(`${colors.red}   This creates massive .npm-cache/_cacache changes during npm install${colors.reset}`);
                console.warn(`${colors.red}   Git watchers will get stuck analyzing cache files endlessly${colors.reset}`);
                console.warn(`${colors.dim}   ════════════════════════════════════════════════════════════${colors.reset}`);
                console.warn(`${colors.green}   🔧 QUICK FIX (run this now):${colors.reset}`);
                console.warn(`   ${colors.cyan}npm config set cache ~/.npm${colors.reset}`);
                if (fs.existsSync('.git')) {
                    console.warn(`${colors.cyan}   git rm -r --cached .npm-cache/ 2>/dev/null || true${colors.reset}`);
                    console.warn(`${colors.cyan}   echo ".npm-cache/" >> .gitignore${colors.reset}`);
                }
                console.warn(`${colors.dim}   ────────────────────────────────────────────────────────────${colors.reset}`);
                console.warn(`${colors.blue}   🛠️  ADVANCED: Use the diagnostic script:${colors.reset}`);
                console.warn(`   ${colors.cyan}npx @cdw0424/super-prompt run scripts/codex/npm-cache-fix.sh --fix${colors.reset}`);
                console.warn(`${colors.dim}   ════════════════════════════════════════════════════════════${colors.reset}`);
                console.warn(`${colors.yellow}   Installation will continue but npm cache issues remain.${colors.reset}`);
                console.warn(`${colors.yellow}   Fix this BEFORE running npm install to avoid git loops!${colors.reset}`);
                console.warn(``);
            }
        } catch (_) { /* ignore diagnostics */ }

        // Step 1.5: Offer Codex CLI install/upgrade (user choice)
        const wantEnv = process.env.SUPER_PROMPT_CODEX_INSTALL;
        let wantCodex = null;
        if (wantEnv === '1' || wantEnv === 'yes' || wantEnv === 'true') wantCodex = true;
        if (wantEnv === '0' || wantEnv === 'no' || wantEnv === 'false') wantCodex = false;
        if (wantCodex === null && process.stdin.isTTY) {
            try {
                // Try to use readline-sync if available, otherwise default to no
                let readline;
                try {
                    readline = require('readline-sync');
                } catch (e) {
                    // readline-sync not available, default to no
                    wantCodex = false;
                }
                
                if (readline) {
                    const ans = readline.question(`${colors.cyan}🧠 Install/upgrade Codex CLI now? [Y/n] ${colors.reset}`);
                    wantCodex = !(String(ans || '').toLowerCase().startsWith('n'));
                }
            } catch (_) {
                wantCodex = false;
            }
        }
        if (wantCodex) {
            console.error(`${colors.cyan}🧠 Ensuring Codex CLI (high reasoning) is up-to-date...${colorsreset}`);
            try {
                execSync('npm install -g @openai/codex@latest', { stdio: 'inherit' });
                completedStep('1.5', 'Codex CLI updated to latest');
            } catch (e) {
                console.error(`${colors.yellow}⚠️  Could not update Codex CLI automatically. You can run:${colorsreset}`);
                console.error(`   ${colors.cyan}npm install -g @openai/codex@latest${colorsreset}`);
            }
        } else {
            console.error(`${colors.dim}Skipping Codex CLI install/upgrade (set SUPER_PROMPT_CODEX_INSTALL=1 to enable)${colorsreset}`);
        }

        // Step 1.8: Detect and migrate legacy installations
        console.error(`${colors.cyan}🔄 Checking for legacy installations...${colorsreset}`);
        await migrateLegacyInstallation();

        // Step 2: Ensure Python CLI lives under .super-prompt (unified location)
        console.error(`${colors.cyan}🐍 Ensuring .super-prompt Python CLI...${colorsreset}`);

        // The directory of the package itself, keeping helpers under .super-prompt
        const packageDir = __dirname;
        const superPromptDir = path.join(packageDir, '.super-prompt');
        ensureDir(superPromptDir);


        await sleep(300);
        completedStep('2', '.super-prompt utilities installed');

        // Step 3: system dependency checks rely on host Python availability
        completedStep('3', 'System dependency checks skipped (system Python assumed)');

        // Step 4: Remove auto-init logic, it's better for the user to run it explicitly.
        
        // Step 5: Ready for project initialization (run in your project)
        console.error(`${colors.cyan}⚡ Ready to set up your project integration...${colorsreset}`);
        console.error(`${colors.dim}   Run this inside your project to install rules & commands:${colorsreset}`);
        console.error(`   ${colors.cyan}super-prompt super:init${colorsreset}`);
        console.error(`   ${colors.cyan}# or if not globally installed:${colorsreset}`);
        console.error(`   ${colors.cyan}npx @cdw0424/super-prompt super:init${colorsreset}`);
        await sleep(300);
        completedStep(4, 'Project integration ready')

        // Remove legacy flag-only shell hook installation
        
        // Installation complete
        console.error(`\n${colors.green}${colors.bold}🎉 Installation Complete!${colorsreset}\n`);
        
        console.error(`${colors.magenta}${colors.bold}📖 Quick Start:${colorsreset}`);

        // Check if super-prompt is accessible in current session
        let commandAvailable = false;
        try {
            execSync('which super-prompt', { stdio: 'ignore' });
            commandAvailable = true;
        } catch (_) {}

        if (!commandAvailable) {
            console.error(`${colors.yellow}⚠️  Command not available in current session${colorsreset}`);
            console.error(`${colors.cyan}   → Try: which super-prompt${colorsreset}`);
            console.error(`${colors.cyan}   → Or restart terminal for PATH updates${colorsreset}\n`);
        }

        console.error(`${colors.dim}   Initialize in your project:${colorsreset}`);
        console.error(`   ${colors.cyan}super-prompt super:init${colorsreset}`);
        console.error(`   ${colors.cyan}npx @cdw0424/super-prompt super:init${colorsreset}\n`);

        console.error(`${colors.dim}   Use personas in your IDE after configuring the MCP Server.${colorsreset}`);
        console.error(`   ${colors.cyan}/frontend  "design strategy"${colorsreset}`);
        console.error(`   ${colors.cyan}/backend   "debug intermittent failures"${colorsreset}`);
        console.error(`   ${colors.cyan}/architect "break down a feature"${colorsreset}`);
        
        console.error(`${colors.blue}🔗 Package: https://npmjs.com/package/@cdw0424/super-prompt${colorsreset}`);
        console.error(`${colors.green}✨ Ready for next-level prompt engineering!${colorsreset}`);
        
    } catch (error) {
        console.error(`${colors.red}❌ Installation failed: ${error.message}${colors.reset}`);
        process.exit(1);
    }
}

// Run animated installation
animatedInstall();
