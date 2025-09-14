// src/core/mode.ts
export type Mode = 'gpt'|'grok';

export function resolveMode(env: NodeJS.ProcessEnv, argvMode?: string): Mode {
  const flag = (argvMode || env.LLM_MODE || 'gpt').toLowerCase();
  const enableGpt  = env.ENABLE_GPT === 'true';
  const enableGrok = env.ENABLE_GROK === 'true';
  if (enableGpt && enableGrok) {
    throw new Error('ERROR: Cannot enable both GPT and Grok modes simultaneously');
  }
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
