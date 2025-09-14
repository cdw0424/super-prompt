// src/providers/openai.ts
import type { LLMProvider } from '../core/mode';

export function createOpenAIProvider(cfg: { apiKey?: string; model?: string; }) : LLMProvider {
  const key = cfg.apiKey || process.env.OPENAI_API_KEY;
  const model = cfg.model || process.env.OPENAI_MODEL || 'gpt-4o-mini';
  return {
    name: 'gpt',
    async chat({messages}) {
      if (!key) throw new Error('OPENAI_API_KEY missing');
      // 실제 OpenAI 호출 로직 연결(생략)
      return { model, messages };
    },
    async dispose() { /* 스트림/세션 정리 필요 시 */ }
  };
}
