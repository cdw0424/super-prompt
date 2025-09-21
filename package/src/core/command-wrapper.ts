// src/core/command-wrapper.ts
import { createMemoryClient } from '../mcp/memory';

const kWithMemory = Symbol('withMemory');

export function withMemory(run: (ctx: any)=>Promise<any>, commandId: string) {
  const wrapped: any = async (ctx: any={}) => {
    const memory = ctx.memory || await createMemoryClient();
    ctx.memory = memory;
    const span = await memory.startSpan({ commandId, userId: ctx.user?.id });
    try {
      const res = await run(ctx);
      await memory.write(span, { type: 'result', data: res });
      await memory.endSpan(span, 'ok');
      return res;
    } catch (err: any) {
      await memory.write(span, { type: 'error', message: String(err?.message || err) });
      await memory.endSpan(span, 'error', { stack: err?.stack });
      throw err;
    } finally {
      if (typeof memory.dispose === 'function') await memory.dispose();
    }
  };
  wrapped[kWithMemory] = true;
  return wrapped;
}

export function isMemoryWrapped(fn: Function) { return Boolean((fn as any)[kWithMemory]); }
