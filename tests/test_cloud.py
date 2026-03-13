# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for TheQuantCloud client module."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from quantsdk.cloud import (
    AuthenticationError,
    CloudBackendInfo,
    CloudClient,
    CloudError,
    CloudJob,
    JobNotFoundError,
    JobStatus,
    QuotaExceededError,
    UsageInfo,
)
from quantsdk.cloud.config import CloudConfig

# ─── JobStatus Tests ───


class TestJobStatus:
    """Tests for the JobStatus enum."""

    def test_terminal_states(self) -> None:
        assert JobStatus.COMPLETED.is_terminal is True
        assert JobStatus.FAILED.is_terminal is True
        assert JobStatus.TIMEOUT.is_terminal is True
        assert JobStatus.CANCELLED.is_terminal is True

    def test_non_terminal_states(self) -> None:
        assert JobStatus.SUBMITTED.is_terminal is False
        assert JobStatus.ANALYZING.is_terminal is False
        assert JobStatus.ROUTING.is_terminal is False
        assert JobStatus.QUEUED.is_terminal is False
        assert JobStatus.DISPATCHED.is_terminal is False
        assert JobStatus.RUNNING.is_terminal is False

    def test_values(self) -> None:
        assert JobStatus.SUBMITTED.value == "submitted"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"


# ─── CloudJob Tests ───


class TestCloudJob:
    def test_creation(self) -> None:
        job = CloudJob(job_id="test-123", status=JobStatus.SUBMITTED)
        assert job.job_id == "test-123"
        assert job.status == JobStatus.SUBMITTED
        assert job.backend is None
        assert job.shots == 1024

    def test_with_all_fields(self) -> None:
        job = CloudJob(
            job_id="test-456",
            status=JobStatus.RUNNING,
            backend="ibm_brisbane",
            submitted_at="2026-03-13T10:00:00Z",
            circuit_id="circ_abc",
            shots=4096,
            metadata={"user": "test"},
        )
        assert job.backend == "ibm_brisbane"
        assert job.shots == 4096


# ─── CloudBackendInfo Tests ───


class TestCloudBackendInfo:
    def test_creation(self) -> None:
        info = CloudBackendInfo(
            name="ibm_brisbane",
            provider="ibm",
            num_qubits=127,
        )
        assert info.name == "ibm_brisbane"
        assert info.is_simulator is False
        assert info.queue_depth == 0

    def test_simulator(self) -> None:
        info = CloudBackendInfo(
            name="sim_cpu",
            provider="quantsdk",
            num_qubits=24,
            is_simulator=True,
        )
        assert info.is_simulator is True


# ─── UsageInfo Tests ───


class TestUsageInfo:
    def test_defaults(self) -> None:
        usage = UsageInfo(tier="explorer")
        assert usage.tier == "explorer"
        assert usage.simulator_minutes_limit == 60.0
        assert usage.qpu_tasks_limit == 10

    def test_developer_tier(self) -> None:
        usage = UsageInfo(
            tier="developer",
            simulator_minutes_used=150.0,
            simulator_minutes_limit=300.0,
            qpu_tasks_used=45,
            qpu_tasks_limit=100,
            credits_remaining_usd=35.0,
        )
        assert usage.simulator_minutes_used == 150.0
        assert usage.credits_remaining_usd == 35.0


# ─── Exception Tests ───


class TestExceptions:
    def test_cloud_error(self) -> None:
        err = CloudError("test error", status_code=500, response={"detail": "fail"})
        assert str(err) == "test error"
        assert err.status_code == 500
        assert err.response["detail"] == "fail"

    def test_auth_error(self) -> None:
        err = AuthenticationError("bad key")
        assert isinstance(err, CloudError)

    def test_quota_error(self) -> None:
        err = QuotaExceededError("limit reached")
        assert isinstance(err, CloudError)

    def test_job_not_found(self) -> None:
        err = JobNotFoundError("no such job")
        assert isinstance(err, CloudError)


# ─── CloudClient Initialization Tests ───


class TestCloudClientInit:
    def test_with_api_key(self) -> None:
        client = CloudClient(api_key="test_key_123")
        assert client.api_base == "https://api.thequantcloud.com/v1"
        assert repr(client) == "CloudClient(api_base='https://api.thequantcloud.com/v1')"

    def test_with_custom_base(self) -> None:
        client = CloudClient(api_key="test", api_base="http://localhost:8000/v1/")
        assert client.api_base == "http://localhost:8000/v1"

    def test_from_env_var(self) -> None:
        with patch.dict(os.environ, {"QUANTCLOUD_API_KEY": "env_key_456"}):
            CloudClient()  # Should not raise AuthenticationError

    def test_no_key_raises(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("os.path.exists", return_value=False),
            pytest.raises(AuthenticationError, match="No API key"),
        ):
            CloudClient()

    def test_context_manager(self) -> None:
        with CloudClient(api_key="test") as client:
            assert client.api_base


# ─── CloudConfig Tests ───


class TestCloudConfig:
    def test_defaults(self) -> None:
        config = CloudConfig()
        assert config.api_key is None
        assert config.api_base == "https://api.thequantcloud.com/v1"
        assert config.default_shots == 1024
        assert config.auto_route is True
        assert config.optimize_for == "quality"

    def test_env_override(self) -> None:
        with patch.dict(os.environ, {
            "QUANTCLOUD_API_KEY": "env_key",
            "QUANTCLOUD_API_BASE": "http://localhost:8000",
        }):
            config = CloudConfig.load()
            assert config.api_key == "env_key"
            assert config.api_base == "http://localhost:8000"

    def test_load_with_no_files(self) -> None:
        """Should return defaults when no config files exist."""
        with patch.dict(os.environ, {}, clear=True):
            # Config path won't exist in test env typically
            config = CloudConfig.load()
            assert config.default_shots == 1024
