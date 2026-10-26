from google.adk import Workflow

from engineering_agent.agents import (
    developer_agent,
    remediation_agent,
    test_agent,
)
from engineering_agent.nodes import (
    begin_workflow,
    end_workflow,
    test_evaluator,
)

# ==============================================================================
# TODO 3: Assemble the Cyclical Engineering Workflow Graph
# ==============================================================================
# An ADK Workflow orchestrates agents and custom nodes as a directed graph.
# Edges define execution sequences, conditional branching, and loops.
#
# Requirements:
# Instantiate `Workflow` named "engineering_workflow" with three edges:
#
# 1. Pipeline Start (Linear edge):
#    ("START", begin_workflow, developer_agent, test_agent)
#    Initializes the workspace, downloads the PRD from GCS, generates code,
#    and runs the initial test suite.
#
# 2. Evaluation & Conditional Branching (Routing edge):
#    (
#        test_agent,
#        test_evaluator,
#        {
#            "PASS": end_workflow,
#            "FAIL": remediation_agent,
#            "ERROR": end_workflow,
#        },
#    )
#    Inspects test results. If PASS, package and upload. If FAIL, route to remediation.
#
# 3. Self-Healing Loop (Cyclic edge):
#    (remediation_agent, test_agent)
#    After the remediation agent applies a fix, route back to test_agent to re-run tests!
# ==============================================================================

# TODO: Replace None with your Workflow instance
root_agent = None
