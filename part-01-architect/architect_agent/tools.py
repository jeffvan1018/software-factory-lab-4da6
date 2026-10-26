from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import (
    Capabilities,
    GCSToolSettings,
)

# ==============================================================================
# TODO 1: Configure the GCS Toolset for the Architect Agent
# ==============================================================================
# The architect agent needs to persist the finalized Product Requirements
# Document (PRD.md) into Google Cloud Storage once approved by the user.
#
# Requirements:
# 1. Instantiate `GCSToolset`.
# 2. Follow the principle of least privilege:
#    - Use `tool_filter=["create_object"]` so the agent can only write files
#      and cannot delete or overwrite unintended objects.
#    - Configure `gcs_tool_settings` with `GCSToolSettings(capabilities=[Capabilities.READ_WRITE])`.
# ==============================================================================

# TODO: Replace None with your GCSToolset instance
gcs_tools = None
