# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
GPU-accelerated quantum simulator backend.

Wraps Qiskit Aer's GPU-accelerated simulation methods, with automatic
fallback to CPU methods when GPU is unavailable.  Supports higher qubit
counts (30+ on GPU, 25 on CPU) compared to the pure-NumPy ``LocalSimulator``.

Requires: ``pip install qiskit-aer`` (CPU) or ``pip install qiskit-aer-gpu``
(NVIDIA GPU).

Usage::

    from quantsdk.simulators.gpu import GPUSimulator

    sim = GPUSimulator()               # auto-detect GPU
    sim = GPUSimulator(method="auto")   # same as above
    sim = GPUSimulator(method="gpu")    # force GPU (fail if unavailable)
    sim = GPUSimulator(method="cpu")    # force CPU

    result = sim.run(circuit, shots=1000)
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

from quantsdk.backend import Backend, BackendInfo, BackendStatus
from quantsdk.result import Result

if TYPE_CHECKING:
    from quantsdk.circuit import Circuit

logger = logging.getLogger(__name__)

# ─── GPU detection ───

_GPU_METHODS = frozenset(
    {
        "statevector_gpu",
        "density_matrix_gpu",
        "unitary_gpu",
    }
)

_CPU_SV_METHODS = frozenset(
    {
        "statevector",
        "density_matrix",
        "matrix_product_state",
        "automatic",
    }
)


def _check_aer() -> None:
    """Raise ImportError if Qiskit Aer is not installed."""
    try:
        import qiskit_aer  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Qiskit Aer is required for the GPU/accelerated simulator. "
            "Install it with: pip install qiskit-aer (CPU) or "
            "pip install qiskit-aer-gpu (GPU)"
        ) from e


def _detect_gpu() -> bool:
    """Check if GPU simulation methods are available in Aer.

    Returns:
        True if at least one GPU method is available.
    """
    try:
        from qiskit_aer import AerSimulator

        available = set(AerSimulator().available_methods())
        return bool(available & _GPU_METHODS)
    except Exception:
        return False


def _best_method(force: str = "auto") -> str:
    """Select the best available simulation method.

    Args:
        force: "auto" (detect), "gpu" (force GPU), or "cpu" (force CPU).

    Returns:
        The Aer method string to use.

    Raises:
        RuntimeError: If "gpu" is forced but no GPU is available.
    """
    if force == "cpu":
        return "automatic"

    if force == "gpu":
        if _detect_gpu():
            return "statevector_gpu"
        raise RuntimeError(
            "GPU simulation requested but no GPU methods available. "
            "Install qiskit-aer-gpu with NVIDIA CUDA drivers, or "
            "use method='auto' for automatic fallback."
        )

    # Auto-detect
    if _detect_gpu():
        return "statevector_gpu"
    return "automatic"


class GPUSimulator(Backend):
    """GPU-accelerated quantum circuit simulator.

    Uses Qiskit Aer as the simulation engine with automatic GPU detection.
    When an NVIDIA GPU is available (via ``qiskit-aer-gpu``), enables
    GPU-accelerated statevector simulation supporting 30+ qubits.  Falls
    back to CPU-based simulation (25 qubits) otherwise.

    The simulator also supports configurable noise models via
    Qiskit Aer's noise framework.

    Args:
        method: Simulation method selection.
            ``"auto"`` — detect GPU, fall back to CPU (default).
            ``"gpu"`` — force GPU (raises RuntimeError if unavailable).
            ``"cpu"`` — force CPU simulation.
        max_qubits: Maximum qubit limit (default: 30 for GPU, 25 for CPU).
        noise_model: Optional Qiskit Aer NoiseModel for noisy simulation.

    Example::

        from quantsdk.simulators.gpu import GPUSimulator

        # Auto-detect best backend
        sim = GPUSimulator()
        result = sim.run(circuit, shots=1000)
        print(result.counts)
        print(sim.info())  # shows whether GPU is active

    Raises:
        ImportError: If ``qiskit-aer`` is not installed.
        RuntimeError: If ``method="gpu"`` but no GPU is available.
    """

    def __init__(
        self,
        method: str = "auto",
        max_qubits: int | None = None,
        noise_model: Any = None,
    ) -> None:
        _check_aer()

        self._requested_method = method
        self._aer_method = _best_method(method)
        self._is_gpu = self._aer_method in _GPU_METHODS
        self._noise_model = noise_model

        # Set qubit limits based on backend
        if max_qubits is not None:
            self._max_qubits = max_qubits
        elif self._is_gpu:
            self._max_qubits = 30
        else:
            self._max_qubits = 25

        logger.info(
            "GPU simulator initialized: method=%s, gpu=%s, max_qubits=%d",
            self._aer_method,
            self._is_gpu,
            self._max_qubits,
        )

    def __repr__(self) -> str:
        return (
            f"GPUSimulator(method='{self._aer_method}', "
            f"gpu={self._is_gpu}, "
            f"max_qubits={self._max_qubits})"
        )

    @property
    def is_gpu(self) -> bool:
        """Whether GPU acceleration is active."""
        return self._is_gpu

    @property
    def method(self) -> str:
        """Active Aer simulation method."""
        return self._aer_method

    def run(self, circuit: Circuit, shots: int = 1024, **options: Any) -> Result:
        """Execute a circuit on the accelerated simulator.

        Args:
            circuit: QuantSDK circuit to simulate.
            shots: Number of measurement shots (default 1024).
            **options:
                seed (int): Random seed for reproducibility.
                optimization_level (int): Qiskit transpiler level (0-3).

        Returns:
            QuantSDK Result with measurement counts.

        Raises:
            ValueError: If circuit exceeds max_qubits.
        """
        from qiskit import transpile
        from qiskit_aer import AerSimulator

        n = circuit.num_qubits
        if n > self._max_qubits:
            raise ValueError(
                f"Circuit has {n} qubits, but this simulator supports at most "
                f"{self._max_qubits}. {'Try a cloud backend.' if self._is_gpu else 'Try installing qiskit-aer-gpu for GPU acceleration.'}"
            )

        # Convert to Qiskit circuit
        from quantsdk.interop.qiskit_interop import to_qiskit

        qc = to_qiskit(circuit)

        # Create Aer simulator with selected method
        sim_kwargs: dict[str, Any] = {"method": self._aer_method}
        if self._noise_model is not None:
            sim_kwargs["noise_model"] = self._noise_model
        backend = AerSimulator(**sim_kwargs)

        # Transpile
        opt_level = options.get("optimization_level", 1)
        seed = options.get("seed")
        transpiled = transpile(qc, backend=backend, optimization_level=opt_level)

        # Run
        run_kwargs: dict[str, Any] = {"shots": shots}
        if seed is not None:
            run_kwargs["seed_simulator"] = seed
        job = backend.run(transpiled, **run_kwargs)
        result = job.result()

        # Extract counts
        raw_counts = result.get_counts()
        counts: dict[str, int] = {}
        for bitstring, count in raw_counts.items():
            # Qiskit returns reversed bitstrings — reverse them
            clean = bitstring.replace(" ", "")
            counts[clean[::-1]] = int(count)

        return Result(
            counts=counts,
            shots=shots,
            backend=f"gpu_simulator:{self._aer_method}",
            job_id=f"gpu-{uuid.uuid4().hex[:12]}",
            metadata={
                "method": self._aer_method,
                "is_gpu": self._is_gpu,
                "num_qubits": n,
                "circuit_depth": circuit.depth,
                "seed": seed,
                "noise_model": self._noise_model is not None,
                "success": result.success,
            },
        )

    def info(self) -> BackendInfo:
        """Get information about the GPU simulator."""
        return BackendInfo(
            name=f"gpu_simulator_{self._aer_method}",
            provider="quantsdk",
            num_qubits=self._max_qubits,
            status=BackendStatus.ONLINE,
            is_simulator=True,
            native_gates=frozenset(
                {
                    "h",
                    "x",
                    "y",
                    "z",
                    "s",
                    "sdg",
                    "t",
                    "tdg",
                    "rx",
                    "ry",
                    "rz",
                    "u3",
                    "cx",
                    "cz",
                    "swap",
                    "ccx",
                    "measure",
                    "reset",
                }
            ),
            max_shots=1_000_000,
            queue_depth=0,
            metadata={
                "method": self._aer_method,
                "is_gpu": self._is_gpu,
                "requested_method": self._requested_method,
                "noise_model": self._noise_model is not None,
            },
        )
