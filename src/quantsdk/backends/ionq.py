# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
IonQ backend adapter -- run QuantSDK circuits on IonQ trapped-ion hardware.

Access IonQ via Amazon Braket SDK.  Requires: pip install quantsdk[ionq]

Usage::

    from quantsdk.backends.ionq import IonQBackend

    # Using IonQ Harmony simulator (free on Braket)
    backend = IonQBackend(device="simulator")

    # Using IonQ Harmony QPU
    backend = IonQBackend(device="harmony")

    # Using IonQ Aria QPU
    backend = IonQBackend(device="aria")

    # Run a circuit
    result = backend.run(circuit, shots=1000)
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Any

import numpy as np

from quantsdk.backend import Backend, BackendInfo, BackendStatus
from quantsdk.result import Result

if TYPE_CHECKING:
    from quantsdk.circuit import Circuit

logger = logging.getLogger(__name__)

# ─── IonQ device ARN mapping ───

_IONQ_DEVICE_ARNS: dict[str, str] = {
    "simulator": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    "ionq_simulator": "arn:aws:braket:us-east-1::device/qpu/ionq/simulator",
    "harmony": "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony",
    "aria": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
    "aria2": "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-2",
    "forte": "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1",
}

# IonQ native gate set (GPI, GPI2, MS)
_IONQ_NATIVE_GATES: frozenset[str] = frozenset(
    {
        "gpi",
        "gpi2",
        "ms",
        "x",
        "y",
        "z",
        "h",
        "cx",
        "s",
        "t",
        "rx",
        "ry",
        "rz",
    }
)


def _check_braket() -> None:
    """Raise ImportError if Amazon Braket SDK is not installed."""
    try:
        import braket  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Amazon Braket SDK is required for IonQ backends. "
            "Install it with: pip install quantsdk[ionq]"
        ) from e


def _resolve_device_arn(device: str) -> str:
    """Resolve a device shortname or full ARN to a Braket device ARN.

    Args:
        device: Either a shortname (e.g. "harmony", "simulator") or full ARN.

    Returns:
        Full Braket device ARN.

    Raises:
        ValueError: If shortname is not recognized and doesn't look like an ARN.
    """
    if device in _IONQ_DEVICE_ARNS:
        return _IONQ_DEVICE_ARNS[device]
    if device.startswith("arn:aws:braket"):
        return device
    available = ", ".join(sorted(_IONQ_DEVICE_ARNS.keys()))
    raise ValueError(
        f"Unknown IonQ device: '{device}'. "
        f"Available shortnames: {available}. "
        f"Or provide a full Braket device ARN."
    )


def _get_aws_device(arn: str) -> Any:
    """Create an AwsDevice instance (isolated for test mocking)."""
    from braket.aws import AwsDevice

    return AwsDevice(arn)


class IonQBackend(Backend):
    """Run circuits on IonQ trapped-ion hardware via Amazon Braket.

    This adapter converts QuantSDK circuits to Amazon Braket format,
    submits them to IonQ devices, and converts results back.

    IonQ devices use trapped-ion qubits with all-to-all connectivity,
    meaning any qubit can interact with any other qubit without SWAP
    gates.  This makes IonQ ideal for circuits with high connectivity
    requirements.

    Args:
        device: Device shortname or full Braket ARN.
            Shortnames: "simulator", "harmony", "aria", "aria2", "forte".
        s3_bucket: S3 bucket for Braket task results.
            Format: ``("bucket-name", "prefix")``.
            If None, uses Braket's default bucket.
        region: AWS region (default: "us-east-1").

    Example::

        from quantsdk.backends.ionq import IonQBackend
        import quantsdk as qs

        backend = IonQBackend(device="simulator")
        circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
        result = backend.run(circuit, shots=1000)
        print(result.counts)
    """

    def __init__(
        self,
        device: str = "simulator",
        s3_bucket: tuple[str, str] | None = None,
        region: str = "us-east-1",
    ) -> None:
        _check_braket()

        self._device_name = device
        self._device_arn = _resolve_device_arn(device)
        self._s3_bucket = s3_bucket
        self._region = region

        # Initialize the Braket device (lazy import for mockability)
        self._device = _get_aws_device(self._device_arn)
        logger.info("IonQ backend initialized: %s (%s)", device, self._device_arn)

    def __repr__(self) -> str:
        return (
            f"IonQBackend(device='{self._device_name}', "
            f"arn='{self._device_arn}', "
            f"region='{self._region}')"
        )

    def run(self, circuit: Circuit, shots: int = 1000, **options: Any) -> Result:
        """Execute a circuit on an IonQ device via Amazon Braket.

        The circuit is converted to a Braket circuit, submitted to the IonQ
        device, and results are returned after the task completes.

        Args:
            circuit: QuantSDK circuit to run.
            shots: Number of measurement shots (default 1000).
            **options: Additional options:
                - poll_interval_seconds (float): Polling interval (default 1.0).
                - disable_qubit_rewiring (bool): Keep qubit mapping (default False).

        Returns:
            QuantSDK Result with measurement counts.
        """
        braket_circuit = _to_braket_circuit(circuit)

        # Submit task
        task_kwargs: dict[str, Any] = {"shots": shots}
        if self._s3_bucket is not None:
            task_kwargs["s3_destination_folder"] = self._s3_bucket
        if options.get("disable_qubit_rewiring"):
            task_kwargs["disable_qubit_rewiring"] = True

        task = self._device.run(braket_circuit, **task_kwargs)
        logger.info("IonQ task submitted: %s", task.id)

        # Wait for result
        braket_result = task.result()
        counts = braket_result.measurement_counts

        # Normalize: Braket returns Counter-like obj -> convert to dict[str, int]
        counts_dict: dict[str, int] = {}
        for bitstring, count in counts.items():
            counts_dict[str(bitstring)] = int(count)

        return Result(
            counts=counts_dict,
            shots=shots,
            backend=f"ionq:{self._device_name}",
            job_id=task.id,
            metadata={
                "device_arn": self._device_arn,
                "region": self._region,
                "task_status": str(task.state()),
            },
        )

    def info(self) -> BackendInfo:
        """Get information about the IonQ device."""
        try:
            properties = self._device.properties
            num_qubits = getattr(properties, "paradigm", None)
            qubit_count = num_qubits.qubitCount if num_qubits is not None else 11
        except Exception:
            qubit_count = 11  # Default for IonQ Harmony

        is_sim = "simulator" in self._device_name.lower() or "sv1" in self._device_arn

        try:
            status_str = self._device.status
            if status_str == "ONLINE":
                status = BackendStatus.ONLINE
            elif status_str == "OFFLINE":
                status = BackendStatus.OFFLINE
            else:
                status = BackendStatus.MAINTENANCE
        except Exception:
            status = BackendStatus.ONLINE

        return BackendInfo(
            name=f"ionq_{self._device_name}",
            provider="ionq",
            num_qubits=qubit_count,
            status=status,
            is_simulator=is_sim,
            native_gates=_IONQ_NATIVE_GATES,
            max_shots=10_000,
            queue_depth=0,
            metadata={
                "device_arn": self._device_arn,
                "region": self._region,
                "connectivity": "all-to-all",
            },
        )


# ─── Circuit Conversion ───


def _to_braket_circuit(circuit: Circuit) -> Any:
    """Convert a QuantSDK circuit to an Amazon Braket Circuit.

    Maps QuantSDK gates to their Braket equivalents.
    IonQ has all-to-all connectivity, so no routing/SWAP insertion needed.
    """
    from braket.circuits import Circuit as BraketCircuit

    from quantsdk.gates import (
        Barrier,
        CCZGate,
        CHGate,
        CPhaseGate,
        CRXGate,
        CRYGate,
        CRZGate,
        CXGate,
        CYGate,
        CZGate,
        FredkinGate,
        HGate,
        IGate,
        Measure,
        PhaseGate,
        RXGate,
        RYGate,
        RZGate,
        RZZGate,
        SdgGate,
        SGate,
        SwapGate,
        SXGate,
        TGate,
        ToffoliGate,
        U3Gate,
        XGate,
        YGate,
        ZGate,
        iSwapGate,
    )

    bc = BraketCircuit()

    for gate in circuit.gates:
        q = gate.qubits

        # Skip barriers and measurements (Braket measures all at end)
        if isinstance(gate, (Barrier, Measure)):
            continue

        # ── Single-qubit non-parametric ──
        if isinstance(gate, HGate):
            bc.h(q[0])
        elif isinstance(gate, XGate):
            bc.x(q[0])
        elif isinstance(gate, YGate):
            bc.y(q[0])
        elif isinstance(gate, ZGate):
            bc.z(q[0])
        elif isinstance(gate, SGate):
            bc.s(q[0])
        elif isinstance(gate, SdgGate):
            bc.si(q[0])
        elif isinstance(gate, TGate):
            bc.t(q[0])
        elif isinstance(gate, IGate):
            bc.i(q[0])
        elif isinstance(gate, SXGate):
            bc.v(q[0])

        # ── Single-qubit parametric ──
        elif isinstance(gate, RXGate):
            bc.rx(q[0], gate.params[0])
        elif isinstance(gate, RYGate):
            bc.ry(q[0], gate.params[0])
        elif isinstance(gate, RZGate):
            bc.rz(q[0], gate.params[0])
        elif isinstance(gate, PhaseGate):
            bc.phaseshift(q[0], gate.params[0])
        elif isinstance(gate, U3Gate):
            # Decompose U3 to Rz-Ry-Rz
            theta, phi, lam = gate.params
            bc.rz(q[0], lam)
            bc.ry(q[0], theta)
            bc.rz(q[0], phi)

        # ── Two-qubit non-parametric ──
        elif isinstance(gate, CXGate):
            bc.cnot(q[0], q[1])
        elif isinstance(gate, CZGate):
            bc.cz(q[0], q[1])
        elif isinstance(gate, CYGate):
            bc.cy(q[0], q[1])
        elif isinstance(gate, CHGate):
            # Braket doesn't have native CH -- use Unitary
            bc.unitary(matrix=_ch_matrix(), targets=[q[0], q[1]])
        elif isinstance(gate, SwapGate):
            bc.swap(q[0], q[1])
        elif isinstance(gate, iSwapGate):
            bc.iswap(q[0], q[1])

        # ── Controlled parametric ──
        elif isinstance(gate, CPhaseGate):
            bc.cphaseshift(q[0], q[1], gate.params[0])
        elif isinstance(gate, CRXGate):
            # Braket has no native CRX — use Unitary matrix
            bc.unitary(matrix=_crx_matrix(gate.params[0]), targets=[q[0], q[1]])
        elif isinstance(gate, CRYGate):
            bc.unitary(matrix=_cry_matrix(gate.params[0]), targets=[q[0], q[1]])
        elif isinstance(gate, CRZGate):
            bc.unitary(matrix=_crz_matrix(gate.params[0]), targets=[q[0], q[1]])

        # ── Two-qubit rotation ──
        elif isinstance(gate, RZZGate):
            bc.zz(q[0], q[1], gate.params[0])

        # ── Three-qubit ──
        elif isinstance(gate, ToffoliGate):
            bc.ccnot(q[0], q[1], q[2])
        elif isinstance(gate, FredkinGate):
            bc.cswap(q[0], q[1], q[2])
        elif isinstance(gate, CCZGate):
            # CCZ = H(t) CCX(c1,c2,t) H(t)
            bc.h(q[2])
            bc.ccnot(q[0], q[1], q[2])
            bc.h(q[2])

        else:
            raise ValueError(f"Unsupported gate for IonQ/Braket: {gate.name}")

    return bc


# ─── Controlled-rotation unitary matrices ───


def _crx_matrix(theta: float) -> np.ndarray:
    """4x4 unitary for CRX(theta): control q0, target q1."""
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, c, -1j * s],
            [0, 0, -1j * s, c],
        ],
        dtype=complex,
    )


def _cry_matrix(theta: float) -> np.ndarray:
    """4x4 unitary for CRY(theta): control q0, target q1."""
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, c, -s],
            [0, 0, s, c],
        ],
        dtype=complex,
    )


def _crz_matrix(lam: float) -> np.ndarray:
    """4x4 unitary for CRZ(lambda): control q0, target q1."""
    return np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, np.exp(-1j * lam / 2), 0],
            [0, 0, 0, np.exp(1j * lam / 2)],
        ],
        dtype=complex,
    )


def _ch_matrix() -> np.ndarray:
    """4x4 unitary for Controlled-Hadamard: control q0, target q1."""
    r = 1.0 / math.sqrt(2)
    return np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, r, r],
            [0, 0, r, -r],
        ],
        dtype=complex,
    )


# ─── Braket Local Simulator Backend ───


class BraketLocalBackend(Backend):
    """Run circuits on Braket's local state-vector simulator.

    Uses the ``amazon-braket-default-simulator`` which requires no AWS
    credentials.  Ideal for development, testing, and CI.

    Args:
        backend_name: Simulator backend (default "default").
            Options: "default" (state vector), "braket_dm" (density matrix).

    Example::

        from quantsdk.backends.ionq import BraketLocalBackend

        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=1000)
    """

    def __init__(self, backend_name: str = "default") -> None:
        _check_braket()
        from braket.devices import LocalSimulator

        self._backend_name = backend_name
        self._device = LocalSimulator(backend=backend_name)
        logger.info("Braket local simulator initialized: %s", backend_name)

    def __repr__(self) -> str:
        return f"BraketLocalBackend(backend='{self._backend_name}')"

    def run(self, circuit: Circuit, shots: int = 1000, **options: Any) -> Result:
        """Execute a circuit on the Braket local simulator.

        Args:
            circuit: QuantSDK circuit to run.
            shots: Number of measurement shots (default 1000).
            **options: Currently unused.

        Returns:
            QuantSDK Result with measurement counts.
        """
        braket_circuit = _to_braket_circuit(circuit)
        braket_result = self._device.run(braket_circuit, shots=shots).result()
        counts = braket_result.measurement_counts

        counts_dict: dict[str, int] = {}
        for bitstring, count in counts.items():
            counts_dict[str(bitstring)] = int(count)

        return Result(
            counts=counts_dict,
            shots=shots,
            backend=f"braket_local:{self._backend_name}",
            job_id="local",
            metadata={"backend": self._backend_name},
        )

    def info(self) -> BackendInfo:
        """Get information about the Braket local simulator."""
        return BackendInfo(
            name=f"braket_local_{self._backend_name}",
            provider="amazon",
            num_qubits=25,
            status=BackendStatus.ONLINE,
            is_simulator=True,
            native_gates=_IONQ_NATIVE_GATES,
            max_shots=100_000,
            queue_depth=0,
            metadata={"backend": self._backend_name},
        )
