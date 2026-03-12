# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
IBM Quantum backend adapter — run QuantSDK circuits on IBM hardware.

Requires: pip install quantsdk[ibm]  (qiskit + qiskit-ibm-runtime)

Usage::

    from quantsdk.backends.ibm import IBMBackend

    # Using IBM Quantum Platform (cloud)
    backend = IBMBackend(token="YOUR_IBM_TOKEN")

    # List available backends
    backends = backend.available_backends()

    # Run a circuit
    result = backend.run(circuit, shots=4096)

    # Run on Aer simulator locally (no token required)
    from quantsdk.backends.ibm import AerBackend
    sim = AerBackend()
    result = sim.run(circuit, shots=1024)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from quantsdk.backend import Backend, BackendInfo, BackendStatus
from quantsdk.result import Result

if TYPE_CHECKING:
    from quantsdk.circuit import Circuit

logger = logging.getLogger(__name__)


def _check_ibm_deps() -> None:
    """Raise ImportError if IBM runtime is not installed."""
    try:
        import qiskit  # noqa: F401
        import qiskit_ibm_runtime  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "qiskit and qiskit-ibm-runtime are required for IBM backends. "
            "Install with: pip install quantsdk[ibm]"
        ) from e


def _check_aer() -> None:
    """Raise ImportError if Aer is not installed."""
    try:
        import qiskit_aer  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "qiskit-aer is required for the AerBackend. Install with: pip install quantsdk[ibm]"
        ) from e


class IBMBackend(Backend):
    """Run circuits on IBM Quantum hardware via qiskit-ibm-runtime.

    This adapter converts QuantSDK circuits to Qiskit format, submits them
    to IBM Quantum via the Sampler primitive, and converts results back.

    Args:
        token: IBM Quantum API token. If None, uses saved credentials.
        instance: IBM Quantum instance (e.g., "ibm-q/open/main").
        backend_name: Specific backend to target (e.g., "ibm_brisbane").
            If None, the least-busy backend is selected automatically.
        channel: Channel type — "ibm_quantum" or "ibm_cloud".

    Example::

        from quantsdk.backends.ibm import IBMBackend
        import quantsdk as qs

        backend = IBMBackend(token="YOUR_TOKEN")
        circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
        result = backend.run(circuit, shots=4096)
        print(result.summary())
    """

    def __init__(
        self,
        token: str | None = None,
        instance: str = "ibm-q/open/main",
        backend_name: str | None = None,
        channel: str = "ibm_quantum_platform",
    ) -> None:
        _check_ibm_deps()
        from qiskit_ibm_runtime import QiskitRuntimeService

        self._token = token
        self._instance = instance
        self._channel = channel
        self._backend_name = backend_name

        # Initialize runtime service
        if token is not None:
            self._service = QiskitRuntimeService(
                channel=channel,
                token=token,
                instance=instance,
            )
        else:
            # Use previously saved credentials
            self._service = QiskitRuntimeService(channel=channel)

        # Resolve backend
        if backend_name:
            self._qiskit_backend = self._service.backend(backend_name)
        else:
            self._qiskit_backend = self._service.least_busy(simulator=False, operational=True)
            logger.info("Auto-selected backend: %s", self._qiskit_backend.name)

    def __repr__(self) -> str:
        """Return a string representation with the token masked."""
        masked = "****" + self._token[-4:] if self._token and len(self._token) >= 4 else "****"
        return (
            f"IBMBackend(token='{masked}', "
            f"backend='{self._qiskit_backend.name}', "
            f"instance='{self._instance}')"
        )

    def run(self, circuit: Circuit, shots: int = 4096, **options: Any) -> Result:
        """Execute a circuit on IBM Quantum hardware.

        Uses the Sampler V2 primitive for execution. The circuit is
        automatically transpiled by IBM's runtime.

        Args:
            circuit: QuantSDK circuit to run.
            shots: Number of measurement shots (default 4096).
            **options: Additional options passed to the Sampler.

        Returns:
            QuantSDK Result with measurement counts.
        """
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import SamplerV2 as Sampler

        from quantsdk.interop.qiskit_interop import to_qiskit

        # Convert to Qiskit circuit
        qiskit_circuit = to_qiskit(circuit)

        # Transpile for the target backend
        pm = generate_preset_pass_manager(
            optimization_level=options.get("optimization_level", 1),
            backend=self._qiskit_backend,
        )
        transpiled = pm.run(qiskit_circuit)
        logger.info(
            "Transpiled circuit: depth=%d, gates=%d",
            transpiled.depth(),
            transpiled.size(),
        )

        # Run via Sampler primitive
        sampler = Sampler(backend=self._qiskit_backend)
        job = sampler.run([transpiled], shots=shots)
        logger.info("Job submitted: %s", job.job_id())

        # Wait for result
        primitive_result = job.result()

        # Extract counts from SamplerV2 result
        pub_result = primitive_result[0]
        counts_dict = _extract_counts(pub_result, shots)

        return Result(
            counts=counts_dict,
            shots=shots,
            backend=f"ibm:{self._qiskit_backend.name}",
            job_id=job.job_id(),
            metadata={
                "transpiled_depth": transpiled.depth(),
                "transpiled_gates": transpiled.size(),
                "optimization_level": options.get("optimization_level", 1),
            },
        )

    def info(self) -> BackendInfo:
        """Get info about the IBM Quantum backend."""
        config = self._qiskit_backend.configuration()

        # Map status
        status_map = {
            True: BackendStatus.ONLINE,
            False: BackendStatus.OFFLINE,
        }
        try:
            is_operational = self._qiskit_backend.status().operational
            status = status_map.get(is_operational, BackendStatus.OFFLINE)
        except Exception:
            status = BackendStatus.ONLINE  # Assume online if status check fails

        return BackendInfo(
            name=self._qiskit_backend.name,
            provider="ibm",
            num_qubits=config.n_qubits,
            status=status,
            is_simulator=config.simulator,
            native_gates=frozenset(config.basis_gates),
            max_shots=config.max_shots,
            queue_depth=0,
            metadata={
                "backend_version": config.backend_version,
                "instance": self._instance,
            },
        )

    def available_backends(self, simulator: bool = False) -> list[BackendInfo]:
        """List available IBM Quantum backends.

        Args:
            simulator: If True, include simulators. Default False.

        Returns:
            List of BackendInfo for available backends.
        """
        backends = self._service.backends(simulator=simulator, operational=True)
        result = []
        for b in backends:
            try:
                config = b.configuration()
                result.append(
                    BackendInfo(
                        name=b.name,
                        provider="ibm",
                        num_qubits=config.n_qubits,
                        status=BackendStatus.ONLINE,
                        is_simulator=config.simulator,
                        native_gates=frozenset(config.basis_gates),
                        max_shots=config.max_shots,
                    )
                )
            except Exception:
                logger.warning("Could not get config for backend: %s", b.name)
        return result


def _extract_counts(pub_result: Any, shots: int) -> dict[str, int]:
    """Extract counts dictionary from a SamplerV2 PubResult.

    The Sampler V2 returns results as DataBin with BitArray.
    We convert this to standard {bitstring: count} format.
    """
    data = pub_result.data

    # SamplerV2 returns data as ClassicalRegister → BitArray
    # Try to get the measurement data from any available register
    counts: dict[str, int] = {}

    # Iterate over all classical registers in the data
    for attr_name in dir(data):
        if attr_name.startswith("_"):
            continue
        attr = getattr(data, attr_name)
        if hasattr(attr, "get_counts"):
            raw_counts = attr.get_counts()
            for bitstring, count in raw_counts.items():
                counts[bitstring] = counts.get(bitstring, 0) + count
            return counts

    # Fallback: try .meas attribute (common for measure_all)
    if hasattr(data, "meas"):
        return dict(data.meas.get_counts())

    # Fallback: try first attribute
    for attr_name in dir(data):
        if attr_name.startswith("_"):
            continue
        attr = getattr(data, attr_name)
        if hasattr(attr, "get_bitstrings"):
            bitstrings = attr.get_bitstrings()
            for bs in bitstrings:
                counts[bs] = counts.get(bs, 0) + 1
            return counts

    logger.warning("Could not extract counts from IBM result, returning empty.")
    return counts


class AerBackend(Backend):
    """Run circuits on the local Qiskit Aer simulator.

    This is useful for testing and development without an IBM token.
    Uses the Aer statevector/QASM simulator locally.

    Args:
        method: Simulation method — "automatic", "statevector",
            "density_matrix", "stabilizer", etc. Default "automatic".

    Example::

        from quantsdk.backends.ibm import AerBackend
        import quantsdk as qs

        backend = AerBackend()
        circuit = qs.Circuit(3).h(0).cx(0, 1).cx(1, 2).measure_all()
        result = backend.run(circuit, shots=10000)
        print(result.counts)
    """

    def __init__(self, method: str = "automatic") -> None:
        _check_aer()
        from qiskit_aer import AerSimulator

        self._method = method
        self._simulator = AerSimulator(method=method)

    def run(self, circuit: Circuit, shots: int = 1024, **options: Any) -> Result:
        """Execute a circuit on the local Aer simulator.

        Args:
            circuit: QuantSDK circuit to run.
            shots: Number of shots (default 1024).
            **options: Additional Aer options (seed_simulator, etc.).

        Returns:
            QuantSDK Result with measurement counts.
        """
        from qiskit import transpile

        from quantsdk.interop.qiskit_interop import to_qiskit

        qiskit_circuit = to_qiskit(circuit)

        # Transpile for Aer
        transpiled = transpile(qiskit_circuit, self._simulator)

        # Run
        seed = options.get("seed_simulator", options.get("seed"))
        job = self._simulator.run(transpiled, shots=shots, seed_simulator=seed)
        aer_result = job.result()

        # Extract counts
        raw_counts = aer_result.get_counts()
        # Normalize bitstring format (Aer uses spaces sometimes)
        counts = {}
        for k, v in raw_counts.items():
            clean_key = k.replace(" ", "")
            counts[clean_key] = v

        return Result(
            counts=counts,
            shots=shots,
            backend="aer_simulator",
            job_id=job.job_id(),
            metadata={
                "method": self._method,
                "success": aer_result.success,
            },
        )

    def info(self) -> BackendInfo:
        """Get info about the Aer simulator."""
        return BackendInfo(
            name="aer_simulator",
            provider="ibm",
            num_qubits=30,  # Aer supports up to ~30 qubits locally
            status=BackendStatus.ONLINE,
            is_simulator=True,
            native_gates=frozenset({"cx", "id", "rz", "sx", "x"}),
            max_shots=1_000_000,
            queue_depth=0,
            metadata={"method": self._method},
        )
