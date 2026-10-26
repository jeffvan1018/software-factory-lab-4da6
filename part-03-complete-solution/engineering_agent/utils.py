import fnmatch
import os

from google.antigravity.hooks import (
    on_session_end,
    on_session_start,
    post_tool_call,
)


def create_agent_hooks(agent_name: str, emoji: str, action_name: str) -> list:
    """Creates a standard set of lifecycle logging hooks for an agent."""
    @on_session_start
    def _on_start():
        print(f"\n{emoji} [{agent_name}] Starting {action_name}...", flush=True)

    @post_tool_call
    def _on_tool(result):
        print(f"   ⚙️  [{agent_name}] Executed: {result.name}", flush=True)

    @on_session_end
    def _on_end():
        print(f"✅ [{agent_name}] Completed {action_name}.\n", flush=True)

    return [_on_start, _on_tool, _on_end]


def load_gitignore_patterns(workspace_dir: str) -> list[str]:
    """Loads ignore patterns from .gitignore in workspace_dir and sensible defaults."""
    patterns = [
        ".git",
        "node_modules",
        ".next",
        "__pycache__",
        "*.pyc",
        ".venv",
        ".env",
        ".DS_Store",
    ]
    gitignore_path = os.path.join(workspace_dir, ".gitignore")
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            print(f"⚠️  [end_workflow] Warning reading .gitignore: {e}", flush=True)
    return patterns


def is_path_ignored(rel_path: str, is_dir: bool, patterns: list[str]) -> bool:
    """Checks whether a relative path matches gitignore patterns."""
    normalized_rel = rel_path.replace("\\", "/").strip("/")
    parts = normalized_rel.split("/")
    basename = parts[-1] if parts else ""

    ignored = False
    for pat in patterns:
        pat = pat.strip()
        if not pat or pat.startswith("#"):
            continue

        negated = False
        if pat.startswith("!"):
            negated = True
            pat = pat[1:]

        dir_only = pat.endswith("/")
        clean_pat = pat.rstrip("/")

        if dir_only and not is_dir:
            continue

        matched = False
        if "/" not in clean_pat:
            if fnmatch.fnmatch(basename, clean_pat):
                matched = True
            elif any(fnmatch.fnmatch(part, clean_pat) for part in parts):
                matched = True
        else:
            pat_to_match = clean_pat.lstrip("/")
            if fnmatch.fnmatch(normalized_rel, pat_to_match) or fnmatch.fnmatch(normalized_rel, f"{pat_to_match}/*"):
                matched = True

        if matched:
            ignored = not negated

    return ignored
