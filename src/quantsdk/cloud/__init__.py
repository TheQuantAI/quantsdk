# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
TheQuantCloud API client.

Provides programmatic access to TheQuantCloud platform for submitting
quantum circuits, checking job status, and retrieving results.

This is the client-side SDK module. The actual cloud service endpoints
(api.thequantcloud.com) are deployed separately.

Example::

    from quantsdk.cloud import CloudClient

    client = CloudClient(api_key="YOUR_API_KEY")
    job = client.submit(circuit, shots=1000)
    result = client.get_result(job.job_id)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ─── Constants ───

DEFAULT_API_BASE = "https://api.thequantcloud.com/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_POLL_INTERVAL = 2.0


# ─── Data Classes ───


class JobStatus(Enum):
    """Status of a cloud job."""

    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    ROUTING = "routing"
    QUEUED = "queued"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """Whether this status is a terminal state."""
        return self in (
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.TIMEOUT,
            JobStatus.CANCELLED,
        )


@dataclass
class CloudJob:
    """Represents a submitted job on TheQuantCloud.

    Attributes:
        job_id: Unique job identifier.
        status: Current job status.
        backend: Backend the job was routed to.
        submitted_at: ISO 8601 timestamp of submission.
        circuit_id: Stored circuit identifier.
        shots: Requested number of shots.
        metadata: Additional job metadata.
    """

    job_id: str
    status: JobStatus
    backend: str | None = None
    submitted_at: str | None = None
    circuit_id: str | None = None
    shots: int = 1024
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CloudBackendInfo:
    """Information about a cloud-available backend.

    Attributes:
        name: Backend identifier.
        provider: Provider name.
        num_qubits: Available qubit count.
        status: Current operational status.
        is_simulator: Whether this is a simulator.
        queue_depth: Current jobs in queue.
        avg_queue_time_sec: Estimated wait time.
        cost_per_shot: Cost per shot in USD.
    """

    name: str
    provider: str
    num_qubits: int
    status: str = "online"
    is_simulator: bool = False
    queue_depth: int = 0
    avg_queue_time_sec: float = 0.0
    cost_per_shot: float = 0.0


@dataclass
class UsageInfo:
    """Current usage and quota information.

    Attributes:
        tier: User's subscription tier.
        simulator_minutes_used: Simulator minutes used this month.
        simulator_minutes_limit: Simulator minutes limit for the tier.
        qpu_tasks_used: QPU tasks used this month.
        qpu_tasks_limit: QPU tasks limit for the tier.
        credits_remaining_usd: Remaining credits in USD.
    """

    tier: str
    simulator_minutes_used: float = 0.0
    simulator_minutes_limit: float = 60.0
    qpu_tasks_used: int = 0
    qpu_tasks_limit: int = 10
    credits_remaining_usd: float = 0.0


# ─── Exceptions ───


class CloudError(Exception):
    """Base exception for TheQuantCloud API errors."""

    def __init__(
        self, message: str, status_code: int | None = None, response: dict[str, Any] | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(CloudError):
    """Invalid or missing API key."""

    pass


class QuotaExceededError(CloudError):
    """Usage quota exceeded for the current tier."""

    pass


class JobNotFoundError(CloudError):
    """Job ID not found."""

    pass


class BackendUnavailableError(CloudError):
    """Requested backend is not available."""

    pass


# ─── Cloud Client ───


class CloudClient:
    """Client for TheQuantCloud API.

    Provides methods to submit circuits, check job status, retrieve results,
    and manage cloud resources. Communicates with api.thequantcloud.com.

    The client handles authentication, request retries, and response parsing.

    Example::

        from quantsdk.cloud import CloudClient

        # Initialize with API key
        client = CloudClient(api_key="YOUR_API_KEY")

        # Submit a circuit
        job = client.submit(circuit, shots=1000)
        print(f"Job submitted: {job.job_id}")

        # Wait for results
        result = client.wait_for_result(job.job_id, timeout=300)
        print(result.counts)

        # Check usage
        usage = client.get_usage()
        print(f"QPU tasks: {usage.qpu_tasks_used}/{usage.qpu_tasks_limit}")
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str = DEFAULT_API_BASE,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the cloud client.

        Args:
            api_key: TheQuantCloud API key. Can also be set via
                     ``QUANTCLOUD_API_KEY`` environment variable.
            api_base: API base URL. Defaults to production.
            timeout: Request timeout in seconds.

        Raises:
            AuthenticationError: If no API key is provided or found.
        """
        self._api_key = api_key or self._load_api_key()
        self._api_base = api_base.rstrip("/")
        self._timeout = timeout
        self._session: Any = None  # Lazy-loaded httpx client

    @staticmethod
    def _load_api_key() -> str:
        """Load API key from environment or config file."""
        import os

        key = os.environ.get("QUANTCLOUD_API_KEY")
        if key:
            return key

        # Try loading from ~/.quantcloud/credentials
        config_path = os.path.expanduser("~/.quantcloud/credentials")
        if os.path.exists(config_path):
            with open(config_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("api_key="):
                        return line.split("=", 1)[1].strip()

        raise AuthenticationError(
            "No API key provided. Set QUANTCLOUD_API_KEY environment variable, "
            "pass api_key= to CloudClient(), or create ~/.quantcloud/credentials"
        )

    @property
    def api_base(self) -> str:
        """API base URL."""
        return self._api_base

    def _get_session(self) -> Any:
        """Get or create an HTTP client session."""
        if self._session is None:
            try:
                import httpx
            except ImportError as exc:
                raise ImportError(
                    "Cloud client requires httpx. Install with: pip install httpx"
                ) from exc
            self._session = httpx.Client(
                base_url=self._api_base,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "quantsdk-python/0.1.0",
                },
                timeout=self._timeout,
            )
        return self._session

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            **kwargs: Additional arguments passed to httpx.

        Returns:
            Parsed JSON response.

        Raises:
            CloudError: On API errors.
        """
        session = self._get_session()
        url = path if path.startswith("http") else f"{self._api_base}/{path.lstrip('/')}"

        try:
            response = session.request(method, url, **kwargs)
        except Exception as e:
            raise CloudError(f"Request failed: {e}") from e

        if response.status_code == 401:
            raise AuthenticationError("Invalid API key", status_code=401)
        if response.status_code == 403:
            raise QuotaExceededError(
                "Usage quota exceeded. Upgrade your plan at thequantcloud.com/pricing",
                status_code=403,
            )
        if response.status_code == 404:
            raise JobNotFoundError(f"Resource not found: {path}", status_code=404)
        if response.status_code >= 400:
            data = (
                response.json()
                if response.headers.get("content-type", "").startswith("application/json")
                else {}
            )
            raise CloudError(
                data.get("error", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                response=data,
            )

        result: dict[str, Any] = response.json()
        return result

    # ─── Circuit Operations ───

    def submit(
        self,
        circuit: Any,
        shots: int = 1024,
        backend: str | None = None,
        *,
        optimize_for: str | None = None,
        max_cost_usd: float | None = None,
        min_fidelity: float | None = None,
        **options: Any,
    ) -> CloudJob:
        """Submit a circuit for execution on TheQuantCloud.

        Args:
            circuit: QuantSDK Circuit to execute.
            shots: Number of measurement repetitions.
            backend: Specific backend, or None for auto-routing.
            optimize_for: Routing optimization target.
            max_cost_usd: Maximum cost constraint.
            min_fidelity: Minimum fidelity constraint.
            **options: Additional execution options.

        Returns:
            CloudJob with the submitted job details.
        """
        # Serialize circuit to OpenQASM for transport
        qasm = circuit.to_openqasm()

        payload: dict[str, Any] = {
            "circuit_qasm": qasm,
            "shots": shots,
            "num_qubits": circuit.num_qubits,
        }
        if backend:
            payload["backend"] = backend
        if optimize_for:
            payload["optimize_for"] = optimize_for
        if max_cost_usd is not None:
            payload["max_cost_usd"] = max_cost_usd
        if min_fidelity is not None:
            payload["min_fidelity"] = min_fidelity
        if options:
            payload["options"] = options

        data = self._request("POST", "/circuits/run", json=payload)

        return CloudJob(
            job_id=data["job_id"],
            status=JobStatus(data.get("status", "submitted")),
            backend=data.get("backend"),
            submitted_at=data.get("submitted_at"),
            circuit_id=data.get("circuit_id"),
            shots=shots,
        )

    def get_job(self, job_id: str) -> CloudJob:
        """Get the current status of a job.

        Args:
            job_id: The job identifier.

        Returns:
            Updated CloudJob with current status.
        """
        data = self._request("GET", f"/jobs/{job_id}")

        return CloudJob(
            job_id=data["job_id"],
            status=JobStatus(data["status"]),
            backend=data.get("backend"),
            submitted_at=data.get("submitted_at"),
            circuit_id=data.get("circuit_id"),
            shots=data.get("shots", 1024),
            metadata=data.get("metadata", {}),
        )

    def get_result(self, job_id: str) -> Any:
        """Get the result of a completed job.

        Args:
            job_id: The job identifier.

        Returns:
            QuantSDK Result object.

        Raises:
            CloudError: If the job is not completed.
        """
        from quantsdk.result import Result

        data = self._request("GET", f"/jobs/{job_id}/result")

        return Result(
            counts=data["counts"],
            shots=data.get("shots", sum(data["counts"].values())),
            backend=data.get("backend", "cloud"),
            job_id=job_id,
            metadata=data.get("metadata", {}),
        )

    def wait_for_result(
        self,
        job_id: str,
        timeout: float = 300.0,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ) -> Any:
        """Wait for a job to complete and return the result.

        Polls the job status at regular intervals until completion or timeout.

        Args:
            job_id: The job identifier.
            timeout: Maximum time to wait in seconds.
            poll_interval: Time between status checks in seconds.

        Returns:
            QuantSDK Result object.

        Raises:
            TimeoutError: If the job doesn't complete within timeout.
            CloudError: If the job fails.
        """
        start = time.monotonic()
        while True:
            job = self.get_job(job_id)

            if job.status == JobStatus.COMPLETED:
                return self.get_result(job_id)

            if job.status in (JobStatus.FAILED, JobStatus.TIMEOUT, JobStatus.CANCELLED):
                raise CloudError(
                    f"Job {job_id} terminated with status: {job.status.value}",
                    response=job.metadata,
                )

            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {timeout}s. "
                    f"Last status: {job.status.value}"
                )

            time.sleep(poll_interval)

    def cancel_job(self, job_id: str) -> CloudJob:
        """Cancel a queued or running job.

        Args:
            job_id: The job identifier.

        Returns:
            Updated CloudJob with cancelled status.
        """
        data = self._request("POST", f"/jobs/{job_id}/cancel")
        return CloudJob(
            job_id=data["job_id"],
            status=JobStatus(data["status"]),
        )

    # ─── Backend Operations ───

    def list_backends(self) -> list[CloudBackendInfo]:
        """List all available backends on TheQuantCloud.

        Returns:
            List of backend information objects.
        """
        data = self._request("GET", "/backends")

        return [
            CloudBackendInfo(
                name=b["name"],
                provider=b["provider"],
                num_qubits=b["num_qubits"],
                status=b.get("status", "online"),
                is_simulator=b.get("is_simulator", False),
                queue_depth=b.get("queue_depth", 0),
                avg_queue_time_sec=b.get("avg_queue_time_sec", 0),
                cost_per_shot=b.get("cost_per_shot", 0),
            )
            for b in data.get("backends", [])
        ]

    def get_backend(self, name: str) -> CloudBackendInfo:
        """Get detailed information about a specific backend.

        Args:
            name: Backend identifier.

        Returns:
            Backend information.
        """
        data = self._request("GET", f"/backends/{name}")

        return CloudBackendInfo(
            name=data["name"],
            provider=data["provider"],
            num_qubits=data["num_qubits"],
            status=data.get("status", "online"),
            is_simulator=data.get("is_simulator", False),
            queue_depth=data.get("queue_depth", 0),
            avg_queue_time_sec=data.get("avg_queue_time_sec", 0),
            cost_per_shot=data.get("cost_per_shot", 0),
        )

    # ─── Usage & Account ───

    def get_usage(self) -> UsageInfo:
        """Get current usage and quota information.

        Returns:
            UsageInfo with current month's usage data.
        """
        data = self._request("GET", "/account/usage")

        return UsageInfo(
            tier=data.get("tier", "explorer"),
            simulator_minutes_used=data.get("simulator_minutes_used", 0),
            simulator_minutes_limit=data.get("simulator_minutes_limit", 60),
            qpu_tasks_used=data.get("qpu_tasks_used", 0),
            qpu_tasks_limit=data.get("qpu_tasks_limit", 10),
            credits_remaining_usd=data.get("credits_remaining_usd", 0),
        )

    # ─── Cleanup ───

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def __enter__(self) -> CloudClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"CloudClient(api_base='{self._api_base}')"
