# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Backend interface — the contract that all quantum backends must implement.

This is the core abstraction that makes QuantSDK framework-agnostic.
Each backend adapter (IBM, IonQ, simulator, etc.) implements this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from quantsdk.circuit import Circuit
    from quantsdk.result import Result


class BackendStatus(Enum):
    """Status of a quantum backend."""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    CALIBRATING = "calibrating"


@dataclass
class BackendInfo:
    """Metadata about a quantum backend.

    Attributes:
        name: Unique backend identifier.
        provider: Provider name (e.g., "ibm", "ionq", "simulator").
        num_qubits: Number of available qubits.
        status: Current operational status.
        is_simulator: Whether this is a simulator (vs real hardware).
        native_gates: Set of natively supported gate names.
        max_shots: Maximum number of shots per job.
        queue_depth: Number of jobs currently queued.
        metadata: Additional backend-specific metadata.
    """

    name: str
    provider: str
    num_qubits: int
    status: BackendStatus = BackendStatus.ONLINE
    is_simulator: bool = False
    native_gates: frozenset[str] = field(default_factory=frozenset)
    max_shots: int = 100_000
    queue_depth: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class Backend(ABC):
    """Abstract base class for all quantum backends.

    Every backend adapter (IBM Quantum, IonQ, GPU simulator, etc.)
    must implement this interface to integrate with QuantSDK.

    Example::

        class MyBackend(Backend):
            def run(self, circuit, shots=1024):
                # Submit circuit and return result
                ...
    """

    @abstractmethod
    def run(self, circuit: Circuit, shots: int = 1024, **options: Any) -> Result:
        """Execute a quantum circuit on this backend.

        Args:
            circuit: The QuantSDK circuit to execute.
            shots: Number of measurement repetitions.
            **options: Backend-specific execution options.

        Returns:
            Result object containing measurement outcomes.
        """
        ...

    @abstractmethod
    def info(self) -> BackendInfo:
        """Get information about this backend.

        Returns:
            BackendInfo with metadata about capabilities and status.
        """
        ...

    @property
    def name(self) -> str:
        """Backend name (convenience property)."""
        return self.info().name

    @property
    def is_simulator(self) -> bool:
        """Whether this backend is a simulator."""
        return self.info().is_simulator
