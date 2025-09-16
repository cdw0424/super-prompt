import json
import subprocess
from unittest.mock import patch

from super_prompt import mcp_server


@patch('super_prompt.mcp_server.subprocess.run')
def test_codex_mcp_payload_structure(mock_run, tmp_path, monkeypatch):
    bridge = tmp_path / 'src' / 'tools'
    bridge.mkdir(parents=True, exist_ok=True)
    bridge_file = bridge / 'codex-mcp.js'
    bridge_file.write_text('// stub bridge')

    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    monkeypatch.setattr(mcp_server, 'package_root', lambda: tmp_path)
    monkeypatch.setattr(mcp_server, 'project_root', lambda: tmp_path)

    captured = {}

    def side_effect(cmd, **kwargs):
        captured['cmd'] = cmd
        captured['kwargs'] = kwargs
        payload = kwargs['env']['CODEX_MCP_PAYLOAD']
        parsed = json.loads(payload)
        # Return a successful Codex MCP result
        result = {'ok': True, 'text': 'PLAN:\n1. Step'}
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(result), stderr='')

    mock_run.side_effect = side_effect

    output = mcp_server._call_codex_assistance('Build feature', 'Repo context', 'architect')

    assert 'PLAN' in output
    payload = json.loads(captured['kwargs']['env']['CODEX_MCP_PAYLOAD'])
    assert payload['model'] == 'gpt-5-codex'
    assert payload['includePlan'] is True
    assert payload['reasoningEffort'] == 'high'
    assert payload['env']['OPENAI_API_KEY'] == 'sk-test'
    assert '[USER REQUEST]' in payload['prompt']


@patch('super_prompt.mcp_server.subprocess.run')
def test_codex_cli_fallback_when_bridge_missing(mock_run, tmp_path, monkeypatch):
    # Ensure bridge path is absent
    monkeypatch.setattr(mcp_server, 'package_root', lambda: tmp_path)
    monkeypatch.setattr(mcp_server, 'project_root', lambda: tmp_path)

    def side_effect(cmd, **kwargs):
        assert cmd[0] == 'codex'
        return subprocess.CompletedProcess(cmd, 0, stdout='fallback', stderr='')

    mock_run.side_effect = side_effect

    output = mcp_server._call_codex_assistance('Investigate bug', 'Context data', 'analyzer')
    assert output == 'fallback'
