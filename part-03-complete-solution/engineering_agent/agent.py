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

root_agent = Workflow(
    name="engineering_workflow",
    edges=[
        (
            "START",
            begin_workflow,
            developer_agent,
            test_agent,
        ),
        (
            test_agent,
            test_evaluator,
            {
                "ERROR": end_workflow,
                "PASS": end_workflow,
                "FAIL": remediation_agent,
            },
        ),
        (
            remediation_agent,
            test_agent,
        ),
    ],
)
