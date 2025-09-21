// src/core/mode.ts
import * as fs from 'fs';
import * as path from 'path';

export type Mode = 'gpt'|'grok';

export function resolveMode(env: NodeJS.ProcessEnv, argvMode?: string): Mode {
  // First check for explicit argv mode or environment variable
  let flag = (argvMode || env.LLM_MODE)?.toLowerCase();

  // If not set, try to read from mode.json file
  if (!flag) {
    try {
      const projectRoot = env.SUPER_PROMPT_PROJECT_ROOT || process.cwd();
      const modeFile = path.join(projectRoot, '.super-prompt', 'mode.json');
      if (fs.existsSync(modeFile)) {
        const data = JSON.parse(fs.readFileSync(modeFile, 'utf-8'));
        flag = data.llm_mode?.toLowerCase();
      }
    } catch (error) {
      // Silently ignore file read errors, will fall back to default
    }
  }

  // Apply environment flag overrides
  const enableGpt  = env.ENABLE_GPT === 'true';
  const enableGrok = env.ENABLE_GROK === 'true';
  if (enableGpt && enableGrok) {
    throw new Error('ERROR: Cannot enable both GPT and Grok modes simultaneously');
  }
  if (enableGpt) {
    flag = 'gpt';
  } else if (enableGrok) {
    flag = 'grok';
  }

  // Default to 'gpt' if nothing is set
  flag = flag || 'gpt';

  // Validation
  if (flag !== 'gpt' && flag !== 'grok') {
    throw new Error(`ERROR: Unsupported mode: ${flag}`);
  }

  return flag as Mode;
}

export interface LLMProvider {
  readonly name: string;
  chat(input: {messages: any[]}): Promise<any>;
  dispose?(): Promise<void>;
}
