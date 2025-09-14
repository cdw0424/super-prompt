const kWithMemory = Symbol('withMemory');

export function withMemory(run, commandId) {
  const wrapped = async (ctx) => {
    const span = await ctx.memory.startSpan({ commandId, userId: ctx.user?.id });
    try {
      const res = await run(ctx);
      await ctx.memory.write(span, { type: 'result', data: res });
      await ctx.memory.endSpan(span, 'ok');
      return res;
    } catch (err) {
      await ctx.memory.write(span, { type: 'error', message: String(err?.message || err) });
      await ctx.memory.endSpan(span, 'error', { stack: err?.stack });
      throw err;
    }
  };
  wrapped[kWithMemory] = true;
  return wrapped;
}

export const isMemoryWrapped = (fn) => Boolean(fn && fn[kWithMemory]);
