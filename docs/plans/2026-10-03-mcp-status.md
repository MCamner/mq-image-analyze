# MCP status implementation plan

## Goal
Valid MCP profiles, honest process status, readable terminal panels, and a working local image HTTP bridge.

## Owner repo
mq-agent

## Secondary repos
mq-mcp, macos-scripts, mq-image-analyze

## Architecture boundary
mq-agent owns status; mq-mcp owns safety profiles; macos-scripts owns menu rendering; mq-image-analyze owns image tools and their transport.

## Non-goals
No releases, commits, tool-schema changes or model downloads.

## Approval gates
File writes: authorized by user. Commit, push, deletion: outside scope.

## Test gates
- mq-agent: pytest tests/test_mcp.py tests/test_mcp_lifecycle.py
- mq-mcp: pytest tests/test_profile_safety_regression.py tests/test_model_routing_tools.py
- macos-scripts: bash tests/ui-progress-result-smoke.sh
- mq-image-analyze: pytest tests/test_mcp_http.py tests/test_mcp_tools.py tests/test_mcp_allowed_roots.py

## Rollback
Revert only the task's individual hunks; preserve pre-existing work.

### Task 1: Safety profiles
Modify mq-mcp profiles/codex.json and profiles/claude-desktop.json; remove Class C shadow from A/B profiles. Add tests/test_profile_safety_regression.py. Expect profile checks to pass.

### Task 2: Process and menu output
Modify mq-agent mq_agent/main.py and tests/test_mcp.py; show reachable unmanaged process as running externally. Modify macos-scripts terminal/menus/mq-agent-menu.sh and tests/ui-progress-result-smoke.sh; use existing passthrough helper for MCP panels. Expect truthful status and isolated panel rows.

### Task 3: Image HTTP bridge
Create mq_image_analyze/mcp/http.py and tests/test_mcp_http.py; modify mq_image_analyze/cli/serve_mcp.py and docs/mcp-tools.md. Bind HTTP to loopback port 8766; reuse registered MCP tools. Expect discovery and palette invocation to pass through HTTP.
