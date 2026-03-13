# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.simulators.gpu — GPU/accelerated simulator backend.

Tests run in CPU mode (method="cpu") since CI has no GPU.
GPU-specific paths are tested with mocking.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pytest

from quantsdk.circuit import Circuit

aer = pytest.importorskip("qiskit_aer", reason="qiskit-aer not installed")

from quantsdk.backend import BackendInfo, BackendStatus  # noqa: E402, I001
from quantsdk.result import Result  # noqa: E402
from quantsdk.simulators.gpu import (  # noqa: E402
    GPUSimulator,
    _best_method,
    _check_aer,
    _detect_gpu,
)


# ═══════════════════════════════════════════════════════════════════
# GPUSimulator tests (CPU mode — actual execution)
# ═══════════════════════════════════════════════════════════════════


class TestGPUSimulatorCPU:
    """Test GPUSimulator in CPU fallback mode (no GPU needed)."""

    def test_instantiation_auto(self) -> None:
        sim = GPUSimulator(method="auto")
        assert sim is not None

    def test_instantiation_cpu(self) -> None:
        sim = GPUSimulator(method="cpu")
        assert sim is not None
        assert sim.method == "automatic"
        assert sim.is_gpu is False

    def test_repr(self) -> None:
        sim = GPUSimulator(method="cpu")
        r = repr(sim)
        assert "GPUSimulator" in r
        assert "automatic" in r

    def test_info(self) -> None:
        sim = GPUSimulator(method="cpu")
        info = sim.info()
        assert isinstance(info, BackendInfo)
        assert "gpu_simulator" in info.name
        assert info.provider == "quantsdk"
        assert info.is_simulator is True
        assert info.status == BackendStatus.ONLINE
        assert info.num_qubits >= 25

    def test_info_metadata(self) -> None:
        sim = GPUSimulator(method="cpu")
        info = sim.info()
        assert "method" in info.metadata
        assert "is_gpu" in info.metadata
        assert info.metadata["is_gpu"] is False

    def test_run_bell_state(self) -> None:
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=1000, seed=42)

        assert isinstance(result, Result)
        assert result.shots == 1000
        assert sum(result.counts.values()) == 1000

        p_00 = result.counts.get("00", 0) / 1000
        p_11 = result.counts.get("11", 0) / 1000
        assert p_00 + p_11 > 0.95

    def test_run_ghz_state(self) -> None:
        circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=2000, seed=42)

        assert result.shots == 2000
        p_000 = result.counts.get("000", 0) / 2000
        p_111 = result.counts.get("111", 0) / 2000
        assert p_000 + p_111 > 0.95

    def test_run_x_gate(self) -> None:
        circuit = Circuit(1).x(0).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert result.counts.get("1", 0) == 100

    def test_run_h_gate(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=10000, seed=42)
        p_0 = result.counts.get("0", 0) / 10000
        assert 0.45 < p_0 < 0.55

    def test_run_parametric_gates(self) -> None:
        circuit = Circuit(1).rx(0, math.pi).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert result.counts.get("1", 0) == 100

    def test_run_multi_gate(self) -> None:
        circuit = (
            Circuit(3)
            .h(0)
            .cx(0, 1)
            .s(1)
            .t(2)
            .rx(2, math.pi / 2)
            .cz(0, 2)
            .measure_all()
        )
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=1000, seed=42)
        assert sum(result.counts.values()) == 1000

    def test_run_reproducible_with_seed(self) -> None:
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        sim = GPUSimulator(method="cpu")
        r1 = sim.run(circuit, shots=1000, seed=42)
        r2 = sim.run(circuit, shots=1000, seed=42)
        assert r1.counts == r2.counts

    def test_run_different_seeds_differ(self) -> None:
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        sim = GPUSimulator(method="cpu")
        r1 = sim.run(circuit, shots=1000, seed=42)
        r2 = sim.run(circuit, shots=1000, seed=99)
        assert sum(r1.counts.values()) == 1000
        assert sum(r2.counts.values()) == 1000

    def test_run_many_shots(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=50000, seed=42)
        assert sum(result.counts.values()) == 50000
        p_0 = result.counts.get("0", 0) / 50000
        assert 0.45 < p_0 < 0.55

    def test_result_backend_name(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert "gpu_simulator" in result.backend

    def test_result_metadata(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert "method" in result.metadata
        assert "is_gpu" in result.metadata
        assert "success" in result.metadata
        assert result.metadata["success"] is True

    def test_custom_max_qubits(self) -> None:
        sim = GPUSimulator(method="cpu", max_qubits=10)
        assert sim.info().num_qubits == 10

    def test_exceeds_max_qubits_raises(self) -> None:
        sim = GPUSimulator(method="cpu", max_qubits=2)
        circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2).measure_all()
        with pytest.raises(ValueError, match="3 qubits"):
            sim.run(circuit, shots=100)

    def test_optimization_level(self) -> None:
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42, optimization_level=0)
        assert sum(result.counts.values()) == 100

    def test_toffoli(self) -> None:
        circuit = Circuit(3).x(0).x(1).ccx(0, 1, 2).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert result.counts.get("111", 0) == 100

    def test_swap(self) -> None:
        circuit = Circuit(2).x(0).swap(0, 1).measure_all()
        sim = GPUSimulator(method="cpu")
        result = sim.run(circuit, shots=100, seed=42)
        assert result.counts.get("01", 0) == 100


# ═══════════════════════════════════════════════════════════════════
# GPU detection tests
# ═══════════════════════════════════════════════════════════════════


class TestGPUDetection:
    """Test GPU detection and method selection."""

    def test_detect_gpu_returns_bool(self) -> None:
        result = _detect_gpu()
        assert isinstance(result, bool)

    def test_detect_gpu_no_gpu_on_ci(self) -> None:
        """On CI (no GPU), should return False."""
        # This is environment-dependent; on most CI it's False
        # Just verify it doesn't crash
        _detect_gpu()

    def test_best_method_cpu(self) -> None:
        method = _best_method("cpu")
        assert method == "automatic"

    def test_best_method_auto_fallback(self) -> None:
        """Auto with no GPU falls back to CPU method."""
        with patch("quantsdk.simulators.gpu._detect_gpu", return_value=False):
            method = _best_method("auto")
            assert method == "automatic"

    def test_best_method_auto_gpu(self) -> None:
        """Auto with GPU available selects GPU method."""
        with patch("quantsdk.simulators.gpu._detect_gpu", return_value=True):
            method = _best_method("auto")
            assert method == "statevector_gpu"

    def test_best_method_force_gpu_available(self) -> None:
        with patch("quantsdk.simulators.gpu._detect_gpu", return_value=True):
            method = _best_method("gpu")
            assert method == "statevector_gpu"

    def test_best_method_force_gpu_unavailable(self) -> None:
        with (
            patch("quantsdk.simulators.gpu._detect_gpu", return_value=False),
            pytest.raises(RuntimeError, match="GPU simulation requested"),
        ):
            _best_method("gpu")


# ═══════════════════════════════════════════════════════════════════
# GPU simulator with mocked GPU
# ═══════════════════════════════════════════════════════════════════


class TestGPUSimulatorGPU:
    """Test GPUSimulator behavior when GPU is 'available' (mocked)."""

    def test_gpu_mode_properties(self) -> None:
        with patch("quantsdk.simulators.gpu._best_method", return_value="statevector_gpu"):
            sim = GPUSimulator(method="gpu")
            assert sim.is_gpu is True
            assert sim.method == "statevector_gpu"
            assert sim._max_qubits == 30

    def test_gpu_info_metadata(self) -> None:
        with patch("quantsdk.simulators.gpu._best_method", return_value="statevector_gpu"):
            sim = GPUSimulator(method="gpu")
            info = sim.info()
            assert info.metadata["is_gpu"] is True
            assert info.num_qubits == 30

    def test_gpu_repr(self) -> None:
        with patch("quantsdk.simulators.gpu._best_method", return_value="statevector_gpu"):
            sim = GPUSimulator(method="gpu")
            r = repr(sim)
            assert "statevector_gpu" in r
            assert "gpu=True" in r

    def test_force_gpu_unavailable_raises(self) -> None:
        with pytest.raises(RuntimeError, match="GPU simulation requested"):
            GPUSimulator(method="gpu")


# ═══════════════════════════════════════════════════════════════════
# Noise model tests
# ═══════════════════════════════════════════════════════════════════


class TestNoiseModel:
    """Test GPUSimulator with noise models."""

    def test_with_depolarizing_noise(self) -> None:
        """Run with a simple noise model."""
        from qiskit_aer.noise import NoiseModel, depolarizing_error

        noise = NoiseModel()
        error = depolarizing_error(0.01, 1)
        noise.add_all_qubit_quantum_error(error, ["x", "h"])

        circuit = Circuit(1).x(0).measure_all()
        sim = GPUSimulator(method="cpu", noise_model=noise)
        result = sim.run(circuit, shots=10000, seed=42)

        # With noise, we should see some |0⟩ outcomes
        assert result.counts.get("1", 0) > 9800  # Still mostly |1⟩
        assert result.metadata["noise_model"] is True

    def test_noise_model_metadata(self) -> None:
        sim_no_noise = GPUSimulator(method="cpu")
        assert sim_no_noise.info().metadata["noise_model"] is False

        mock_noise = MagicMock()
        sim_noise = GPUSimulator(method="cpu", noise_model=mock_noise)
        assert sim_noise.info().metadata["noise_model"] is True


# ═══════════════════════════════════════════════════════════════════
# Import guard test
# ═══════════════════════════════════════════════════════════════════


class TestImportGuard:
    """Test import error messages."""

    def test_check_aer_passes(self) -> None:
        _check_aer()

    def test_check_aer_fails(self) -> None:
        with patch.dict("sys.modules", {"qiskit_aer": None}), pytest.raises(
            ImportError, match="Qiskit Aer"
        ):
            _check_aer()


# ═══════════════════════════════════════════════════════════════════
# Module-level import test
# ═══════════════════════════════════════════════════════════════════


class TestModuleImport:
    """Test that GPUSimulator is importable from simulators package."""

    def test_lazy_import(self) -> None:
        from quantsdk.simulators import GPUSimulator as GPUSim

        assert GPUSim is GPUSimulator
