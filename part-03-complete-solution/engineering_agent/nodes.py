import os
import re
import uuid
from urllib.parse import urlparse

from google.adk import Context, Event
from google.cloud import storage

from engineering_agent.agents import set_agent_workspaces
from engineering_agent.config import BUCKET_NAME, WORKSPACE_HOME
from engineering_agent.utils import is_path_ignored, load_gitignore_patterns


def begin_workflow(node_input: str, ctx: Context) -> Event:
    """Initializes the workflow workspace and downloads the PRD from GCS."""
    print(f"\n🚀 [begin_workflow] Initializing workflow with input: {node_input}", flush=True)
    unique_id = (
        getattr(ctx, "invocation_id", None)
        or (ctx.session.id if getattr(ctx, "session", None) else None)
        or str(uuid.uuid4())
    )
    unique_id = str(unique_id).replace("/", "_")

    workspace_dir = os.path.join(WORKSPACE_HOME, unique_id)
    os.makedirs(workspace_dir, exist_ok=True)

    https_match = re.search(
        r"https?://(?:storage\.googleapis\.com|storage\.cloud\.google\.com)/([a-zA-Z0-9_\.\-]+)/([^\s\"\'\)]+)",
        str(node_input),
    )
    gs_match = re.search(
        r"gs://([a-zA-Z0-9_\.\-]+)/([^\s\"\'\)]+)",
        str(node_input),
    )

    if https_match:
        bucket_name = https_match.group(1)
        blob_name = https_match.group(2).rstrip(".,;!?")
        source_url = https_match.group(0).rstrip(".,;!?")
    elif gs_match:
        bucket_name = gs_match.group(1)
        blob_name = gs_match.group(2).rstrip(".,;!?")
        source_url = gs_match.group(0).rstrip(".,;!?")
    else:
        raw_input = str(node_input).strip().strip("'\"")
        parsed = urlparse(raw_input)
        if parsed.scheme in ("http", "https") and (
            "googleapis.com" in parsed.netloc or "google.com" in parsed.netloc
        ):
            parts = parsed.path.lstrip("/").split("/", 1)
            bucket_name = parts[0]
            blob_name = parts[1] if len(parts) > 1 else ""
            source_url = raw_input
        elif raw_input.startswith("gs://"):
            bucket_name = parsed.netloc
            blob_name = parsed.path.lstrip("/")
            source_url = raw_input
        else:
            bucket_name = BUCKET_NAME
            blob_name = raw_input.lstrip("/")
            source_url = f"gs://{bucket_name}/{blob_name}"

    if not blob_name:
        raise ValueError(
            f"Could not determine a valid Google Cloud Storage path from input: {node_input}"
        )

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    docs_dir = os.path.join(workspace_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    file_name = os.path.basename(blob_name) or "downloaded_file"
    destination_path = os.path.join(docs_dir, file_name)
    blob.download_to_filename(destination_path)

    source_dir = os.path.dirname(blob_name)
    source_gcs_dir = f"gs://{bucket_name}/{source_dir}" if source_dir else f"gs://{bucket_name}"

    # Set the sub-agents' workspaces
    set_agent_workspaces(workspace_dir)

    state_updates = {
        "workspace_dir": workspace_dir,
        "workspace_path": workspace_dir,
        "workspace": workspace_dir,
        "workspace_name": unique_id,
        "docs_dir": docs_dir,
        "downloaded_file_path": destination_path,
        "downloaded_file": destination_path,
        "source_bucket": bucket_name,
        "source_dir": source_dir,
        "source_directory": source_dir,
        "source_gcs_dir": source_gcs_dir,
        "gcs_bucket": bucket_name,
        "gcs_dir": source_dir,
        "source_url": source_url,
        "source_blob": blob_name,
    }

    for key, value in state_updates.items():
        ctx.state[key] = value

    print(f"🏁 [begin_workflow] Initialization complete. Workspace ready at: {workspace_dir}\n", flush=True)

    return Event(
        output=(
            f"Workspace initialized at {workspace_dir}. "
            f"Downloaded {destination_path} from {source_url}."
        ),
        actions={
            "state_delta": state_updates,
        },
    )


def test_evaluator(node_input: str, ctx: Context) -> Event:
    """Evaluates test output from test_agent and routes to PASS, FAIL, or ERROR."""
    call_count = ctx.state.get("test_eval_count", 0) + 1
    ctx.state["test_eval_count"] = call_count
    print(f"\n⚖️  [test_evaluator] Evaluating test results (attempt {call_count})...", flush=True)

    test_result = None
    if node_input:
        text = str(node_input).strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        last_line = lines[-1] if lines else ""

        if last_line.upper() == "PASS" or last_line.upper().endswith("PASS"):
            test_result = "PASS"
        elif last_line.upper() == "FAIL" or last_line.upper().endswith("FAIL"):
            test_result = "FAIL"
        elif re.search(r"\bPASS\b", text, re.IGNORECASE) and not re.search(r"\bFAIL\b", text, re.IGNORECASE):
            test_result = "PASS"
        elif re.search(r"\bFAIL\b", text, re.IGNORECASE):
            test_result = "FAIL"
        else:
            test_result = text

    if test_result is None:
        test_result = (
            ctx.state.get("Test Result")
            or ctx.state.get("test_result")
            or ctx.state.get("TestResult")
        )

    if test_result is None:
        error_msg = (
            "Error: No test result found in agent output or workflow state. "
            "Terminating workflow with ERROR."
        )
        print("🏁 [test_evaluator] No test result found. Terminating workflow with ERROR.\n", flush=True)
        return Event(
            route="ERROR",
            output=error_msg,
            actions={
                "state_delta": {
                    "evaluation_status": "ERROR",
                    "evaluation_error": error_msg,
                }
            },
        )

    is_pass = False
    if isinstance(test_result, bool):
        is_pass = test_result
    elif isinstance(test_result, str):
        is_pass = test_result.strip().upper() == "PASS"
    elif isinstance(test_result, dict):
        status = test_result.get("status") or test_result.get("result") or test_result.get("outcome")
        if isinstance(status, str):
            is_pass = status.strip().upper() == "PASS"
        elif isinstance(status, bool):
            is_pass = status

    result_str = "PASS" if is_pass else "FAIL"
    ctx.state["Test Result"] = result_str

    if is_pass:
        print("🏁 [test_evaluator] Completed evaluation. Result: PASS. Routing to: end_workflow\n", flush=True)
        return Event(
            route="PASS",
            output="Test evaluation passed.",
            actions={
                "state_delta": {
                    "evaluation_status": "PASS",
                    "Test Result": "PASS",
                }
            },
        )

    if call_count >= 3:
        warning_msg = (
            f"Warning: Test evaluation failed after {call_count} iterations. "
            "Terminating workflow with ERROR to prevent an infinite loop."
        )
        print(f"🏁 [test_evaluator] Max iterations ({call_count}) exceeded. Terminating workflow with ERROR.\n", flush=True)
        return Event(
            route="ERROR",
            output=warning_msg,
            actions={
                "state_delta": {
                    "evaluation_status": "ERROR",
                    "evaluation_warning": warning_msg,
                    "Test Result": "FAIL",
                }
            },
        )

    print(f"🏁 [test_evaluator] Completed evaluation. Result: FAIL (attempt {call_count}). Routing to: remediation_agent\n", flush=True)
    return Event(
        route="FAIL",
        output=f"Test evaluation failed (attempt {call_count}). Routing to remediation.",
        actions={
            "state_delta": {
                "evaluation_status": "FAIL",
                "Test Result": "FAIL",
            }
        },
    )


def end_workflow(node_input: str, ctx: Context) -> Event:
    """Packages the completed workspace and uploads it to Google Cloud Storage."""
    workspace_dir = ctx.state.get("workspace_dir")
    if not workspace_dir or not os.path.exists(workspace_dir):
        raise ValueError(f"Workspace directory not found: {workspace_dir}")

    print(f"\n📦 [end_workflow] Starting final workflow packaging and GCS upload for workspace: {workspace_dir}...", flush=True)

    bucket_name = ctx.state.get("source_bucket") or BUCKET_NAME
    source_dir = ctx.state.get("source_dir", "")

    workspace_name = os.path.basename(os.path.normpath(workspace_dir))
    target_prefix = f"{source_dir}/{workspace_name}".strip("/") if source_dir else workspace_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    ignore_patterns = load_gitignore_patterns(workspace_dir)

    uploaded_files = []
    for root, dirs, files in os.walk(workspace_dir):
        rel_root = os.path.relpath(root, workspace_dir)
        if rel_root == ".":
            rel_root = ""

        # Prune ignored directories in-place so os.walk does not traverse them
        dirs[:] = [
            d for d in dirs
            if not is_path_ignored(os.path.join(rel_root, d) if rel_root else d, is_dir=True, patterns=ignore_patterns)
        ]

        for file in files:
            rel_path = os.path.join(rel_root, file) if rel_root else file
            if is_path_ignored(rel_path, is_dir=False, patterns=ignore_patterns):
                continue

            local_file_path = os.path.join(root, file)
            blob_path = f"{target_prefix}/{rel_path}".replace("\\", "/")
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_file_path)
            uploaded_files.append(blob_path)

    target_gcs_url = f"gs://{bucket_name}/{target_prefix}/"
    state_updates = {
        "uploaded_gcs_url": target_gcs_url,
        "uploaded_files": uploaded_files,
    }

    for key, value in state_updates.items():
        ctx.state[key] = value

    print(f"🏁 [end_workflow] Upload complete! Successfully uploaded {len(uploaded_files)} files to {target_gcs_url}\n", flush=True)

    return Event(
        output=f"Workflow completed successfully. Workspace uploaded to {target_gcs_url}",
        actions={
            "state_delta": state_updates,
        },
    )
