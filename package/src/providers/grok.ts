// src/providers/grok.ts
import type { LLMProvider } from '../core/mode';

export function createGrokProvider(cfg: { apiKey?: string; model?: string; }) : LLMProvider {
  const key = cfg.apiKey || process.env.XAI_API_KEY;
  const model = cfg.model || process.env.XAI_MODEL || 'grok-2-mini';
  return {
    name: 'grok',
    async chat({messages}) {
      if (!key) throw new Error('XAI_API_KEY missing');
      // 실제 xAI 호출 로직 연결(생략)
      return { model, messages };
    },
    async dispose() { /* 세션 정리 */ }
  };
}
