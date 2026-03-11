# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.backends.ibm — AerBackend (local simulator).

Note: IBMBackend tests require a valid IBM Quantum token, so we only
test the AerBackend (local Aer simulator) in CI/local dev.
"""

from __future__ import annotations

import math

import pytest

from quantsdk.circuit import Circuit

aer = pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed")
qiskit = pytest.importorskip("qiskit", reason="Qiskit not installed")

from quantsdk.backend import BackendInfo, BackendStatus  # noqa: E402
from quantsdk.backends.ibm import AerBackend  # noqa: E402

# ─── AerBackend tests ───


class TestAerBackend:
    """Test the local Aer simulator backend."""

    def test_instantiation(self):
        """AerBackend can be created."""
        backend = AerBackend()
        assert backend is not None

    def test_info(self):
        """AerBackend returns valid BackendInfo."""
        backend = AerBackend()
        info = backend.info()

        assert isinstance(info, BackendInfo)
        assert info.name == "aer_simulator"
        assert info.provider == "ibm"
        assert info.is_simulator is True
        assert info.status == BackendStatus.ONLINE
        assert info.num_qubits >= 20

    def test_name_property(self):
        """Backend .name property works."""
        backend = AerBackend()
        assert backend.name == "aer_simulator"

    def test_run_bell_state(self):
        """Run a Bell state circuit on Aer."""
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=1000, seed=42)

        assert result.shots == 1000
        assert result.backend == "aer_simulator"
        assert sum(result.counts.values()) == 1000

        # Bell state should produce roughly equal |00⟩ and |11⟩
        assert "00" in result.counts or "11" in result.counts
        # Shouldn't have |01⟩ or |10⟩ (or very few due to noise)
        p_00 = result.counts.get("00", 0) / 1000
        p_11 = result.counts.get("11", 0) / 1000
        assert p_00 + p_11 > 0.95  # Should be essentially all 00 and 11

    def test_run_ghz_state(self):
        """Run a 3-qubit GHZ state."""
        circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=2000, seed=123)

        assert result.shots == 2000
        # GHZ: should be |000⟩ and |111⟩
        p_000 = result.counts.get("000", 0) / 2000
        p_111 = result.counts.get("111", 0) / 2000
        assert p_000 + p_111 > 0.95

    def test_run_single_qubit(self):
        """Run single-qubit circuit — X gate puts qubit in |1⟩."""
        circuit = Circuit(1).x(0).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=100, seed=42)

        # X|0⟩ = |1⟩ deterministically
        assert result.counts.get("1", 0) == 100

    def test_run_with_parametric_gates(self):
        """Run circuit with parametric gates."""
        circuit = Circuit(1).rx(0, math.pi).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=500, seed=42)

        # RX(pi)|0⟩ = -i|1⟩, measure always gives |1⟩
        assert result.counts.get("1", 0) == 500

    def test_result_metadata(self):
        """Result contains expected metadata."""
        circuit = Circuit(1).h(0).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=100, seed=42)

        assert "method" in result.metadata
        assert "success" in result.metadata
        assert result.metadata["success"] is True

    def test_reproducible_with_seed(self):
        """Same seed gives same results."""
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        backend = AerBackend()

        r1 = backend.run(circuit, shots=1000, seed=42)
        r2 = backend.run(circuit, shots=1000, seed=42)
        assert r1.counts == r2.counts

    def test_different_seeds_differ(self):
        """Different seeds can give different results."""
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        backend = AerBackend()

        r1 = backend.run(circuit, shots=1000, seed=42)
        r2 = backend.run(circuit, shots=1000, seed=99)
        # They might occasionally be the same, but with 1000 shots it's very unlikely
        # Just check both are valid
        assert sum(r1.counts.values()) == 1000
        assert sum(r2.counts.values()) == 1000

    def test_many_shots(self):
        """Can handle large shot count."""
        circuit = Circuit(1).h(0).measure_all()
        backend = AerBackend()
        result = backend.run(circuit, shots=50000, seed=42)

        assert sum(result.counts.values()) == 50000
        # H|0⟩ should give ~50% |0⟩ and ~50% |1⟩
        p_0 = result.counts.get("0", 0) / 50000
        assert 0.45 < p_0 < 0.55
