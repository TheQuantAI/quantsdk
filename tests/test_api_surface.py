# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for Circuit convenience methods and enhanced qs.run() API."""

from __future__ import annotations

import math

import pytest

import quantsdk as qs
from quantsdk.circuit import Circuit

# ─── Circuit.to_qiskit() / from_qiskit() convenience methods ───

qiskit = pytest.importorskip("qiskit", reason="Qiskit not installed")


class TestCircuitConvenienceMethods:
    """Test to_qiskit(), to_openqasm(), from_qiskit(), from_openqasm() on Circuit."""

    def test_to_qiskit(self):
        """circuit.to_qiskit() returns a Qiskit QuantumCircuit."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        qc = c.to_qiskit()

        assert qc.num_qubits == 2
        assert qc.num_clbits == 2

    def test_to_openqasm(self):
        """circuit.to_openqasm() returns a valid QASM string."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        qasm = c.to_openqasm()

        assert "OPENQASM 2.0;" in qasm
        assert "h q[0];" in qasm
        assert "cx q[0],q[1];" in qasm

    def test_from_qiskit_classmethod(self):
        """Circuit.from_qiskit() creates a QuantSDK circuit."""
        from qiskit.circuit import QuantumCircuit as QiskitQC

        qc = QiskitQC(2)
        qc.h(0)
        qc.cx(0, 1)

        c = Circuit.from_qiskit(qc)
        assert c.num_qubits == 2
        assert len(c.gates) == 2

    def test_from_openqasm_classmethod(self):
        """Circuit.from_openqasm() parses a QASM string."""
        qasm = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        h q[0];
        cx q[0],q[1];
        """
        c = Circuit.from_openqasm(qasm)
        assert c.num_qubits == 2
        assert len(c.gates) == 2

    def test_roundtrip_via_convenience(self):
        """circuit → to_qiskit → from_qiskit round-trip via convenience methods."""
        original = Circuit(3).h(0).cx(0, 1).rx(2, math.pi / 4).measure_all()
        qc = original.to_qiskit()
        restored = Circuit.from_qiskit(qc)

        assert restored.num_qubits == 3
        assert len(restored.gates) == len(original.gates)

    def test_roundtrip_via_openqasm_convenience(self):
        """circuit → to_openqasm → from_openqasm round-trip."""
        original = Circuit(2).h(0).cx(0, 1).measure_all()
        qasm = original.to_openqasm()
        restored = Circuit.from_openqasm(qasm)

        assert restored.num_qubits == 2
        assert len(restored.gates) == len(original.gates)


# ─── Enhanced qs.run() API ───


class TestRunnerEnhanced:
    """Test the enhanced qs.run() with multiple backend support."""

    def test_run_default(self):
        """Default backend (local simulator) still works."""
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, shots=100, seed=42)
        assert result.shots == 100
        assert result.backend == "local_simulator"

    def test_run_local_explicit(self):
        """Explicit 'local' backend works."""
        c = Circuit(1).x(0).measure_all()
        result = qs.run(c, backend="local", shots=50, seed=42)
        assert result.counts.get("1", 0) == 50

    def test_run_local_simulator_explicit(self):
        """Explicit 'local_simulator' backend works."""
        c = Circuit(1).h(0).measure_all()
        result = qs.run(c, backend="local_simulator", shots=100, seed=42)
        assert sum(result.counts.values()) == 100

    def test_run_aer_backend(self):
        """qs.run(backend='aer') uses Aer simulator."""
        pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed")
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, backend="aer", shots=500, seed=42)

        assert result.shots == 500
        assert result.backend == "aer_simulator"
        p_00 = result.counts.get("00", 0) / 500
        p_11 = result.counts.get("11", 0) / 500
        assert p_00 + p_11 > 0.95

    def test_run_aer_simulator_alias(self):
        """qs.run(backend='aer_simulator') also works."""
        pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed")
        c = Circuit(1).x(0).measure_all()
        result = qs.run(c, backend="aer_simulator", shots=100, seed=42)
        assert result.counts.get("1", 0) == 100

    def test_run_unknown_backend_raises(self):
        """Unknown backend raises ValueError."""
        c = Circuit(1).h(0).measure_all()
        with pytest.raises(ValueError, match="Unknown backend"):
            qs.run(c, backend="fake_backend")

    def test_run_smart_routing_works(self):
        """Smart routing via QuantRouter now works."""
        c = Circuit(1).h(0).measure_all()
        result = qs.run(c, optimize_for="quality", shots=100)
        assert result.shots == 100
        assert result.counts  # Should have measurement results


# ─── Result.plot_histogram() ───


class TestResultPlotHistogram:
    """Test Result.plot_histogram() visualization."""

    def test_plot_histogram_returns_figure(self):
        """plot_histogram returns a matplotlib Figure."""
        plt = pytest.importorskip("matplotlib.pyplot", reason="matplotlib not installed")
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, shots=100, seed=42)

        fig = result.plot_histogram(show=False)
        assert fig is not None
        assert hasattr(fig, "savefig")  # It's a Figure
        plt.close(fig)

    def test_plot_histogram_top_k(self):
        """plot_histogram with top_k limits bars."""
        plt = pytest.importorskip("matplotlib.pyplot", reason="matplotlib not installed")
        c = Circuit(3).h(0).h(1).h(2).measure_all()
        result = qs.run(c, shots=1000, seed=42)

        fig = result.plot_histogram(top_k=4, show=False)
        axes = fig.get_axes()
        # Should have bars (patches) - at most top_k
        num_bars = len(axes[0].patches)
        assert num_bars <= 4
        plt.close(fig)

    def test_plot_histogram_custom_title(self):
        """plot_histogram accepts a custom title."""
        plt = pytest.importorskip("matplotlib.pyplot", reason="matplotlib not installed")
        c = Circuit(1).h(0).measure_all()
        result = qs.run(c, shots=100, seed=42)

        fig = result.plot_histogram(title="My Custom Title", show=False)
        ax = fig.get_axes()[0]
        assert ax.get_title() == "My Custom Title"
        plt.close(fig)


# ─── Result.to_pandas() ───


class TestResultToPandas:
    """Test Result.to_pandas() DataFrame export."""

    def test_to_pandas_returns_dataframe(self):
        """to_pandas returns a pandas DataFrame."""
        pd = pytest.importorskip("pandas", reason="pandas not installed")
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, shots=1000, seed=42)

        df = result.to_pandas()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["bitstring", "count", "probability"]

    def test_to_pandas_sorted_by_count(self):
        """DataFrame is sorted by count descending."""
        pytest.importorskip("pandas", reason="pandas not installed")
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, shots=1000, seed=42)

        df = result.to_pandas()
        counts = df["count"].tolist()
        assert counts == sorted(counts, reverse=True)

    def test_to_pandas_probabilities_sum_to_one(self):
        """Probabilities in the DataFrame sum to 1."""
        pytest.importorskip("pandas", reason="pandas not installed")
        c = Circuit(2).h(0).cx(0, 1).measure_all()
        result = qs.run(c, shots=1000, seed=42)

        df = result.to_pandas()
        assert abs(df["probability"].sum() - 1.0) < 1e-10

    def test_to_pandas_row_count_matches_unique_outcomes(self):
        """Number of rows matches number of unique measurement outcomes."""
        pytest.importorskip("pandas", reason="pandas not installed")
        c = Circuit(1).x(0).measure_all()
        result = qs.run(c, shots=100, seed=42)

        df = result.to_pandas()
        assert len(df) == len(result.counts)
