#!/usr/bin/env node
// Lightweight MCP client bridge for Codex CLI

import process from 'node:process';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

function logError(message, error) {
  const details = error instanceof Error ? `${error.message}` : String(error);
  process.stderr.write(`-------- codex-mcp bridge error: ${message}: ${details}\n`);
}

function collectTextBlocks(content) {
  if (!Array.isArray(content)) return '';
  return content
    .filter((block) => block && typeof block === 'object' && block.type === 'text' && typeof block.text === 'string')
    .map((block) => block.text.trim())
    .filter(Boolean)
    .join('\n');
}

async function main() {
  const payloadRaw = process.env.CODEX_MCP_PAYLOAD;
  if (!payloadRaw) {
    logError('missing CODEX_MCP_PAYLOAD environment variable', 'payload required');
    process.exitCode = 2;
    return;
  }

  let payload;
  try {
    payload = JSON.parse(payloadRaw);
  } catch (error) {
    logError('failed to parse CODEX_MCP_PAYLOAD', error);
    process.exitCode = 2;
    return;
  }

  if (!payload || typeof payload.prompt !== 'string' || !payload.prompt.trim()) {
    logError('invalid payload', 'prompt is required');
    process.exitCode = 2;
    return;
  }

  const transport = new StdioClientTransport({
    command: payload.command || 'codex',
    args: Array.isArray(payload.args) ? payload.args : ['mcp'],
    env: payload.env || {},
    cwd: payload.cwd,
    stderr: 'pipe',
  });

  if (transport.stderr) {
    transport.stderr.on('data', (chunk) => {
      if (chunk) process.stderr.write(chunk);
    });
  }

  const client = new Client({
    name: payload.clientName || 'super-prompt-codex-bridge',
    version: payload.clientVersion || 'unknown',
  });

  try {
    await client.connect(transport, { timeout: payload.timeoutMs || 120000 });

    if (payload.listTools) {
      try {
        await client.listTools({});
      } catch (error) {
        logError('listTools failed (continuing)', error);
      }
    }

    const toolName = payload.toolName || 'codex';
    const args = { ...payload.arguments };
    args.prompt = payload.prompt;
    if (payload.conversationId) args.conversationId = payload.conversationId;
    if (payload.approvalPolicy) args['approval-policy'] = payload.approvalPolicy;
    if (payload.includePlan !== false) args['include-plan-tool'] = true;
    if (payload.model || !args.model) args.model = payload.model || 'gpt-5-codex';
    const config = { ...(args.config || {}) };
    if (!config.model_reasoning_effort) {
      config.model_reasoning_effort = payload.reasoningEffort || 'high';
    }
    args.config = config;
    if (!args.sandbox && payload.sandbox !== false) {
      args.sandbox = payload.sandbox || 'workspace-write';
    }
    if (payload.baseInstructions) {
      args['base-instructions'] = payload.baseInstructions;
    }

    const result = await client.callTool({ name: toolName, arguments: args });

    const output = {
      ok: !result.isError,
      isError: Boolean(result.isError),
      content: result.content || [],
      structuredContent: result.structuredContent || null,
      text: collectTextBlocks(result.content),
    };

    process.stdout.write(`${JSON.stringify(output)}\n`);
  } catch (error) {
    logError('codex MCP invocation failed', error);
    process.exitCode = 1;
  } finally {
    await client.close();
  }
}

main().catch((error) => {
  logError('unhandled exception', error);
  process.exitCode = 1;
});
