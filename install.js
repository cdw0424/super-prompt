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
      console.log(`✅ Created npm cache directory: ${cacheDir}`);
    }

    // Fix permissions on cache directory
    try {
      execSync(`chmod -R 755 "${cacheDir}"`, { stdio: 'ignore' });
      console.log('✅ Fixed npm cache permissions');
    } catch (permError) {
      console.log('⚠️  Cache permission fix skipped (non-critical)');
    }
  } catch (error) {
    console.log('⚠️  Cache setup skipped:', error.message);
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

async function setupPythonVenv(superPromptDir) {
    try {
        console.log(`${colors.cyan}🐍 Setting up Python virtual environment...${colors.reset}`);

        const venvDir = path.join(superPromptDir, 'venv');
        const platform = os.platform();

        // Remove existing venv if it exists
        if (fs.existsSync(venvDir)) {
            console.log(`${colors.dim}   → Removing existing venv...${colors.reset}`);
            fs.rmSync(venvDir, { recursive: true, force: true });
        }

        // Create virtual environment
        console.log(`${colors.dim}   → Creating virtual environment...${colors.reset}`);
        const pythonCmd = platform === 'win32' ? 'python' : 'python3';
        execSync(`${pythonCmd} -m venv "${venvDir}"`, { stdio: 'inherit' });

        // Determine pip and python paths in venv
        const venvBin = platform === 'win32' ? path.join(venvDir, 'Scripts') : path.join(venvDir, 'bin');
        const venvPip = platform === 'win32' ? path.join(venvBin, 'pip.exe') : path.join(venvBin, 'pip');
        const venvPython = platform === 'win32' ? path.join(venvBin, 'python.exe') : path.join(venvBin, 'python');

        // Upgrade pip in venv
        console.log(`${colors.dim}   → Upgrading pip in virtual environment...${colors.reset}`);
        execSync(`"${venvPython}" -m pip install --upgrade pip`, { stdio: 'inherit' });

        // Install required Python packages (minimal set)
        const packages = [
            'typer>=0.9.0',      // CLI framework
            'pyyaml>=6.0',       // YAML parsing
            'pathspec>=0.11.0'   // File filtering
        ];

        console.log(`${colors.dim}   → Installing Python dependencies...${colors.reset}`);
        execSync(`"${venvPip}" install ${packages.join(' ')}`, { stdio: 'inherit' });

        // Create data directory for SQLite and other files
        const dataDir = path.join(venvDir, 'data');
        ensureDir(dataDir);
        console.log(`${colors.dim}   → Created data directory for SQLite/DB files${colors.reset}`);

        // Create venv info file
        const venvInfo = {
            created: new Date().toISOString(),
            python_version: execSync(`"${venvPython}" --version`, { encoding: 'utf8' }).trim(),
            packages: packages,
            platform: platform,
            data_dir: dataDir
        };

        fs.writeFileSync(
            path.join(venvDir, 'venv-info.json'),
            JSON.stringify(venvInfo, null, 2),
            'utf8'
        );

        console.log(`${colors.green}   ✓ Python virtual environment created successfully${colors.reset}`);
        console.log(`${colors.dim}     venv: ${venvDir}${colors.reset}`);
        console.log(`${colors.dim}     data: ${dataDir}${colors.reset}`);

    } catch (error) {
        console.log(`${colors.yellow}   ⚠ Virtual environment setup failed: ${error.message}${colors.reset}`);
        console.log(`${colors.dim}     Super Prompt will attempt to use system Python${colors.reset}`);
    }
}

async function migrateLegacyInstallation() {
    const globalInstall = isGlobalInstall();
    if (!globalInstall) {
        console.log(`${colors.dim}   → Skipping legacy migration for local install${colors.reset}`);
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
                        console.log(`${colors.yellow}   → Found legacy symlink: ${legacyPath}${colors.reset}`);
                        legacyFound = true;

                        // Remove legacy symlink
                        try {
                            fs.unlinkSync(legacyPath);
                            console.log(`${colors.green}   ✓ Removed legacy symlink: ${legacyPath}${colors.reset}`);
                        } catch (removeError) {
                            // If we can't remove it directly, it might be owned by root
                            console.log(`${colors.yellow}   ⚠ Legacy symlink detected but couldn't remove automatically${colors.reset}`);
                            console.log(`${colors.dim}     Run: sudo rm ${legacyPath}${colors.reset}`);
                        }
                    }
                } catch (readError) {
                    // Not a symlink or other error, continue
                }
            }
        }

        if (legacyFound) {
            console.log(`${colors.green}   ✓ Legacy symlink cleanup completed${colors.reset}`);
        } else {
            console.log(`${colors.dim}   → No legacy installation found${colors.reset}`);
        }

    } catch (error) {
        console.log(`${colors.yellow}   ⚠ Legacy migration skipped: ${error.message}${colors.reset}`);
    }
}

function ensureFlagOnlyShellHook() {
  try {
    const skip = String(process.env.SP_SKIP_FLAG_ONLY_HOOK || '').toLowerCase();
    if (skip === '1' || skip === 'true' || skip === 'yes') {
      console.log(`${colors.dim}Skipping flag-only shell hook (SP_SKIP_FLAG_ONLY_HOOK=1)${colors.reset}`);
      return;
    }

    const shellPath = process.env.SHELL || '';
    const shell = shellPath.split('/').pop();
    const home = os.homedir();

    const marker = 'SP_FLAG_ONLY_HANDLER';
    let rcFile = '';
    let snippet = '';

    if (shell === 'bash') {
      rcFile = path.join(home, '.bashrc');
      snippet = `\n# ${marker}\n` +
        `command_not_found_handle() {\n` +
        `  case "$1" in\n` +
        `    --sp-*|--grok-mode-on|--grok-mode-off|--codex-mode-on|--codex-mode-off|--sp-grok-mode-on|--sp-grok-mode-off|--sp-codex-mode-on|--sp-codex-mode-off|--sp-codec-mode-on|--sp-codec-mode-off)\n` +
        `      command sp \"$@\"; return $? ;;\n` +
        `  esac\n` +
        `  echo \"bash: $1: command not found\" 1>&2\n` +
        `  return 127\n` +
        `}`;
    } else {
      // Default to zsh (macOS default)
      rcFile = path.join(home, '.zshrc');
      snippet = `\n# ${marker}\n` +
        `function command_not_found_handler() {\n` +
        `  if [[ \"$1\" == --sp-* || \"$1\" == --grok-mode-on || \"$1\" == --grok-mode-off || \"$1\" == --codex-mode-on || \"$1\" == --codex-mode-off || \"$1\" == --sp-grok-mode-on || \"$1\" == --sp-grok-mode-off || \"$1\" == --sp-codex-mode-on || \"$1\" == --sp-codex-mode-off || \"$1\" == --sp-codec-mode-on || \"$1\" == --sp-codec-mode-off ]]; then\n` +
        `    command sp \"$@\"\n` +
        `    return $?\n` +
        `  fi\n` +
        `  return 127\n` +
        `}`;
    }

    // Idempotent append
    let current = '';
    try { current = fs.readFileSync(rcFile, 'utf8'); } catch (_) {}
    if (!current.includes(marker)) {
      fs.appendFileSync(rcFile, `\n${snippet}\n`, 'utf8');
      console.log(`-------- Installed flag-only handler in ${rcFile}`);
    } else {
      console.log(`-------- Flag-only handler already present in ${rcFile}`);
    }
  } catch (e) {
    console.log(`${colors.dim}Flag-only shell hook skipped: ${e && e.message}${colors.reset}`);
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

        // Step 1.8: Detect and migrate legacy installations
        console.log(`${colors.cyan}🔄 Checking for legacy installations...${colors.reset}`);
        await migrateLegacyInstallation();

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

            // FORCE COPY ADVANCED .super-prompt utilities from templates
            // This ensures all projects get the latest version regardless of installation time
            const templateSuperPromptDir = path.join(__dirname, 'packages', 'cursor-assets', 'templates');

            try {
                if (fs.existsSync(templateSuperPromptDir)) {
                    copyDirectory(
                        templateSuperPromptDir,
                        superPromptDir,
                        'Super Prompt utility suite (advanced version)'
                    );
                    console.log(`   ${colors.dim}→ Using advanced .super-prompt utilities from templates${colors.reset}`);
                } else {
                    // Try alternative paths
                    const altPaths = [
                        path.join(__dirname, 'packages', 'cursor-assets', 'templates'),
                        path.join(__dirname, '..', 'packages', 'cursor-assets', 'templates'),
                        path.join(__dirname, 'templates')
                    ];

                    let copied = false;
                    for (const altPath of altPaths) {
                        if (fs.existsSync(altPath)) {
                            copyDirectory(
                                altPath,
                                superPromptDir,
                                'Super Prompt utility suite (advanced version)'
                            );
                            console.log(`   ${colors.dim}→ Using advanced .super-prompt utilities from ${altPath}${colors.reset}`);
                            copied = true;
                            break;
                        }
                    }

                    if (!copied) {
                        console.log(`   ${colors.dim}→ Templates not found, skipping .super-prompt setup${colors.reset}`);
                    }
                }
            } catch (error) {
                console.log(`   ${colors.dim}→ Error copying .super-prompt utilities: ${error.message}${colors.reset}`);
            }

            // FORCE COPY ADVANCED PACKAGES (core-py, cli-node, cursor-assets)
            console.log(`${colors.cyan}📦 Installing packages utilities...${colors.reset}`);
            const packagesDir = path.join(projectRoot, 'packages');
            const templatePackagesDir = path.join(__dirname, 'packages', 'cursor-assets', 'templates', 'packages');

            console.log(`   ${colors.dim}→ DEBUG: __dirname: ${__dirname}${colors.reset}`);
            console.log(`   ${colors.dim}→ DEBUG: templatePackagesDir: ${templatePackagesDir}${colors.reset}`);
            console.log(`   ${colors.dim}→ DEBUG: templatePackagesDir exists: ${fs.existsSync(templatePackagesDir)}${colors.reset}`);

            try {
                if (fs.existsSync(templatePackagesDir)) {
                    console.log(`   ${colors.dim}→ DEBUG: Starting packages copy from ${templatePackagesDir} to ${packagesDir}${colors.reset}`);
                    copyDirectory(
                        templatePackagesDir,
                        packagesDir,
                        'Super Prompt packages suite (advanced version)'
                    );
                    console.log(`   ${colors.dim}→ Using advanced packages utilities from templates${colors.reset}`);
                } else {
                    console.log(`   ${colors.dim}→ Templates not found, skipping packages setup${colors.reset}`);
                    console.log(`   ${colors.dim}→ DEBUG: Looking for alternative paths...${colors.reset}`);

                    // Try alternative paths
                    const altPaths = [
                        path.join(__dirname, 'packages', 'cursor-assets', 'templates'),
                        path.join(__dirname, '..', 'packages', 'cursor-assets', 'templates', 'packages'),
                        path.join(__dirname, 'templates', 'packages')
                    ];

                    let copied = false;
                    for (const altPath of altPaths) {
                        console.log(`   ${colors.dim}→ DEBUG: Trying alternative path: ${altPath} (exists: ${fs.existsSync(altPath)})${colors.reset}`);
                        if (fs.existsSync(altPath)) {
                            copyDirectory(
                                altPath,
                                packagesDir,
                                'Super Prompt packages suite (alternative path)'
                            );
                            console.log(`   ${colors.dim}→ Using advanced packages utilities from ${altPath}${colors.reset}`);
                            copied = true;
                            break;
                        }
                    }

                    if (!copied) {
                        console.log(`   ${colors.dim}→ No packages templates found, skipping setup${colors.reset}`);
                    }
                }
            } catch (error) {
                console.log(`   ${colors.dim}→ Error copying packages utilities: ${error.message}${colors.reset}`);
            }

            // Install canonical tag-executor.sh (kept minimal to avoid drift)
            const advancedTagSrc = path.join(__dirname, 'packages', 'cursor-assets', 'templates', 'tag-executor.sh');
            const cursorCommandsDir = path.join(projectRoot, '.cursor', 'commands', 'super-prompt');
            ensureDir(cursorCommandsDir);
            const advancedTagDest = path.join(cursorCommandsDir, 'tag-executor.sh');

            if (fs.existsSync(advancedTagSrc)) {
                fs.copyFileSync(advancedTagSrc, advancedTagDest);
                fs.chmodSync(advancedTagDest, '755');
                console.log(`   ${colors.dim}→ tag-executor.sh installed (canonical wrapper with Python fallback)${colors.reset}`);
            } else {
                console.log(`   ${colors.dim}→ Warning: tag-executor.sh not found at ${advancedTagSrc}${colors.reset}`);
            }

            // Create Python virtual environment in .super-prompt
            await setupPythonVenv(superPromptDir);
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

        // Install flag-only shell hook automatically (optional)
        console.log(`${colors.cyan}🪝 Installing flag-only shell handler (--sp-*, mode toggles)...${colors.reset}`);
        ensureFlagOnlyShellHook();

        // Installation complete
        console.log(`\n${colors.green}${colors.bold}🎉 Installation Complete!${colors.reset}\n`);
        
        console.log(`${colors.magenta}${colors.bold}📖 Quick Start:${colors.reset}`);

        // Check if super-prompt is accessible in current session
        let commandAvailable = false;
        try {
            execSync('which super-prompt', { stdio: 'ignore' });
            commandAvailable = true;
        } catch (_) {}

        if (!commandAvailable) {
            console.log(`${colors.yellow}⚠️  Command not available in current session${colors.reset}`);
            console.log(`${colors.cyan}   → Try: which super-prompt${colors.reset}`);
            console.log(`${colors.cyan}   → Or restart terminal for PATH updates${colors.reset}\n`);
        }

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
