# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Cloud configuration management.

Handles API keys, default settings, and credential storage for
TheQuantCloud client.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Default config directory
_CONFIG_DIR = Path.home() / ".quantcloud"
_CREDENTIALS_FILE = _CONFIG_DIR / "credentials"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


@dataclass
class CloudConfig:
    """Configuration for TheQuantCloud client.

    Attributes:
        api_key: API authentication key.
        api_base: Base URL for the API.
        default_backend: Default backend for execution.
        default_shots: Default number of shots.
        timeout: Request timeout in seconds.
        auto_route: Whether to enable auto-routing by default.
        optimize_for: Default optimization target.
    """

    api_key: str | None = None
    api_base: str = "https://api.thequantcloud.com/v1"
    default_backend: str | None = None
    default_shots: int = 1024
    timeout: float = 30.0
    auto_route: bool = True
    optimize_for: str = "quality"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls) -> CloudConfig:
        """Load configuration from environment and config files.

        Priority order (highest to lowest):
        1. Environment variables (QUANTCLOUD_API_KEY, QUANTCLOUD_API_BASE)
        2. Config file (~/.quantcloud/config.json)
        3. Credentials file (~/.quantcloud/credentials)
        4. Default values
        """
        config = cls()

        # Load from config file
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE) as f:
                    data = json.load(f)
                for key, value in data.items():
                    if hasattr(config, key):
                        object.__setattr__(config, key, value)
            except (json.JSONDecodeError, OSError):
                pass

        # Load API key from credentials file
        if config.api_key is None and _CREDENTIALS_FILE.exists():
            try:
                with open(_CREDENTIALS_FILE) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("api_key="):
                            config.api_key = line.split("=", 1)[1].strip()
                            break
            except OSError:
                pass

        # Environment variables override everything
        env_key = os.environ.get("QUANTCLOUD_API_KEY")
        if env_key:
            config.api_key = env_key

        env_base = os.environ.get("QUANTCLOUD_API_BASE")
        if env_base:
            config.api_base = env_base

        return config

    def save(self) -> None:
        """Save configuration to disk."""
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Save config
        data = {
            "api_base": self.api_base,
            "default_backend": self.default_backend,
            "default_shots": self.default_shots,
            "timeout": self.timeout,
            "auto_route": self.auto_route,
            "optimize_for": self.optimize_for,
        }
        with open(_CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

        # Save credentials separately (more restrictive permissions)
        if self.api_key:
            with open(_CREDENTIALS_FILE, "w") as f:
                f.write(f"api_key={self.api_key}\n")
            os.chmod(_CREDENTIALS_FILE, 0o600)
