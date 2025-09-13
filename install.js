#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
const pkg = require('./package.json');

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

console.log(logo);

// Progress animation
let dots = 0;
const progressChars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
let progressIndex = 0;

function showProgress(message) {
    process.stdout.write(`${colors.cyan}${progressChars[progressIndex]} ${message}${colors.reset}\r`);
    progressIndex = (progressIndex + 1) % progressChars.length;
}

function completedStep(step, message) {
    console.log(`${colors.green}✓${colors.reset} ${colors.bold}Step ${step}:${colors.reset} ${message}`);
}

// Start installation
console.log(`${colors.yellow}${colors.bold}🚀 Starting installation...${colors.reset}\n`);

// Check platform
const platform = os.platform();
console.log(`${colors.cyan}⚙️  Checking platform compatibility...${colors.reset}`);

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
        console.log(`   ${colors.dim}→ ${description}${colors.reset}`);
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
        console.log(`   ${colors.dim}→ ${description}${colors.reset}`);
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
        console.log(`   ${colors.dim}→ ${description}${colors.reset}`);
    } catch (error) {
        console.error(`${colors.red}❌ Failed to write ${filePath}: ${error.message}${colors.reset}`);
        throw error;
    }
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
            console.log(`${colors.cyan}🧠 Ensuring Codex CLI (high reasoning) is up-to-date...${colors.reset}`);
            try {
                execSync('npm install -g @openai/codex@latest', { stdio: 'inherit' });
                completedStep('1.5', 'Codex CLI updated to latest');
            } catch (e) {
                console.warn(`${colors.yellow}⚠️  Could not update Codex CLI automatically. You can run:${colors.reset}`);
                console.warn(`   ${colors.cyan}npm install -g @openai/codex@latest${colors.reset}`);
            }
        } else {
            console.log(`${colors.dim}Skipping Codex CLI install/upgrade (set SUPER_PROMPT_CODEX_INSTALL=1 to enable)${colors.reset}`);
        }

        // Step 2: Ensure Python CLI lives under .super-prompt (unified location)
        console.log(`${colors.cyan}🐍 Ensuring .super-prompt Python CLI...${colors.reset}`);
        const projectRoot = findProjectRoot();
        const globalInstall = isGlobalInstall();
        if (globalInstall) {
            console.log(`${colors.dim}Detected global install — will not modify your current directory${colors.reset}`);
        }

        // Step 2.5: Setting up .super-prompt directory
        console.log(`${colors.cyan}📁 Installing .super-prompt utilities...${colors.reset}`);

        if (!globalInstall) {
            const superPromptDir = path.join(projectRoot, '.super-prompt');
            copyDirectory(
                path.join(__dirname, '.super-prompt'),
                superPromptDir,
                'Super Prompt utility suite'
            );
        } else {
            console.log(`${colors.dim}Skipping .super-prompt copy on global install${colors.reset}`);
        }
        
        await sleep(300);
        completedStep('2', '.super-prompt utilities installed');

        // Step 3: Ensure system dependencies (Python 3 + SQLite3)
        try {
            console.log(`${colors.cyan}🧩 Ensuring system dependencies (Python 3, SQLite3)...${colors.reset}`);

            const hasCmd = (cmd) => {
                try {
                    if (platform === 'win32') {
                        execSync(`where ${cmd}`, { stdio: 'ignore' });
                    } else {
                        execSync(`command -v ${cmd}`, { stdio: 'ignore', shell: '/bin/bash' });
                    }
                    return true;
                } catch (_) { return false; }
            };

            const run = (cmd) => {
                try { execSync(cmd, { stdio: 'inherit' }); return true; } catch (_) { return false; }
            };

            // Python
            let pythonOk = hasCmd('python3') || (platform === 'win32' && (hasCmd('py') || hasCmd('python')));
            if (!pythonOk) {
                if (platform === 'darwin') {
                    if (hasCmd('brew')) {
                        console.log(`${colors.dim}→ Installing python3 via Homebrew...${colors.reset}`);
                        pythonOk = run('brew install python@3');
                    }
                } else if (platform === 'linux') {
                    if (hasCmd('apt-get')) pythonOk = run('sudo -n apt-get update && sudo -n apt-get install -y python3') || pythonOk;
                    if (!pythonOk && hasCmd('dnf')) pythonOk = run('sudo -n dnf install -y python3') || pythonOk;
                    if (!pythonOk && hasCmd('yum')) pythonOk = run('sudo -n yum install -y python3') || pythonOk;
                    if (!pythonOk && hasCmd('pacman')) pythonOk = run('sudo -n pacman -S --noconfirm python') || pythonOk;
                } else if (platform === 'win32') {
                    if (hasCmd('winget')) pythonOk = run('winget install -e --id Python.Python.3.11') || pythonOk;
                    if (!pythonOk && hasCmd('choco')) pythonOk = run('choco install -y python') || pythonOk;
                }
            }
            if (!pythonOk) {
                console.warn(`${colors.yellow}⚠️  Python 3 not installed automatically. Please install manually.${colors.reset}`);
            }

            // SQLite
            let sqliteOk = hasCmd('sqlite3');
            if (!sqliteOk) {
                if (platform === 'darwin') {
                    if (hasCmd('brew')) sqliteOk = run('brew install sqlite') || sqliteOk;
                } else if (platform === 'linux') {
                    if (hasCmd('apt-get')) sqliteOk = run('sudo -n apt-get install -y sqlite3') || sqliteOk;
                    if (!sqliteOk && hasCmd('dnf')) sqliteOk = run('sudo -n dnf install -y sqlite') || sqliteOk;
                    if (!sqliteOk && hasCmd('yum')) sqliteOk = run('sudo -n yum install -y sqlite') || sqliteOk;
                    if (!sqliteOk && hasCmd('pacman')) sqliteOk = run('sudo -n pacman -S --noconfirm sqlite') || sqliteOk;
                } else if (platform === 'win32') {
                    if (hasCmd('winget')) sqliteOk = run('winget install -e --id SQLite.sqlite') || sqliteOk;
                    if (!sqliteOk && hasCmd('choco')) sqliteOk = run('choco install -y sqlite') || sqliteOk;
                }
            }
            if (!sqliteOk) {
                console.warn(`${colors.yellow}⚠️  SQLite3 not installed automatically. Please install via your package manager.${colors.reset}`);
            }
            completedStep('3', 'System dependencies checked');
        } catch (e) {
            console.warn(`${colors.yellow}⚠️  System dependency check skipped: ${e && e.message}${colors.reset}`);
        }

        // Step 4: Optional auto-init into current project on global install (opt-in)
        try {
            const autoInit = process.env.SUPER_PROMPT_AUTO_INIT;
            const shouldAuto = autoInit && /^(1|true|yes|y)$/i.test(autoInit);
            if (shouldAuto) {
                // Determine a safe project root (prefer INIT_CWD with package.json that is not ours)
                const initCwd = process.env.INIT_CWD || process.cwd();
                const pj = path.join(initCwd, 'package.json');
                if (fs.existsSync(pj)) {
                    const p = JSON.parse(fs.readFileSync(pj, 'utf8'));
                    if (p && p.name !== '@cdw0424/super-prompt') {
                        console.log(`${colors.cyan}⚡ Auto-initializing Super Prompt in ${initCwd} (SUPER_PROMPT_AUTO_INIT=1)${colors.reset}`);
                        try {
                            execSync('super-prompt super:init', { cwd: initCwd, stdio: 'inherit' });
                            completedStep('4', `Project initialized at ${initCwd}`);
                        } catch (e) {
                            console.warn(`${colors.yellow}⚠️  Auto-init failed; run manually in your project:${colors.reset}`);
                            console.warn(`   ${colors.cyan}super-prompt super:init${colors.reset}`);
                        }
                    }
                }
            }
        } catch (e) {
            console.warn(`${colors.yellow}⚠️  Auto-init skipped: ${e && e.message}${colors.reset}`);
        }

        // Step 5: Ready for project initialization (run in your project)
        console.log(`${colors.cyan}⚡ Ready to set up your project integration...${colors.reset}`);
        console.log(`${colors.dim}   Run this inside your project to install rules & commands:${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt super:init${colors.reset}`);
        console.log(`   ${colors.cyan}# or if not globally installed:${colors.reset}`);
        console.log(`   ${colors.cyan}npx @cdw0424/super-prompt super:init${colors.reset}`);
        await sleep(300);
        completedStep(5, 'Project integration ready')

        // Installation complete
        console.log(`\n${colors.green}${colors.bold}🎉 Installation Complete!${colors.reset}\n`);
        
        console.log(`${colors.magenta}${colors.bold}📖 Quick Start:${colors.reset}`);
        console.log(`${colors.dim}   Initialize in your project:${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt super:init${colors.reset}`);
        console.log(`   ${colors.cyan}npx @cdw0424/super-prompt super:init${colors.reset}\n`);

        console.log(`${colors.dim}   Use personas in CLI (optimize command is optional):${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt --sp-frontend  "design strategy"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt --sp-backend   "debug intermittent failures"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt --sp-architect "break down a feature"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt --sp-debate --rounds 6 "Should we adopt feature flags?"${colors.reset}`);
        console.log(`${colors.dim}   Tip: control runtime Codex upgrade via SP_SKIP_CODEX_UPGRADE=1 env var.${colors.reset}\n`);
        
        console.log(`${colors.blue}🔗 Package: https://npmjs.com/package/@cdw0424/super-prompt${colors.reset}`);
        console.log(`${colors.green}✨ Ready for next-level prompt engineering!${colors.reset}`);
        
    } catch (error) {
        console.error(`${colors.red}❌ Installation failed: ${error.message}${colors.reset}`);
        process.exit(1);
    }
}

// Run animated installation
animatedInstall();
