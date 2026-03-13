# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
PennyLane interop -- convert between QuantSDK circuits and PennyLane tapes.

Requires: pip install quantsdk[interop]  (or pip install pennylane)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from quantsdk.circuit import Circuit
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
    ECRGate,
    FredkinGate,
    Gate,
    HGate,
    IGate,
    Measure,
    PhaseGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXGate,
    TdgGate,
    TGate,
    ToffoliGate,
    U1Gate,
    U2Gate,
    U3Gate,
    XGate,
    YGate,
    ZGate,
    iSwapGate,
)

if TYPE_CHECKING:
    import pennylane as qml


def _check_pennylane() -> None:
    """Raise ImportError if PennyLane is not installed."""
    try:
        import pennylane as _qml  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "PennyLane is required for PennyLane interop. "
            "Install it with: pip install quantsdk[interop]"
        ) from e


# ─── QuantSDK -> PennyLane ───


def to_pennylane(circuit: Circuit) -> qml.tape.QuantumScript:
    """Convert a QuantSDK Circuit to a PennyLane QuantumScript (tape).

    The returned tape contains all gate operations. If the circuit has
    measurements, ``qml.counts()`` is added on the measured wires.

    Args:
        circuit: The QuantSDK circuit to convert.

    Returns:
        A ``pennylane.tape.QuantumScript`` containing the operations.

    Raises:
        ImportError: If PennyLane is not installed.
        ValueError: If the circuit contains unsupported gates.

    Example::

        import quantsdk as qs
        from quantsdk.interop.pennylane_interop import to_pennylane

        circuit = qs.Circuit(2)
        circuit.h(0).cx(0, 1).measure_all()

        tape = to_pennylane(circuit)
    """
    _check_pennylane()
    import pennylane as pl

    ops: list[Any] = []
    measured_wires: list[int] = []

    for gate in circuit.gates:
        pl_op = _gate_to_pennylane(gate, pl)
        if pl_op is not None:
            ops.append(pl_op)
        if isinstance(gate, Measure):
            measured_wires.append(gate.qubits[0])

    # Build measurements
    measurements: list[Any] = []
    if measured_wires:
        measurements.append(pl.counts(wires=measured_wires))
    else:
        # Default: return state measurement on all wires
        measurements.append(pl.state())

    return pl.tape.QuantumScript(ops, measurements)


def _gate_to_pennylane(gate: Gate, pl: Any) -> Any | None:
    """Convert a single QuantSDK gate to a PennyLane operation."""
    q = gate.qubits

    # ── Measurement -- handled separately ──
    if isinstance(gate, Measure):
        return None

    # ── Barrier -- no PennyLane equivalent ──
    if isinstance(gate, Barrier):
        return pl.Barrier(wires=list(q))

    # ── Single-qubit non-parametric ──
    if isinstance(gate, HGate):
        return pl.Hadamard(wires=q[0])

    if isinstance(gate, XGate):
        return pl.PauliX(wires=q[0])

    if isinstance(gate, YGate):
        return pl.PauliY(wires=q[0])

    if isinstance(gate, ZGate):
        return pl.PauliZ(wires=q[0])

    if isinstance(gate, SGate):
        return pl.S(wires=q[0])

    if isinstance(gate, SdgGate):
        return pl.adjoint(pl.S(wires=q[0]))

    if isinstance(gate, TGate):
        return pl.T(wires=q[0])

    if isinstance(gate, TdgGate):
        return pl.adjoint(pl.T(wires=q[0]))

    if isinstance(gate, IGate):
        return pl.Identity(wires=q[0])

    if isinstance(gate, SXGate):
        return pl.SX(wires=q[0])

    # ── Single-qubit parametric ──
    if isinstance(gate, RXGate):
        return pl.RX(gate.params[0], wires=q[0])

    if isinstance(gate, RYGate):
        return pl.RY(gate.params[0], wires=q[0])

    if isinstance(gate, RZGate):
        return pl.RZ(gate.params[0], wires=q[0])

    if isinstance(gate, PhaseGate):
        return pl.PhaseShift(gate.params[0], wires=q[0])

    if isinstance(gate, U1Gate):
        return pl.U1(gate.params[0], wires=q[0])

    if isinstance(gate, U2Gate):
        return pl.U2(gate.params[0], gate.params[1], wires=q[0])

    if isinstance(gate, U3Gate):
        return pl.U3(gate.params[0], gate.params[1], gate.params[2], wires=q[0])

    # ── Two-qubit non-parametric ──
    if isinstance(gate, CXGate):
        return pl.CNOT(wires=[q[0], q[1]])

    if isinstance(gate, CZGate):
        return pl.CZ(wires=[q[0], q[1]])

    if isinstance(gate, CYGate):
        return pl.CY(wires=[q[0], q[1]])

    if isinstance(gate, CHGate):
        return pl.CH(wires=[q[0], q[1]])

    if isinstance(gate, SwapGate):
        return pl.SWAP(wires=[q[0], q[1]])

    if isinstance(gate, iSwapGate):
        return pl.ISWAP(wires=[q[0], q[1]])

    if isinstance(gate, ECRGate):
        return pl.ECR(wires=[q[0], q[1]])

    # ── Controlled parametric ──
    if isinstance(gate, CRXGate):
        return pl.CRX(gate.params[0], wires=[q[0], q[1]])

    if isinstance(gate, CRYGate):
        return pl.CRY(gate.params[0], wires=[q[0], q[1]])

    if isinstance(gate, CRZGate):
        return pl.CRZ(gate.params[0], wires=[q[0], q[1]])

    if isinstance(gate, CPhaseGate):
        return pl.ControlledPhaseShift(gate.params[0], wires=[q[0], q[1]])

    # ── Two-qubit rotation (Ising) ──
    if isinstance(gate, RXXGate):
        return pl.IsingXX(gate.params[0], wires=[q[0], q[1]])

    if isinstance(gate, RYYGate):
        return pl.IsingYY(gate.params[0], wires=[q[0], q[1]])

    if isinstance(gate, RZZGate):
        return pl.IsingZZ(gate.params[0], wires=[q[0], q[1]])

    # ── Three-qubit ──
    if isinstance(gate, ToffoliGate):
        return pl.Toffoli(wires=[q[0], q[1], q[2]])

    if isinstance(gate, FredkinGate):
        return pl.CSWAP(wires=[q[0], q[1], q[2]])

    if isinstance(gate, CCZGate):
        return pl.CCZ(wires=[q[0], q[1], q[2]])

    raise ValueError(f"Unsupported gate for PennyLane export: {gate.name}")


# ─── PennyLane -> QuantSDK ───


def from_pennylane(tape: qml.tape.QuantumScript) -> Circuit:
    """Convert a PennyLane QuantumScript (tape) to a QuantSDK Circuit.

    Args:
        tape: A PennyLane QuantumScript or QuantumTape.

    Returns:
        A QuantSDK Circuit equivalent.

    Raises:
        ImportError: If PennyLane is not installed.
        ValueError: If the tape contains unsupported operations.

    Example::

        import pennylane as qml
        from quantsdk.interop.pennylane_interop import from_pennylane

        ops = [qml.Hadamard(wires=0), qml.CNOT(wires=[0, 1])]
        measurements = [qml.counts(wires=[0, 1])]
        tape = qml.tape.QuantumScript(ops, measurements)

        circuit = from_pennylane(tape)
        print(circuit.draw())
    """
    _check_pennylane()
    import pennylane as pl

    # Determine number of qubits from tape wires
    all_wires = tape.wires.tolist()
    if not all_wires:
        return Circuit(1)

    # Map wire labels to sequential qubit indices
    wire_map: dict[Any, int] = {}
    for w in sorted(all_wires):
        wire_map[w] = len(wire_map)
    num_qubits = len(wire_map)

    circuit = Circuit(num_qubits)

    for op in tape.operations:
        wires = [wire_map[w] for w in op.wires.tolist()]
        _pennylane_op_to_quantsdk(op, wires, circuit, pl)

    # Add measurements based on tape measurements
    for meas in tape.measurements:
        meas_wires = [wire_map[w] for w in meas.wires.tolist()]
        for w in meas_wires:
            # Only add if not already measured
            already_measured = any(
                isinstance(g, Measure) and g.qubits[0] == w for g in circuit._gates
            )
            if not already_measured:
                circuit._gates.append(Measure(w))

    return circuit


def _pennylane_op_to_quantsdk(
    op: Any,
    wires: list[int],
    circuit: Circuit,
    pl: Any,
) -> None:
    """Convert a PennyLane operation to QuantSDK gate(s)."""
    name = op.name
    params = op.parameters

    # ── Adjoint operations ──
    if isinstance(op, pl.ops.op_math.Adjoint):
        base = op.base
        base_name = type(base).__name__
        if base_name == "S":
            circuit._gates.append(SdgGate(wires[0]))
            return
        if base_name == "T":
            circuit._gates.append(TdgGate(wires[0]))
            return
        if base_name == "SX":
            # SXdg
            from quantsdk.gates import SXdgGate

            circuit._gates.append(SXdgGate(wires[0]))
            return
        raise ValueError(f"Unsupported adjoint operation: Adjoint({base_name})")

    # ── Barrier ──
    if name == "Barrier":
        circuit._gates.append(Barrier(wires))
        return

    # ── Single-qubit non-parametric ──
    if isinstance(op, pl.Hadamard):
        circuit._gates.append(HGate(wires[0]))
        return

    if isinstance(op, pl.PauliX):
        circuit._gates.append(XGate(wires[0]))
        return

    if isinstance(op, pl.PauliY):
        circuit._gates.append(YGate(wires[0]))
        return

    if isinstance(op, pl.PauliZ):
        circuit._gates.append(ZGate(wires[0]))
        return

    if isinstance(op, pl.S):
        circuit._gates.append(SGate(wires[0]))
        return

    if isinstance(op, pl.T):
        circuit._gates.append(TGate(wires[0]))
        return

    if isinstance(op, pl.Identity):
        circuit._gates.append(IGate(wires[0]))
        return

    if isinstance(op, pl.SX):
        circuit._gates.append(SXGate(wires[0]))
        return

    # ── Single-qubit parametric ──
    if isinstance(op, pl.RX):
        circuit._gates.append(RXGate(wires[0], float(params[0])))
        return

    if isinstance(op, pl.RY):
        circuit._gates.append(RYGate(wires[0], float(params[0])))
        return

    if isinstance(op, pl.RZ):
        circuit._gates.append(RZGate(wires[0], float(params[0])))
        return

    if isinstance(op, pl.PhaseShift):
        circuit._gates.append(PhaseGate(wires[0], float(params[0])))
        return

    if isinstance(op, pl.U1):
        circuit._gates.append(U1Gate(wires[0], float(params[0])))
        return

    if isinstance(op, pl.U2):
        circuit._gates.append(U2Gate(wires[0], float(params[0]), float(params[1])))
        return

    if isinstance(op, pl.U3):
        circuit._gates.append(
            U3Gate(wires[0], float(params[0]), float(params[1]), float(params[2]))
        )
        return

    # ── Two-qubit non-parametric ──
    if isinstance(op, pl.CNOT):
        circuit._gates.append(CXGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.CZ):
        circuit._gates.append(CZGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.CY):
        circuit._gates.append(CYGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.CH):
        circuit._gates.append(CHGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.SWAP):
        circuit._gates.append(SwapGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.ISWAP):
        circuit._gates.append(iSwapGate(wires[0], wires[1]))
        return

    if isinstance(op, pl.ECR):
        circuit._gates.append(ECRGate(wires[0], wires[1]))
        return

    # ── Controlled parametric ──
    if isinstance(op, pl.CRX):
        circuit._gates.append(CRXGate(wires[0], wires[1], float(params[0])))
        return

    if isinstance(op, pl.CRY):
        circuit._gates.append(CRYGate(wires[0], wires[1], float(params[0])))
        return

    if isinstance(op, pl.CRZ):
        circuit._gates.append(CRZGate(wires[0], wires[1], float(params[0])))
        return

    if isinstance(op, pl.ControlledPhaseShift):
        circuit._gates.append(CPhaseGate(wires[0], wires[1], float(params[0])))
        return

    # ── Two-qubit rotation (Ising) ──
    if isinstance(op, pl.IsingXX):
        circuit._gates.append(RXXGate(wires[0], wires[1], float(params[0])))
        return

    if isinstance(op, pl.IsingYY):
        circuit._gates.append(RYYGate(wires[0], wires[1], float(params[0])))
        return

    if isinstance(op, pl.IsingZZ):
        circuit._gates.append(RZZGate(wires[0], wires[1], float(params[0])))
        return

    # ── Three-qubit ──
    if isinstance(op, pl.Toffoli):
        circuit._gates.append(ToffoliGate(wires[0], wires[1], wires[2]))
        return

    if isinstance(op, pl.CSWAP):
        circuit._gates.append(FredkinGate(wires[0], wires[1], wires[2]))
        return

    if isinstance(op, pl.CCZ):
        circuit._gates.append(CCZGate(wires[0], wires[1], wires[2]))
        return

    raise ValueError(
        f"Unsupported PennyLane operation for QuantSDK import: {name} ({type(op).__name__})"
    )
