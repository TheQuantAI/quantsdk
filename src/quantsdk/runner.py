# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Top-level runner — the `qs.run()` function.

Provides the simplest possible API for executing quantum circuits.
Automatically selects a backend if none is specified.
"""

from __future__ import annotations

from typing import Any

from quantsdk.circuit import Circuit
from quantsdk.result import Result
from quantsdk.simulators.local import LocalSimulator


# Default backend instance (lazy singleton)
_default_simulator: LocalSimulator | None = None


def _get_default_simulator() -> LocalSimulator:
    """Get or create the default local simulator."""
    global _default_simulator
    if _default_simulator is None:
        _default_simulator = LocalSimulator()
    return _default_simulator


def run(
    circuit: Circuit,
    shots: int = 1024,
    backend: str | None = None,
    *,
    optimize_for: str | None = None,
    max_cost_usd: float | None = None,
    min_fidelity: float | None = None,
    seed: int | None = None,
    **options: Any,
) -> Result:
    """Execute a quantum circuit.

    This is the main entry point for running circuits. By default, runs on
    the local simulator. Specify a backend name or optimization constraints
    to use cloud backends (requires TheQuantCloud account).

    Args:
        circuit: The quantum circuit to execute.
        shots: Number of measurement repetitions (default: 1024).
        backend: Backend name (e.g., "ibm_brisbane", "ionq_harmony").
                 If None, uses local simulator.
        optimize_for: Optimization target — "quality", "speed", or "cost".
                      Enables QuantRouter smart routing (cloud only).
        max_cost_usd: Maximum cost in USD (cloud only).
        min_fidelity: Minimum acceptable fidelity (cloud only).
        seed: Random seed for reproducible results (simulator only).
        **options: Additional backend-specific options.

    Returns:
        Result object containing measurement counts and metadata.

    Example::

        import quantsdk as qs

        circuit = qs.Circuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        # Run on local simulator (default)
        result = qs.run(circuit, shots=1000)
        print(result.counts)  # {'00': 503, '11': 497}

        # Run on specific backend (requires cloud account)
        result = qs.run(circuit, backend="ibm_brisbane", shots=1000)

        # Smart routing (requires cloud account)
        result = qs.run(circuit, optimize_for="quality", shots=1000)
    """
    # For now (v0.1), only local simulator is supported.
    # Cloud backends and QuantRouter will be added in v0.2+.

    if backend is not None and backend != "local_simulator":
        raise NotImplementedError(
            f"Backend '{backend}' is not available in QuantSDK v0.1 (local mode). "
            f"Cloud backends will be available in v0.2. "
            f"For now, use backend=None for the local simulator."
        )

    if optimize_for is not None:
        raise NotImplementedError(
            "Smart routing (optimize_for) requires TheQuantCloud. "
            "Coming in v0.2. For now, circuits run on the local simulator."
        )

    simulator = _get_default_simulator()
    return simulator.run(circuit, shots=shots, seed=seed, **options)
