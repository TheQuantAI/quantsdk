# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Qiskit interop — convert between QuantSDK circuits and Qiskit QuantumCircuits.

Requires: pip install quantsdk[ibm]  (or pip install qiskit)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from quantsdk.circuit import Circuit
from quantsdk.gates import (
    Barrier,
    CXGate,
    CZGate,
    FredkinGate,
    HGate,
    IGate,
    Measure,
    RXGate,
    RYGate,
    RZGate,
    RZZGate,
    SGate,
    SwapGate,
    TGate,
    ToffoliGate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
)

if TYPE_CHECKING:
    from qiskit.circuit import QuantumCircuit as QiskitCircuit


def _check_qiskit() -> None:
    """Raise ImportError if qiskit is not installed."""
    try:
        import qiskit  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Qiskit is required for Qiskit interop. "
            "Install it with: pip install quantsdk[ibm]"
        ) from e


def to_qiskit(circuit: Circuit) -> QiskitCircuit:
    """Convert a QuantSDK Circuit to a Qiskit QuantumCircuit.

    Args:
        circuit: The QuantSDK circuit to convert.

    Returns:
        A Qiskit QuantumCircuit equivalent.

    Raises:
        ImportError: If qiskit is not installed.

    Example::

        import quantsdk as qs
        from quantsdk.interop import to_qiskit

        circuit = qs.Circuit(2)
        circuit.h(0).cx(0, 1).measure_all()

        qiskit_circuit = to_qiskit(circuit)
        print(qiskit_circuit)
    """
    _check_qiskit()
    from qiskit.circuit import QuantumCircuit as QiskitQC

    # Count measurements to determine if we need classical bits
    num_measurements = circuit.num_measurements
    if num_measurements > 0:
        qc = QiskitQC(circuit.num_qubits, num_measurements)
    else:
        qc = QiskitQC(circuit.num_qubits)
    qc.name = circuit.name

    clbit_index = 0  # Track classical bit allocation

    for gate in circuit.gates:
        if isinstance(gate, Measure):
            qubit = gate.qubits[0]
            qc.measure(qubit, clbit_index)
            clbit_index += 1

        elif isinstance(gate, Barrier):
            qc.barrier(*gate.qubits)

        elif isinstance(gate, HGate):
            qc.h(gate.qubits[0])

        elif isinstance(gate, XGate):
            qc.x(gate.qubits[0])

        elif isinstance(gate, YGate):
            qc.y(gate.qubits[0])

        elif isinstance(gate, ZGate):
            qc.z(gate.qubits[0])

        elif isinstance(gate, SGate):
            qc.s(gate.qubits[0])

        elif isinstance(gate, TGate):
            qc.t(gate.qubits[0])

        elif isinstance(gate, IGate):
            qc.id(gate.qubits[0])

        elif isinstance(gate, RXGate):
            qc.rx(gate.params[0], gate.qubits[0])

        elif isinstance(gate, RYGate):
            qc.ry(gate.params[0], gate.qubits[0])

        elif isinstance(gate, RZGate):
            qc.rz(gate.params[0], gate.qubits[0])

        elif isinstance(gate, U3Gate):
            qc.u(gate.params[0], gate.params[1], gate.params[2], gate.qubits[0])

        elif isinstance(gate, CXGate):
            qc.cx(gate.qubits[0], gate.qubits[1])

        elif isinstance(gate, CZGate):
            qc.cz(gate.qubits[0], gate.qubits[1])

        elif isinstance(gate, SwapGate):
            qc.swap(gate.qubits[0], gate.qubits[1])

        elif isinstance(gate, RZZGate):
            qc.rzz(gate.params[0], gate.qubits[0], gate.qubits[1])

        elif isinstance(gate, ToffoliGate):
            qc.ccx(gate.qubits[0], gate.qubits[1], gate.qubits[2])

        elif isinstance(gate, FredkinGate):
            qc.cswap(gate.qubits[0], gate.qubits[1], gate.qubits[2])

        else:
            raise ValueError(f"Unsupported gate for Qiskit export: {gate.name}")

    return qc


# ─── Qiskit gate name → QuantSDK gate builder mapping ───

_QISKIT_GATE_MAP: dict[str, type | None] = {
    "h": HGate,
    "x": XGate,
    "y": YGate,
    "z": ZGate,
    "s": SGate,
    "t": TGate,
    "id": IGate,
    "rx": RXGate,
    "ry": RYGate,
    "rz": RZGate,
    "u": U3Gate,
    "cx": CXGate,
    "cz": CZGate,
    "swap": SwapGate,
    "rzz": RZZGate,
    "ccx": ToffoliGate,
    "cswap": FredkinGate,
}


def from_qiskit(qiskit_circuit: QiskitCircuit) -> Circuit:
    """Convert a Qiskit QuantumCircuit to a QuantSDK Circuit.

    Args:
        qiskit_circuit: The Qiskit circuit to convert.

    Returns:
        A QuantSDK Circuit equivalent.

    Raises:
        ImportError: If qiskit is not installed.
        ValueError: If the Qiskit circuit contains unsupported gates.

    Example::

        from qiskit.circuit import QuantumCircuit
        from quantsdk.interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()

        circuit = from_qiskit(qc)
        print(circuit.draw())
    """
    _check_qiskit()
    from qiskit.circuit import Measure as QiskitMeasure

    circuit = Circuit(qiskit_circuit.num_qubits, name=qiskit_circuit.name)

    for instruction in qiskit_circuit.data:
        op = instruction.operation
        qubits = [qiskit_circuit.find_bit(q).index for q in instruction.qubits]
        params = list(op.params)
        gate_name = op.name.lower()

        # Handle measurement
        if isinstance(op, QiskitMeasure) or gate_name == "measure":
            circuit.measure(qubits[0])
            continue

        # Handle barrier
        if gate_name == "barrier":
            circuit.barrier(qubits)
            continue

        # Lookup in gate map
        gate_class = _QISKIT_GATE_MAP.get(gate_name)
        if gate_class is None:
            raise ValueError(
                f"Unsupported Qiskit gate for QuantSDK import: '{op.name}'. "
                f"Supported gates: {sorted(_QISKIT_GATE_MAP.keys())}"
            )

        # Build the QuantSDK gate with appropriate arguments
        if gate_class in (HGate, XGate, YGate, ZGate, SGate, TGate, IGate):
            # Single-qubit, no params
            circuit._gates.append(gate_class(qubits[0]))

        elif gate_class in (RXGate, RYGate, RZGate):
            # Single-qubit, one param
            circuit._gates.append(gate_class(qubits[0], float(params[0])))

        elif gate_class is U3Gate:
            # Single-qubit, three params
            circuit._gates.append(
                U3Gate(qubits[0], float(params[0]), float(params[1]), float(params[2]))
            )

        elif gate_class in (CXGate, CZGate, SwapGate):
            # Two-qubit, no params
            circuit._gates.append(gate_class(qubits[0], qubits[1]))

        elif gate_class is RZZGate:
            # Two-qubit, one param
            circuit._gates.append(RZZGate(qubits[0], qubits[1], float(params[0])))

        elif gate_class is ToffoliGate:
            circuit._gates.append(ToffoliGate(qubits[0], qubits[1], qubits[2]))

        elif gate_class is FredkinGate:
            circuit._gates.append(FredkinGate(qubits[0], qubits[1], qubits[2]))

        else:
            raise ValueError(f"Gate mapping not implemented: {gate_name}")

    return circuit
