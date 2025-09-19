# Implementation Plan

## REQ-ID: REQ-SDD-001

## Architecture Overview
- MCP stdio launcher at bin/sp-mcp

## Technical Stack
- Node CLI wrapper + Python MCP server

## Security Architecture
- Protected directories enforced (.cursor/, .super-prompt/, .codex/)

## Testing Strategy
- scripts/sdd/acceptance_self_check.py --quiet

## Deployment Strategy
- Run ./bin/super-prompt super:init in each workspace

## Success Metrics
- SDD gates report PASS on fresh initialization
