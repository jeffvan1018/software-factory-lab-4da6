from google.adk.agents import Agent

from architect_agent.callbacks import inject_session_id
from architect_agent.config import MODEL_NAME
from architect_agent.prompts import architect_agent_instructions
from architect_agent.tools import gcs_tools

# ==============================================================================
# TODO 2: Define and Assemble the Root Architect Agent
# ==============================================================================
# In ADK, an Agent is defined by its model, instruction prompt, lifecycle
# callbacks, and tools.
#
# Requirements:
# 1. Instantiate `Agent(...)` as `root_agent`.
# 2. Configure the following parameters:
#    - name: "architect_agent"
#    - model: MODEL_NAME (from architect_agent.config)
#    - description: A brief summary of what this agent does (collaborates on PRDs
#      and persists them to Cloud Storage upon approval)
#    - instruction: architect_agent_instructions (from architect_agent.prompts)
#    - before_agent_callback: inject_session_id (from architect_agent.callbacks)
#    - tools: A list containing your configured GCS tools ([gcs_tools])
# ==============================================================================

# TODO: Replace None with your Agent instance
root_agent = None
