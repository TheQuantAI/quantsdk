# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Top-level runner — the `qs.run()` function.

Provides the simplest possible API for executing quantum circuits.
Automatically selects a backend if none is specified.
"""

from __future__ import annotations

import logging
from typing import Any

from quantsdk.circuit import Circuit
from quantsdk.result import Result
from quantsdk.simulators.local import LocalSimulator

logger = logging.getLogger(__name__)

# Default backend instance (lazy singleton)
_default_simulator: LocalSimulator | None = None

# Known backend aliases for quick resolution
_BACKEND_ALIASES: dict[str, str] = {
    "local": "local_simulator",
    "local_simulator": "local_simulator",
    "simulator": "local_simulator",
    "aer": "aer_simulator",
    "aer_simulator": "aer_simulator",
    "qasm_simulator": "aer_simulator",
}


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
        backend: Backend name. Options:

            - ``None`` or ``"local_simulator"`` — Pure NumPy local simulator (default)
            - ``"aer"`` or ``"aer_simulator"`` — Qiskit Aer simulator (requires qiskit-aer)
            - ``"ibm_<name>"`` — IBM Quantum hardware (requires token + qiskit-ibm-runtime)

        optimize_for: Optimization target — "quality", "speed", or "cost".
                      Enables QuantRouter smart routing.
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

        # Run on Aer simulator
        result = qs.run(circuit, backend="aer", shots=1000)

        # Run on IBM Quantum hardware
        result = qs.run(circuit, backend="ibm_brisbane", shots=4096)

        # Smart routing via QuantRouter
        result = qs.run(circuit, optimize_for="quality", shots=1000)
    """
    if optimize_for is not None:
        from quantsdk.router import QuantRouter, RoutingConstraints

        router = QuantRouter()
        constraints = RoutingConstraints(
            optimize_for=optimize_for,
            max_cost_usd=max_cost_usd,
            min_fidelity=min_fidelity,
        )
        decision = router.route(circuit, constraints=constraints)
        logger.info("QuantRouter selected '%s': %s", decision.backend, decision.reason)

        # Re-invoke run() with the selected backend (no optimize_for to avoid recursion)
        return run(circuit, shots=shots, backend=decision.backend, seed=seed, **options)

    # Resolve backend name
    resolved = _BACKEND_ALIASES.get(backend or "local_simulator", backend or "local_simulator")

    # ─── Local simulator (default, no dependencies) ───
    if resolved == "local_simulator":
        simulator = _get_default_simulator()
        return simulator.run(circuit, shots=shots, seed=seed, **options)

    # ─── Aer simulator (requires qiskit-aer) ───
    if resolved == "aer_simulator":
        try:
            from quantsdk.backends.ibm import AerBackend
        except ImportError as e:
            raise ImportError(
                "Aer backend requires qiskit-aer. Install with: pip install quantsdk[ibm]"
            ) from e
        aer = AerBackend(method=options.pop("method", "automatic"))
        return aer.run(circuit, shots=shots, seed=seed, **options)

    # ─── IBM Quantum hardware (requires qiskit-ibm-runtime) ───
    if resolved.startswith("ibm_") or resolved.startswith("ibm-"):
        try:
            from quantsdk.backends.ibm import IBMBackend
        except ImportError as e:
            raise ImportError(
                "IBM backend requires qiskit and qiskit-ibm-runtime. "
                "Install with: pip install quantsdk[ibm]"
            ) from e
        token = options.pop("token", None)
        instance = options.pop("instance", "ibm-q/open/main")
        channel = options.pop("channel", "ibm_quantum_platform")
        ibm_backend = IBMBackend(
            token=token,
            instance=instance,
            backend_name=resolved,
            channel=channel,
        )
        return ibm_backend.run(circuit, shots=shots, **options)

    raise ValueError(
        f"Unknown backend: '{backend}'. "
        f"Available: 'local_simulator' (default), 'aer', or 'ibm_<backend_name>'. "
        f"QuantRouter smart routing coming in v0.2."
    )
