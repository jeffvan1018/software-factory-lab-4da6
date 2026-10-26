from google.adk.agents import Agent

from architect_agent.callbacks import inject_session_id
from architect_agent.config import MODEL_NAME
from architect_agent.prompts import architect_agent_instructions
from architect_agent.tools import gcs_tools

root_agent = Agent(
    name="architect_agent",
    model=MODEL_NAME,
    description=(
        "Software architect agent that collaborates on PRDs and persists "
        "them to Cloud Storage upon approval."
    ),
    instruction=architect_agent_instructions,
    before_agent_callback=inject_session_id,
    tools=[gcs_tools],
)
