from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import (
    Capabilities,
    GCSToolSettings,
)

# Initialize GCS toolset with write capabilities
gcs_tools = GCSToolset(
    tool_filter=["create_object"],
    gcs_tool_settings=GCSToolSettings(
        capabilities=[Capabilities.READ_WRITE],
    ),
)
