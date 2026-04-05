#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then execs into 'nanobot gateway'.
"""

import json
import os
import sys
from pathlib import Path


def main():
    # Paths
    config_dir = Path("/app/nanobot")
    config_path = config_dir / "config.json"
    resolved_path = config_dir / "config.resolved.json"
    workspace_dir = config_dir / "workspace"
    # venv is at /app/.venv (workspace root), not /app/nanobot/.venv
    venv_bin = Path("/app/.venv") / "bin"

    # Ensure venv bin is in PATH
    os.environ["PATH"] = str(venv_bin) + os.pathsep + os.environ.get("PATH", "")

    # Read base config
    with open(config_path) as f:
        config = json.load(f)

    # Ensure required sections exist
    if "providers" not in config:
        config["providers"] = {}
    if "custom" not in config["providers"]:
        config["providers"]["custom"] = {}
    if "agents" not in config:
        config["agents"] = {"defaults": {}}
    if "defaults" not in config["agents"]:
        config["agents"]["defaults"] = {}
    if "tools" not in config:
        config["tools"] = {}
    if "mcpServers" not in config["tools"]:
        config["tools"]["mcpServers"] = {}

    # Override from environment variables
    # LLM provider settings
    if llm_api_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = llm_api_base
    if llm_api_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = llm_api_model

    # Gateway settings
    if gateway_host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config["gateway"] = config.get("gateway", {})
        config["gateway"]["host"] = gateway_host
    if gateway_port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # MCP servers
    # LMS MCP server
    config["tools"]["mcpServers"]["lms"] = {
        "command": "python",
        "args": ["-m", "mcp_lms"],
        "env": {
            "NANOBOT_LMS_BACKEND_URL": os.environ.get(
                "NANOBOT_LMS_BACKEND_URL", "http://backend:8000"
            ),
            "NANOBOT_LMS_API_KEY": os.environ.get(
                "NANOBOT_LMS_API_KEY",
                config.get("providers", {}).get("custom", {}).get("apiKey", ""),
            ),
        },
    }

    # Holidays MCP server
    config["tools"]["mcpServers"]["holidays"] = {
        "command": "python",
        "args": ["-m", "mcp_holidays"],
    }

    # Webchat channel (for browser-based chat UI)
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_HOST", "0.0.0.0")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_PORT", "8083")
    webchat_key = os.environ.get("NANOBOT_ACCESS_KEY", "")
    if webchat_key:
        config["channels"] = config.get("channels", {})
        config["channels"]["webchat"] = {
            "enabled": True,
            "host": webchat_host,
            "port": int(webchat_port),
            "allowFrom": ["*"],
            "apiKey": webchat_key,
        }

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Resolved config written to {resolved_path}")

    # Exec into nanobot gateway using full path
    nanobot_cmd = venv_bin / "nanobot"
    os.execvp(
        str(nanobot_cmd),
        [
            str(nanobot_cmd),
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_dir),
        ],
    )


if __name__ == "__main__":
    main()
