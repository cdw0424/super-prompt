// src/commands/super-init.js
const fs = require('fs');
const path = require('path');
const readline = require('readline/promises');
const { stdin: input, stdout: output } = require('process');

const FRAMEWORKS = {
  'nextjs': {
    name: 'Next.js + TypeScript',
    description: 'React framework with TypeScript',
    files: ['20-nextjs.mdc', '30-typescript.mdc', '40-react.mdc']
  },
  'react': {
    name: 'React + TypeScript',
    description: 'React library with TypeScript',
    files: ['30-typescript.mdc', '40-react.mdc']
  },
  'react-router': {
    name: 'React Router v7 + TypeScript',
    description: 'React Router v7 with TypeScript',
    files: ['30-typescript.mdc', '40-react.mdc', '45-react-router-v7.mdc']
  },
  'vue': {
    name: 'Vue.js + TypeScript',
    description: 'Vue.js framework with TypeScript',
    files: ['30-typescript.mdc', '50-vue.mdc']
  },
  'python': {
    name: 'Python',
    description: 'Python development',
    files: ['60-python.mdc']
  },
  'django': {
    name: 'Django',
    description: 'Django web framework',
    files: ['60-python.mdc', '70-django.mdc']
  },
  'fastapi': {
    name: 'FastAPI',
    description: 'FastAPI framework',
    files: ['60-python.mdc', '80-fastapi.mdc']
  },
  'all': {
    name: 'All Frameworks',
    description: 'Install all framework rules',
    files: ['20-nextjs.mdc', '30-typescript.mdc', '40-react.mdc', '45-react-router-v7.mdc', '50-vue.mdc', '60-python.mdc', '70-django.mdc', '80-fastapi.mdc']
  }
};

function ensureDir(p) { 
  if (!fs.existsSync(p)) {
    fs.mkdirSync(p, { recursive: true }); 
  }
}

async function promptFramework() {
  const rl = readline.createInterface({ input, output });
  
  try {
    console.log('');
    console.log('📦 Select your project type:');
    console.log('');
    console.log('  1. Next.js + TypeScript (React framework)');
    console.log('  2. React + TypeScript');
    console.log('  3. React Router v7 + TypeScript');
    console.log('  4. Vue.js + TypeScript');
    console.log('  5. Python');
    console.log('  6. Django (Python web framework)');
    console.log('  7. FastAPI (Python API framework)');
    console.log('  8. All Frameworks (install everything)');
    console.log('');
    
    const answer = await rl.question('Enter your choice (1-8) [1]: ');
    const choice = answer.trim() || '1';
    
    const mapping = {
      '1': 'nextjs',
      '2': 'react',
      '3': 'react-router',
      '4': 'vue',
      '5': 'python',
      '6': 'django',
      '7': 'fastapi',
      '8': 'all'
    };
    
    return mapping[choice] || 'nextjs';
  } finally {
    rl.close();
  }
}

function printBanner() {
  console.log('');
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║                                                           ║');
  console.log('║              ⚡ SUPER PROMPT v7.0.0 ⚡                      ║');
  console.log('║                                                           ║');
  console.log('║     Simplified Development Assistant for Cursor IDE       ║');
  console.log('║                                                           ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  console.log('');
}

async function run(_ctx) {
  printBanner();
  
  const cwd = process.cwd();
  console.log('📁 Project Root:', cwd);
  console.log('');
  
  try {
    // Prompt for framework selection
    const isInteractive = process.stdin.isTTY && process.stdout.isTTY;
    let selectedFramework = 'nextjs';
    
    if (isInteractive) {
      selectedFramework = await promptFramework();
    }
    
    const frameworkConfig = FRAMEWORKS[selectedFramework];
    console.log('');
    console.log(`✨ Selected: ${frameworkConfig.name}`);
    console.log('');
    console.log('🚀 Initializing Super Prompt...');
    console.log('');

    // Copy .cursor/ files from package to user project
    const cursorDir = path.join(cwd, '.cursor');
    console.log('📂 Setting up .cursor/ directory...');
    ensureDir(cursorDir);
    const packageCursorDir = path.join(__dirname, '..', '..', '.cursor');
    
    if (!fs.existsSync(packageCursorDir)) {
      console.error('');
      console.error('❌ CRITICAL ERROR: .cursor files not found in package');
      console.error('❌ Please reinstall Super Prompt: npm install @cdw0424/super-prompt');
      process.exitCode = 1;
      return;
    }

    console.log('📦 Copying Cursor Rules & Commands...');
    
    let copiedCount = 0;
    const selectedFiles = new Set(frameworkConfig.files);
    
    // Copy .cursor/ directory selectively
    function copyDir(src, dest, relativePath = '') {
      if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
      }
      
      const entries = fs.readdirSync(src, { withFileTypes: true });
      for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        const relPath = path.join(relativePath, entry.name);
        
        if (entry.isDirectory()) {
          // Skip frameworks directory during initial copy
          if (entry.name === 'frameworks') {
            continue;
          }
          copyDir(srcPath, destPath, relPath);
        } else {
          // With --force, always overwrite
          if (process.argv.includes('--force') || !fs.existsSync(destPath)) {
            fs.copyFileSync(srcPath, destPath);
            const displayPath = path.relative(cwd, destPath);
            console.log(`  ✓ ${displayPath}`);
            copiedCount++;
          }
        }
      }
    }
    
    // Copy base rules and roles
    copyDir(packageCursorDir, cursorDir);
    
    // Copy selected framework rules
    const frameworksDir = path.join(packageCursorDir, 'frameworks');
    if (fs.existsSync(frameworksDir)) {
      const destRulesDir = path.join(cursorDir, 'rules');
      ensureDir(destRulesDir);
      
      for (const file of selectedFiles) {
        const srcFile = path.join(frameworksDir, file);
        const destFile = path.join(destRulesDir, file);
        
        if (fs.existsSync(srcFile)) {
          if (process.argv.includes('--force') || !fs.existsSync(destFile)) {
            fs.copyFileSync(srcFile, destFile);
            const displayPath = path.relative(cwd, destFile);
            console.log(`  ✓ ${displayPath}`);
            copiedCount++;
          }
        }
      }
    }
    
    console.log('');
    console.log(`✅ Copied ${copiedCount} files to .cursor/`);

    // Installation complete
    console.log('');
    console.log('╔═══════════════════════════════════════════════════════════╗');
    console.log('║                                                           ║');
    console.log('║              ✅ Installation Complete! ✅                 ║');
    console.log('║                                                           ║');
    console.log('╚═══════════════════════════════════════════════════════════╝');
    console.log('');
    console.log('📚 Available Features:');
    console.log('');
    console.log('  🎯 Cursor Rules (Auto-applied):');
    console.log('     • Code Quality Guidelines');
    console.log('     • Clean Code Principles');
    
    // Show installed framework rules
    if (selectedFiles.size > 0) {
      console.log('     • Framework-specific rules:');
      for (const file of selectedFiles) {
        const ruleName = file.replace('.mdc', '').replace(/^\d+-/, '');
        console.log(`       - ${ruleName.charAt(0).toUpperCase() + ruleName.slice(1)}`);
      }
    }
    console.log('');
    console.log('  👥 Roles (Use with @):');
    console.log('     • @architect    - System architecture design');
    console.log('     • @backend      - Backend & API development');
    console.log('     • @frontend     - Frontend & UI/UX development');
    console.log('     • @devops       - DevOps & SRE');
    console.log('     • @double-check - Risk audit & verification');
    console.log('     • @performance  - Performance optimization');
    console.log('     • @qa           - Quality assurance & testing');
    console.log('     • @refactor     - Code refactoring');
    console.log('     • @security     - Security & privacy');
    console.log('     • @troubleshooting - Debugging & incident response');
    console.log('');
    console.log('  ⚡ Commands (Use with /):');
    console.log('     • /sdd-micro    - Spec-Driven Development workflow');
    console.log('');
    console.log('🚀 Get Started:');
    console.log('   Try: /sdd-micro to start your first feature!');
    console.log('');

    process.exitCode = 0;
  } catch (err) {
    console.error('');
    console.error('❌ Installation failed:', err?.message || err);
    console.error('');
    process.exitCode = 1;
  }
}

// Export for use in bin/super-prompt
if (require.main === module) {
  run().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
} else {
  module.exports = { run };
}
