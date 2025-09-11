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
${colors.dim}              Cursor-first Prompt Engineering Toolkit${colors.reset}
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

if (platform !== 'darwin' && platform !== 'linux') {
    console.error(`${colors.red}❌ Super Prompt only supports macOS and Linux${colors.reset}`);
    process.exit(1);
}

completedStep(1, `Platform check passed (${platform})`);

function ensureDir(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
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
        // Step 1.5: Offer Codex CLI install/upgrade (user choice)
        const wantEnv = process.env.SUPER_PROMPT_CODEX_INSTALL;
        let wantCodex = null;
        if (wantEnv === '1' || wantEnv === 'yes' || wantEnv === 'true') wantCodex = true;
        if (wantEnv === '0' || wantEnv === 'no' || wantEnv === 'false') wantCodex = false;
        if (wantCodex === null && process.stdin.isTTY) {
            try {
                const readline = require('readline-sync');
                const ans = readline.question(`${colors.cyan}🧠 Install/upgrade Codex CLI now? [Y/n] ${colors.reset}`);
                wantCodex = !(String(ans || '').toLowerCase().startsWith('n'));
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

        // Step 2: Setting up Python CLI
        console.log(`${colors.cyan}🐍 Setting up Python CLI components...${colors.reset}`);
        
        const scriptsDir = 'scripts/super_prompt';
        ensureDir(scriptsDir);
        
        copyFile(
            path.join(__dirname, 'templates/simple_cli.py'),
            path.join(scriptsDir, 'cli.py'),
            'Python CLI engine'
        );
        
        writeFile(
            path.join(scriptsDir, '__init__.py'), 
            '# super_prompt package\n',
            'Python package initialization'
        );
        
        await sleep(500);
        completedStep(2, 'Python CLI components ready');

        // Step 3: Ready for project initialization (run in your project)
        console.log(`${colors.cyan}⚡ Ready to set up your project integration...${colors.reset}`);
        console.log(`${colors.dim}   Run this inside your project to install rules & commands:${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt super:init${colors.reset}`);
        await sleep(300);
        completedStep(3, 'Project integration ready')

        // Installation complete
        console.log(`\n${colors.green}${colors.bold}🎉 Installation Complete!${colors.reset}\n`);
        
        console.log(`${colors.magenta}${colors.bold}📖 Quick Start:${colors.reset}`);
        console.log(`${colors.dim}   Initialize in your project:${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt super:init${colors.reset}`);
        console.log(`   ${colors.cyan}npx @cdw0424/super-prompt super:init${colors.reset}\n`);
        
        console.log(`${colors.dim}   Use personas in CLI (flags — no slash commands needed):${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt optimize --frontend  "design strategy"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt optimize --backend   "debug intermittent failures"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt optimize --architect "break down a feature"${colors.reset}`);
        console.log(`   ${colors.cyan}super-prompt optimize --debate --rounds 6 "Should we adopt feature flags?"${colors.reset}`);
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
