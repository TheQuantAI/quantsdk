# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
Cirq interop — convert between QuantSDK circuits and Google Cirq circuits.

Requires: pip install quantsdk[interop]  (or pip install cirq-core)
"""

from __future__ import annotations

import math
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
    CSdgGate,
    CSGate,
    CSXGate,
    CU1Gate,
    CU3Gate,
    CXGate,
    CYGate,
    CZGate,
    DCXGate,
    ECRGate,
    FredkinGate,
    Gate,
    HGate,
    IGate,
    Measure,
    PhaseGate,
    Reset,
    RGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZXGate,
    RZZGate,
    SdgGate,
    SGate,
    SwapGate,
    SXdgGate,
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
    import cirq


def _check_cirq() -> None:
    """Raise ImportError if cirq is not installed."""
    try:
        import cirq as _cirq  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "Cirq is required for Cirq interop. "
            "Install it with: pip install quantsdk[interop]"
        ) from e


# ─── QuantSDK → Cirq ───


def to_cirq(circuit: Circuit) -> cirq.Circuit:
    """Convert a QuantSDK Circuit to a Google Cirq Circuit.

    Uses ``cirq.LineQubit`` for qubit mapping (qubit index → LineQubit(index)).

    Args:
        circuit: The QuantSDK circuit to convert.

    Returns:
        A ``cirq.Circuit`` equivalent.

    Raises:
        ImportError: If cirq-core is not installed.
        ValueError: If the circuit contains gates unsupported in Cirq.

    Example::

        import quantsdk as qs
        from quantsdk.interop.cirq_interop import to_cirq

        circuit = qs.Circuit(2)
        circuit.h(0).cx(0, 1).measure_all()

        cirq_circuit = to_cirq(circuit)
        print(cirq_circuit)
    """
    _check_cirq()
    import cirq as cq

    qubits = cq.LineQubit.range(circuit.num_qubits)
    ops: list[cq.Operation] = []

    measurement_count = 0

    for gate in circuit.gates:
        cirq_op = _gate_to_cirq_op(gate, qubits, measurement_count, cq)
        if cirq_op is not None:
            ops.append(cirq_op)
        if isinstance(gate, Measure):
            measurement_count += 1

    return cq.Circuit(ops)


def _gate_to_cirq_op(
    gate: Gate,
    qubits: list[Any],
    meas_idx: int,
    cq: Any,
) -> Any | None:
    """Convert a single QuantSDK gate to a Cirq operation."""
    q = gate.qubits

    # ── Measurement ──
    if isinstance(gate, Measure):
        return cq.measure(qubits[q[0]], key=f"m{meas_idx}")

    # ── Barrier — Cirq has no direct equivalent; skip ──
    if isinstance(gate, Barrier):
        return None

    # ── Reset ──
    if isinstance(gate, Reset):
        return cq.ResetChannel()(qubits[q[0]])

    # ── Single-qubit non-parametric gates ──
    if isinstance(gate, HGate):
        return cq.H(qubits[q[0]])

    if isinstance(gate, XGate):
        return cq.X(qubits[q[0]])

    if isinstance(gate, YGate):
        return cq.Y(qubits[q[0]])

    if isinstance(gate, ZGate):
        return cq.Z(qubits[q[0]])

    if isinstance(gate, SGate):
        return cq.S(qubits[q[0]])

    if isinstance(gate, SdgGate):
        return (cq.S**-1)(qubits[q[0]])

    if isinstance(gate, TGate):
        return cq.T(qubits[q[0]])

    if isinstance(gate, TdgGate):
        return (cq.T**-1)(qubits[q[0]])

    if isinstance(gate, IGate):
        return cq.I(qubits[q[0]])

    if isinstance(gate, SXGate):
        return cq.XPowGate(exponent=0.5)(qubits[q[0]])

    if isinstance(gate, SXdgGate):
        return cq.XPowGate(exponent=-0.5)(qubits[q[0]])

    # ── Single-qubit parametric gates ──
    if isinstance(gate, RXGate):
        return cq.rx(gate.params[0])(qubits[q[0]])

    if isinstance(gate, RYGate):
        return cq.ry(gate.params[0])(qubits[q[0]])

    if isinstance(gate, RZGate):
        return cq.rz(gate.params[0])(qubits[q[0]])

    if isinstance(gate, PhaseGate):
        # Phase(lam) = diag(1, e^{i*lam}) = ZPowGate(exponent=lam/pi)
        return cq.ZPowGate(exponent=gate.params[0] / math.pi)(qubits[q[0]])

    if isinstance(gate, U1Gate):
        # U1 is equivalent to Phase
        return cq.ZPowGate(exponent=gate.params[0] / math.pi)(qubits[q[0]])

    if isinstance(gate, U2Gate):
        # U2(phi, lam) = U3(pi/2, phi, lam) — decompose via MatrixGate
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]])

    if isinstance(gate, U3Gate):
        # General single-qubit rotation — use MatrixGate
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]])

    if isinstance(gate, RGate):
        # General rotation R(theta, phi) — use MatrixGate
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]])

    # ── Two-qubit non-parametric gates ──
    if isinstance(gate, CXGate):
        return cq.CNOT(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CZGate):
        return cq.CZ(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CYGate):
        # CY = controlled Y — Cirq doesn't have a direct CY constant
        return cq.ControlledGate(cq.Y)(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CHGate):
        return cq.ControlledGate(cq.H)(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, SwapGate):
        return cq.SWAP(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, iSwapGate):
        return cq.ISWAP(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, DCXGate):
        # DCX = CX(0,1) then CX(1,0) — decompose using MatrixGate
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, ECRGate):
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]], qubits[q[1]])

    # ── Controlled parametric gates ──
    if isinstance(gate, CSGate):
        return cq.ControlledGate(cq.S)(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CSdgGate):
        return cq.ControlledGate(cq.S**-1)(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CSXGate):
        return cq.ControlledGate(cq.XPowGate(exponent=0.5))(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CRXGate):
        return cq.ControlledGate(cq.rx(gate.params[0]))(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CRYGate):
        return cq.ControlledGate(cq.ry(gate.params[0]))(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CRZGate):
        return cq.ControlledGate(cq.rz(gate.params[0]))(qubits[q[0]], qubits[q[1]])

    if isinstance(gate, CPhaseGate):
        return cq.ControlledGate(cq.ZPowGate(exponent=gate.params[0] / math.pi))(
            qubits[q[0]], qubits[q[1]]
        )

    if isinstance(gate, CU1Gate):
        return cq.ControlledGate(cq.ZPowGate(exponent=gate.params[0] / math.pi))(
            qubits[q[0]], qubits[q[1]]
        )

    if isinstance(gate, CU3Gate):
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]], qubits[q[1]])

    # ── Two-qubit rotation gates ──
    if isinstance(gate, RXXGate):
        # RXX(theta) = XXPowGate(exponent=theta/pi, global_shift=-0.5)
        return cq.XXPowGate(exponent=gate.params[0] / math.pi, global_shift=-0.5)(
            qubits[q[0]], qubits[q[1]]
        )

    if isinstance(gate, RYYGate):
        return cq.YYPowGate(exponent=gate.params[0] / math.pi, global_shift=-0.5)(
            qubits[q[0]], qubits[q[1]]
        )

    if isinstance(gate, RZZGate):
        return cq.ZZPowGate(exponent=gate.params[0] / math.pi, global_shift=-0.5)(
            qubits[q[0]], qubits[q[1]]
        )

    if isinstance(gate, RZXGate):
        # No direct Cirq equivalent — use MatrixGate
        mat = gate.matrix()
        return cq.MatrixGate(mat)(qubits[q[0]], qubits[q[1]])

    # ── Three-qubit gates ──
    if isinstance(gate, ToffoliGate):
        return cq.TOFFOLI(qubits[q[0]], qubits[q[1]], qubits[q[2]])

    if isinstance(gate, CCZGate):
        return cq.CCZ(qubits[q[0]], qubits[q[1]], qubits[q[2]])

    if isinstance(gate, FredkinGate):
        return cq.FREDKIN(qubits[q[0]], qubits[q[1]], qubits[q[2]])

    raise ValueError(f"Unsupported gate for Cirq export: {gate.name}")


# ─── Cirq → QuantSDK ───


def from_cirq(cirq_circuit: cirq.Circuit) -> Circuit:
    """Convert a Google Cirq Circuit to a QuantSDK Circuit.

    Qubits are mapped by their ``cirq.LineQubit`` index.  If the Cirq circuit
    uses ``GridQubit`` or ``NamedQubit``, they are sorted and assigned
    sequential indices starting from 0.

    Args:
        cirq_circuit: The Cirq circuit to convert.

    Returns:
        A QuantSDK Circuit equivalent.

    Raises:
        ImportError: If cirq-core is not installed.
        ValueError: If the circuit contains unsupported gate types.

    Example::

        import cirq
        from quantsdk.interop.cirq_interop import from_cirq

        q = cirq.LineQubit.range(2)
        cirq_circuit = cirq.Circuit([
            cirq.H(q[0]),
            cirq.CNOT(q[0], q[1]),
            cirq.measure(q[0], q[1], key='result'),
        ])

        circuit = from_cirq(cirq_circuit)
        print(circuit.draw())
    """
    _check_cirq()
    import cirq as cq

    # Build qubit → index mapping
    all_qubits = sorted(cirq_circuit.all_qubits())
    qubit_map: dict[cq.Qid, int] = {q: i for i, q in enumerate(all_qubits)}
    num_qubits = len(all_qubits)

    if num_qubits == 0:
        return Circuit(1)  # At least 1 qubit

    circuit = Circuit(num_qubits)

    for op in cirq_circuit.all_operations():
        indices = tuple(qubit_map[q] for q in op.qubits)
        _cirq_op_to_quantsdk(op, indices, circuit, cq)

    return circuit


def _cirq_op_to_quantsdk(
    op: Any,
    indices: tuple[int, ...],
    circuit: Circuit,
    cq: Any,
) -> None:
    """Convert a single Cirq operation to QuantSDK gate(s) appended to circuit."""
    gate = op.gate

    if gate is None:
        raise ValueError(f"Unsupported Cirq operation (no gate): {op}")

    # ── Measurement ──
    if isinstance(gate, cq.MeasurementGate):
        for idx in indices:
            circuit._gates.append(Measure(idx))
        return

    # ── Reset ──
    if isinstance(gate, cq.ResetChannel):
        circuit._gates.append(Reset(indices[0]))
        return

    # ── Identity ──
    if isinstance(gate, cq.IdentityGate):
        for idx in indices:
            circuit._gates.append(IGate(idx))
        return

    # ── Controlled operations — unwrap ──
    if isinstance(gate, cq.ControlledGate):
        # We handle simple single-control gates
        sub_gate = gate.sub_gate
        num_controls = gate.num_controls()
        if num_controls == 1 and len(indices) == 2:
            ctrl, tgt = indices
            _handle_controlled_gate(sub_gate, ctrl, tgt, circuit, cq)
            return
        raise ValueError(
            f"Unsupported controlled gate with {num_controls} controls: {gate}"
        )

    # ── HPowGate ──
    if isinstance(gate, cq.HPowGate):
        exp = gate.exponent
        if _is_close(exp, 1):
            circuit._gates.append(HGate(indices[0]))
            return
        raise ValueError(f"Unsupported HPowGate exponent: {exp}")

    # ── XPowGate / Pauli-X ──
    if isinstance(gate, cq.XPowGate):
        exp = gate.exponent
        shift = gate.global_shift
        if _is_close(shift, -0.5):
            # This is an Rx gate: theta = exponent * pi
            theta = float(exp) * math.pi
            circuit._gates.append(RXGate(indices[0], theta))
            return
        if _is_close(exp, 1) and _is_close(shift, 0):
            circuit._gates.append(XGate(indices[0]))
            return
        if _is_close(exp, 0.5) and _is_close(shift, 0):
            circuit._gates.append(SXGate(indices[0]))
            return
        if _is_close(exp, -0.5) and _is_close(shift, 0):
            circuit._gates.append(SXdgGate(indices[0]))
            return
        raise ValueError(f"Unsupported XPowGate(exponent={exp}, global_shift={shift})")

    # ── YPowGate / Pauli-Y ──
    if isinstance(gate, cq.YPowGate):
        exp = gate.exponent
        shift = gate.global_shift
        if _is_close(shift, -0.5):
            theta = float(exp) * math.pi
            circuit._gates.append(RYGate(indices[0], theta))
            return
        if _is_close(exp, 1) and _is_close(shift, 0):
            circuit._gates.append(YGate(indices[0]))
            return
        raise ValueError(f"Unsupported YPowGate(exponent={exp}, global_shift={shift})")

    # ── ZPowGate / Pauli-Z / S / T / Phase ──
    if isinstance(gate, cq.ZPowGate):
        exp = gate.exponent
        shift = gate.global_shift
        if _is_close(shift, -0.5):
            # Rz gate: theta = exponent * pi
            theta = float(exp) * math.pi
            circuit._gates.append(RZGate(indices[0], theta))
            return
        if _is_close(shift, 0):
            if _is_close(exp, 1):
                circuit._gates.append(ZGate(indices[0]))
                return
            if _is_close(exp, 0.5):
                circuit._gates.append(SGate(indices[0]))
                return
            if _is_close(exp, -0.5):
                circuit._gates.append(SdgGate(indices[0]))
                return
            if _is_close(exp, 0.25):
                circuit._gates.append(TGate(indices[0]))
                return
            if _is_close(exp, -0.25):
                circuit._gates.append(TdgGate(indices[0]))
                return
            # General phase gate: P(lam) where lam = exp * pi
            lam = float(exp) * math.pi
            circuit._gates.append(PhaseGate(indices[0], lam))
            return
        raise ValueError(f"Unsupported ZPowGate(exponent={exp}, global_shift={shift})")

    # ── CXPowGate (CNOT) ──
    if isinstance(gate, cq.CXPowGate):
        if _is_close(gate.exponent, 1):
            circuit._gates.append(CXGate(indices[0], indices[1]))
            return
        raise ValueError(f"Unsupported CXPowGate exponent: {gate.exponent}")

    # ── CZPowGate ──
    if isinstance(gate, cq.CZPowGate):
        exp = gate.exponent
        if _is_close(exp, 1):
            circuit._gates.append(CZGate(indices[0], indices[1]))
            return
        # General controlled-phase: CP(lam) where lam = exp * pi
        lam = float(exp) * math.pi
        circuit._gates.append(CPhaseGate(indices[0], indices[1], lam))
        return

    # ── SwapPowGate ──
    if isinstance(gate, cq.SwapPowGate):
        if _is_close(gate.exponent, 1):
            circuit._gates.append(SwapGate(indices[0], indices[1]))
            return
        raise ValueError(f"Unsupported SwapPowGate exponent: {gate.exponent}")

    # ── ISwapPowGate ──
    if isinstance(gate, cq.ISwapPowGate):
        if _is_close(gate.exponent, 1):
            circuit._gates.append(iSwapGate(indices[0], indices[1]))
            return
        raise ValueError(f"Unsupported ISwapPowGate exponent: {gate.exponent}")

    # ── XXPowGate ──
    if isinstance(gate, cq.XXPowGate):
        theta = float(gate.exponent) * math.pi
        circuit._gates.append(RXXGate(indices[0], indices[1], theta))
        return

    # ── YYPowGate ──
    if isinstance(gate, cq.YYPowGate):
        theta = float(gate.exponent) * math.pi
        circuit._gates.append(RYYGate(indices[0], indices[1], theta))
        return

    # ── ZZPowGate ──
    if isinstance(gate, cq.ZZPowGate):
        theta = float(gate.exponent) * math.pi
        circuit._gates.append(RZZGate(indices[0], indices[1], theta))
        return

    # ── CCXPowGate (Toffoli) ──
    if isinstance(gate, cq.CCXPowGate):
        if _is_close(gate.exponent, 1):
            circuit._gates.append(ToffoliGate(indices[0], indices[1], indices[2]))
            return
        raise ValueError(f"Unsupported CCXPowGate exponent: {gate.exponent}")

    # ── CCZPowGate ──
    if isinstance(gate, cq.CCZPowGate):
        if _is_close(gate.exponent, 1):
            circuit._gates.append(CCZGate(indices[0], indices[1], indices[2]))
            return
        raise ValueError(f"Unsupported CCZPowGate exponent: {gate.exponent}")

    # ── CSwapGate (Fredkin) ──
    if isinstance(gate, cq.CSwapGate):
        circuit._gates.append(FredkinGate(indices[0], indices[1], indices[2]))
        return

    # ── MatrixGate — try to match unitary ──
    if isinstance(gate, cq.MatrixGate):
        # We cannot reliably reverse-engineer which gate this was.
        # Store as U3 for 1-qubit or raise for multi-qubit.
        if gate.num_qubits() == 1:
            mat = cq.unitary(gate)
            # Decompose to U3 via cirq
            theta, phi, lam = _unitary_to_u3(mat)
            circuit._gates.append(U3Gate(indices[0], theta, phi, lam))
            return
        raise ValueError(
            f"Cannot import multi-qubit MatrixGate back to QuantSDK: {gate}"
        )

    raise ValueError(f"Unsupported Cirq gate type for QuantSDK import: {type(gate).__name__}")


def _handle_controlled_gate(
    sub_gate: Any,
    ctrl: int,
    tgt: int,
    circuit: Circuit,
    cq: Any,
) -> None:
    """Handle a ControlledGate with one control qubit."""
    # HPowGate → CH
    if isinstance(sub_gate, cq.HPowGate) and _is_close(sub_gate.exponent, 1):
        circuit._gates.append(CHGate(ctrl, tgt))
        return

    # Y → CY
    if isinstance(sub_gate, cq.YPowGate) and _is_close(sub_gate.exponent, 1) and _is_close(
        sub_gate.global_shift, 0
    ):
        circuit._gates.append(CYGate(ctrl, tgt))
        return

    # ZPowGate → CS, CSdg, CPhase
    if isinstance(sub_gate, cq.ZPowGate) and _is_close(sub_gate.global_shift, 0):
        exp = sub_gate.exponent
        if _is_close(exp, 0.5):
            circuit._gates.append(CSGate(ctrl, tgt))
            return
        if _is_close(exp, -0.5):
            circuit._gates.append(CSdgGate(ctrl, tgt))
            return
        lam = float(exp) * math.pi
        circuit._gates.append(CPhaseGate(ctrl, tgt, lam))
        return

    # XPowGate with global_shift=-0.5 → CRX
    if isinstance(sub_gate, cq.XPowGate) and _is_close(sub_gate.global_shift, -0.5):
        theta = float(sub_gate.exponent) * math.pi
        circuit._gates.append(CRXGate(ctrl, tgt, theta))
        return

    # XPowGate exp=0.5 → CSX
    if isinstance(sub_gate, cq.XPowGate) and _is_close(sub_gate.exponent, 0.5) and _is_close(
        sub_gate.global_shift, 0
    ):
        circuit._gates.append(CSXGate(ctrl, tgt))
        return

    # YPowGate with global_shift=-0.5 → CRY
    if isinstance(sub_gate, cq.YPowGate) and _is_close(sub_gate.global_shift, -0.5):
        theta = float(sub_gate.exponent) * math.pi
        circuit._gates.append(CRYGate(ctrl, tgt, theta))
        return

    # ZPowGate with global_shift=-0.5 → CRZ
    if isinstance(sub_gate, cq.ZPowGate) and _is_close(sub_gate.global_shift, -0.5):
        theta = float(sub_gate.exponent) * math.pi
        circuit._gates.append(CRZGate(ctrl, tgt, theta))
        return

    # S gate (exponent 0.5) → CS
    if isinstance(sub_gate, cq.ZPowGate):
        exp = sub_gate.exponent
        lam = float(exp) * math.pi
        circuit._gates.append(CPhaseGate(ctrl, tgt, lam))
        return

    raise ValueError(f"Unsupported controlled sub-gate: {type(sub_gate).__name__}")


# ─── Utilities ───


def _is_close(a: float, b: float, atol: float = 1e-9) -> bool:
    """Check if two floats are close."""
    return abs(float(a) - float(b)) < atol


def _unitary_to_u3(mat: Any) -> tuple[float, float, float]:
    """Decompose a 2x2 unitary matrix into U3(theta, phi, lam) parameters.

    Uses the standard decomposition:
        U3(θ, φ, λ) = [[cos(θ/2), -e^{iλ} sin(θ/2)],
                        [e^{iφ} sin(θ/2), e^{i(φ+λ)} cos(θ/2)]]
    """
    import numpy as np

    # Extract parameters from the matrix
    # mat[0,0] = cos(theta/2)
    # mat[1,0] = e^{i*phi} * sin(theta/2)
    theta = 2 * math.acos(min(abs(mat[0, 0]), 1.0))

    if abs(math.sin(theta / 2)) < 1e-10:
        # theta ~ 0, phi and lam are degenerate
        phi = 0.0
        lam = float(np.angle(mat[1, 1]))
    elif abs(math.cos(theta / 2)) < 1e-10:
        # theta ~ pi
        phi = float(np.angle(mat[1, 0]))
        lam = float(-np.angle(mat[0, 1]))
    else:
        phi = float(np.angle(mat[1, 0]))
        lam = float(-np.angle(mat[0, 1]))

    return theta, phi, lam
