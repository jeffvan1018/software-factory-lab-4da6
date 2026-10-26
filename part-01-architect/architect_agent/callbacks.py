from google.adk.agents.callback_context import CallbackContext


async def inject_session_id(callback_context: CallbackContext) -> None:
    """Injects the session and conversation IDs into state for template formatting."""
    session = getattr(callback_context, "session", None)
    session_id = getattr(session, "id", None) or "default_session"
    state = callback_context.state
    if "session_id" not in state:
        state["session_id"] = session_id
    if "conversation_id" not in state:
        state["conversation_id"] = session_id
