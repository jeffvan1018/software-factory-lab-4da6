from google.adk.labs.antigravity import AntigravityAgent
from google.antigravity import LocalAgentConfig
from google.antigravity.hooks import policy

from engineering_agent.config import MODEL_NAME
from engineering_agent.prompts import (
    developer_agent_instructions,
    remediation_agent_instructions,
    test_agent_instructions,
)
from engineering_agent.utils import create_agent_hooks

# ==============================================================================
# REFERENCE EXAMPLE: Developer Agent Configuration
# ==============================================================================
# The developer agent writes application code.
# Principle of Least Privilege: It is allowed to view, create, edit, and search files,
# but DENIED `run_command` so it cannot execute code or run test suites itself.
# ==============================================================================
developer_agent_config = LocalAgentConfig(
    model=MODEL_NAME,
    system_instructions=developer_agent_instructions,
    policies=[
        policy.deny_all(),
        policy.allow("view_file"),
        policy.allow("create_file"),
        policy.allow("edit_file"),
        policy.allow("list_directory"),
        policy.allow("find_file"),
        policy.allow("search_directory"),
    ],
    hooks=create_agent_hooks("developer_agent", "💻", "implementation"),
)

developer_agent = AntigravityAgent(
    name="developer_agent",
    description="Software developer agent",
    mode="single_turn",
    config=developer_agent_config,
)


# ==============================================================================
# TODO 1: Configure the Test Agent
# ==============================================================================
# The test agent reviews the PRD, authors test suites, and runs them.
#
# Requirements:
# 1. Define `test_agent_config` using `LocalAgentConfig`:
#    - model: MODEL_NAME
#    - system_instructions: test_agent_instructions
#    - policies:
#        * policy.deny_all()
#        * File tools: "view_file", "create_file", "edit_file", "list_directory", "find_file", "search_directory"
#        * Command execution: policy.allow("run_command") (REQUIRED to run test runners!)
#    - hooks: create_agent_hooks("test_agent", "🔍", "verification")
#
# 2. Define `test_agent` using `AntigravityAgent`:
#    - name: "test_agent"
#    - description: "Software test agent"
#    - mode: "single_turn"
#    - config: test_agent_config
# ==============================================================================

# TODO: Replace None with your LocalAgentConfig instance
test_agent_config = None

# TODO: Replace None with your AntigravityAgent instance
test_agent = None


# ==============================================================================
# TODO 2: Configure the Remediation Agent
# ==============================================================================
# The remediation agent reads test failure logs and applies minimal surgical fixes.
#
# Requirements:
# 1. Define `remediation_agent_config` using `LocalAgentConfig`:
#    - model: MODEL_NAME
#    - system_instructions: remediation_agent_instructions
#    - policies:
#        * policy.deny_all()
#        * File tools: "view_file", "create_file", "edit_file", "list_directory", "find_file", "search_directory"
#        * Command execution: policy.allow("run_command") (allows running targeted failing test)
#    - hooks: create_agent_hooks("remediation_agent", "🔧", "defect remediation")
#
# 2. Define `remediation_agent` using `AntigravityAgent`:
#    - name: "remediation_agent"
#    - description: "Software remediation agent"
#    - mode: "single_turn"
#    - config: remediation_agent_config
# ==============================================================================

# TODO: Replace None with your LocalAgentConfig instance
remediation_agent_config = None

# TODO: Replace None with your AntigravityAgent instance
remediation_agent = None


def set_agent_workspaces(workspace_dir: str) -> None:
    """Sets the workspace path for all sub-agents."""
    if developer_agent_config:
        developer_agent_config.workspaces = [workspace_dir]
    if test_agent_config:
        test_agent_config.workspaces = [workspace_dir]
    if remediation_agent_config:
        remediation_agent_config.workspaces = [workspace_dir]
