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

# Developer Agent Configuration
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

# Test Agent Configuration
test_agent_config = LocalAgentConfig(
    model=MODEL_NAME,
    system_instructions=test_agent_instructions,
    policies=[
        policy.deny_all(),
        policy.allow("view_file"),
        policy.allow("create_file"),
        policy.allow("edit_file"),
        policy.allow("list_directory"),
        policy.allow("find_file"),
        policy.allow("search_directory"),
        policy.allow("run_command"),
    ],
    hooks=create_agent_hooks("test_agent", "🔍", "verification"),
)

test_agent = AntigravityAgent(
    name="test_agent",
    description="Software test agent",
    mode="single_turn",
    config=test_agent_config,
)

# Remediation Agent Configuration
remediation_agent_config = LocalAgentConfig(
    model=MODEL_NAME,
    system_instructions=remediation_agent_instructions,
    policies=[
        policy.deny_all(),
        policy.allow("view_file"),
        policy.allow("create_file"),
        policy.allow("edit_file"),
        policy.allow("list_directory"),
        policy.allow("find_file"),
        policy.allow("search_directory"),
        policy.allow("run_command"),
    ],
    hooks=create_agent_hooks("remediation_agent", "🔧", "defect remediation"),
)

remediation_agent = AntigravityAgent(
    name="remediation_agent",
    description="Software remediation agent",
    mode="single_turn",
    config=remediation_agent_config,
)


def set_agent_workspaces(workspace_dir: str) -> None:
    """Sets the workspace path for all sub-agents."""
    developer_agent_config.workspaces = [workspace_dir]
    test_agent_config.workspaces = [workspace_dir]
    remediation_agent_config.workspaces = [workspace_dir]
