// src/core/llm-factory.ts
import { resolveMode, type Mode, type LLMProvider } from './mode';
import { createOpenAIProvider } from '../providers/openai';
import { createGrokProvider } from '../providers/grok';

let current: LLMProvider | undefined;

export function createLLM(mode?: Mode) : LLMProvider {
  const m = mode || resolveMode(process.env);
  const provider = (m === 'gpt')
    ? createOpenAIProvider({})
    : createGrokProvider({});
  return provider;
}

export async function switchLLM(next: LLMProvider) {
  if (current && current !== next && typeof current.dispose === 'function') {
    await current.dispose();
    console.log('-------- mode: disposed previous provider');
  }
  current = next;
  console.log(`-------- mode: resolved to ${next.name}`);
  return current;
}
