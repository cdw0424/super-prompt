// src/mcp/memory.ts
// 역할: MCP 메모리 클라이언트 생성 + NOOP 자동 전환
// 로그 규칙 준수: 모든 로그 앞에 '--------'
export interface Memory {
  startSpan(meta: { commandId: string; userId?: string }): Promise<string>;
  write(spanId: string, event: any): Promise<void>;
  endSpan(spanId: string, status: 'ok' | 'error', extra?: any): Promise<void>;
  kind: 'mcp' | 'noop';
  dispose?(): Promise<void>;
}

class NoopMemory implements Memory {
  kind: 'noop' = 'noop';
  async startSpan() { return `noop:${Date.now()}`; }
  async write() {}
  async endSpan() {}
}

export async function createMemoryClient() : Promise<Memory> {
  // 환경 변수로 완전 비활성
  if (process.env.MCP_CLIENT_DISABLED === 'true') {
    console.warn('-------- MCP memory: NOOP mode (disabled via env)');
    return new NoopMemory();
  }
  try {
    // 실제 MCP SDK 연결부 (프로젝트 SDK에 맞게 교체)
    // 예시: @modelcontextprotocol/sdk 가정 (실제 명칭에 맞게 수정)
    // const client = await createMcpClient({ endpoint: process.env.MCP_ENDPOINT, apiKey: process.env.MCP_API_KEY });
    // return wrapMcpClient(client);

    // 임시: SDK가 준비된 빌드에서는 위 주석을 해제하고 아래 라인을 제거
    console.warn('-------- MCP memory: NOOP mode (SDK stub, enable real client when ready)');
    return new NoopMemory();
  } catch (e: any) {
    console.error('-------- MCP memory: fallback to NOOP due to error:', e?.message || e);
    return new NoopMemory();
  }
}
