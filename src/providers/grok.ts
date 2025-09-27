// src/providers/grok.ts
import type { LLMProvider } from '../core/mode';

interface GrokMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: Array<{
    id: string;
    type: 'function';
    function: {
      name: string;
      arguments: string;
    };
  }>;
  tool_call_id?: string;
}

interface GrokTool {
  type: 'function';
  function: {
    name: string;
    description?: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
    };
  };
}

interface GrokChatOptions {
  messages: GrokMessage[];
  model?: string;
  tools?: GrokTool[];
  tool_choice?: 'auto' | 'required' | { type: 'function'; function: { name: string } };
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

interface GrokStreamChunk {
  choices: Array<{
    delta: {
      content?: string;
      reasoning_content?: string;
      tool_calls?: Array<{
        id?: string;
        type?: 'function';
        function?: {
          name?: string;
          arguments?: string;
        };
      }>;
    };
    finish_reason?: string;
  }>;
}

export function createGrokProvider(cfg: { apiKey?: string; model?: string; }) : LLMProvider {
  const key = cfg.apiKey || process.env.XAI_API_KEY;
  const model = cfg.model || process.env.XAI_MODEL || getOptimizedModelForMode();

  function getOptimizedModelForMode(): string {
    // Check environment variable for current mode
    const superPromptMode = process.env.SUPER_PROMPT_MODE?.toLowerCase();
    if (superPromptMode === 'grok') {
      return 'grok-code-fast-1';
    }
    // Default to grok-code-fast-1 for backward compatibility, but this will be overridden by mode detection
    return 'grok-code-fast-1';
  }

  function isGrokModeActive(): boolean {
    const superPromptMode = process.env.SUPER_PROMPT_MODE?.toLowerCase();
    return superPromptMode === 'grok';
  }

  return {
    name: 'grok',
    async chat({messages, tools, tool_choice = 'auto', stream = true}) {
      if (!key) throw new Error('XAI_API_KEY missing');

      const grokMessages: GrokMessage[] = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        ...(msg.tool_calls && {
          tool_calls: msg.tool_calls.map(call => ({
            id: call.id,
            type: 'function' as const,
            function: {
              name: call.function.name,
              arguments: call.function.arguments
            }
          }))
        }),
        ...(msg.role === 'tool' && msg.tool_call_id && { tool_call_id: msg.tool_call_id })
      }));

      const requestOptions: GrokChatOptions = {
        messages: grokMessages,
        model,
        tools: tools?.map(tool => ({
          type: 'function',
          function: {
            name: tool.function.name,
            description: tool.function.description,
            parameters: tool.function.parameters
          }
        })),
        tool_choice,
        stream,
        temperature: 0.1,
        max_tokens: 4096
      };

      // Remove undefined properties
      Object.keys(requestOptions).forEach(key => {
        if (requestOptions[key as keyof GrokChatOptions] === undefined) {
          delete requestOptions[key as keyof GrokChatOptions];
        }
      });

      if (stream) {
        return this._streamChat(requestOptions);
      } else {
        return this._syncChat(requestOptions);
      }
    },

    async _streamChat(options: GrokChatOptions) {
      const response = await fetch('https://api.x.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${key}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(options)
      });

      if (!response.ok) {
        throw new Error(`Grok API error: ${response.status} ${response.statusText}`);
      }

      const stream = new ReadableStream({
        async start(controller) {
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          try {
            while (true) {
              const { done, value } = await reader!.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.trim() === '' || !line.startsWith('data: ')) continue;

                if (line.includes('data: [DONE]')) break;

                try {
                  const data: GrokStreamChunk = JSON.parse(line.slice(6));
                  controller.enqueue(data);
                } catch (e) {
                  // Skip invalid JSON chunks
                  continue;
                }
              }
            }
          } finally {
            controller.close();
          }
        }
      });

      return {
        model: options.model || 'grok-code-fast-1',
        messages: options.messages,
        stream
      };
    },

    async _syncChat(options: GrokChatOptions) {
      const response = await fetch('https://api.x.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${key}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(options)
      });

      if (!response.ok) {
        throw new Error(`Grok API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      return {
        model: data.model,
        messages: [
          ...options.messages,
          {
            role: 'assistant',
            content: data.choices[0].message.content || '',
            tool_calls: data.choices[0].message.tool_calls?.map((call: any) => ({
              id: call.id,
              type: 'function',
              function: {
                name: call.function.name,
                arguments: call.function.arguments
              }
            }))
          }
        ]
      };
    },

    async dispose() {
      // Cleanup resources if needed
    }
  };
}
