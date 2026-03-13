# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Tests for quantsdk.backends.ionq — IonQ/Braket backend adapter.

Tests use BraketLocalBackend (local state-vector simulator) which requires
no AWS credentials.  IonQBackend is tested with mocks where device access
is needed.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pytest

from quantsdk.circuit import Circuit

braket = pytest.importorskip("braket", reason="amazon-braket-sdk not installed")

from quantsdk.backend import BackendInfo, BackendStatus  # noqa: E402, I001
from quantsdk.backends.ionq import (  # noqa: E402
    BraketLocalBackend,
    IonQBackend,
    _check_braket,
    _resolve_device_arn,
    _to_braket_circuit,
)
from quantsdk.result import Result  # noqa: E402


# ═══════════════════════════════════════════════════════════════════
# BraketLocalBackend tests (real execution on local simulator)
# ═══════════════════════════════════════════════════════════════════


class TestBraketLocalBackend:
    """Test the Braket local simulator backend."""

    def test_instantiation(self) -> None:
        backend = BraketLocalBackend()
        assert backend is not None

    def test_repr(self) -> None:
        backend = BraketLocalBackend()
        assert "BraketLocalBackend" in repr(backend)
        assert "default" in repr(backend)

    def test_info(self) -> None:
        backend = BraketLocalBackend()
        info = backend.info()
        assert isinstance(info, BackendInfo)
        assert info.name == "braket_local_default"
        assert info.provider == "amazon"
        assert info.is_simulator is True
        assert info.status == BackendStatus.ONLINE
        assert info.num_qubits >= 20

    def test_run_bell_state(self) -> None:
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=1000)

        assert isinstance(result, Result)
        assert result.shots == 1000
        assert result.backend == "braket_local:default"
        assert sum(result.counts.values()) == 1000

        p_00 = result.counts.get("00", 0) / 1000
        p_11 = result.counts.get("11", 0) / 1000
        assert p_00 + p_11 > 0.95

    def test_run_ghz_state(self) -> None:
        circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=2000)

        assert result.shots == 2000
        p_000 = result.counts.get("000", 0) / 2000
        p_111 = result.counts.get("111", 0) / 2000
        assert p_000 + p_111 > 0.95

    def test_run_x_gate(self) -> None:
        circuit = Circuit(1).x(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("1", 0) == 100

    def test_run_y_gate(self) -> None:
        circuit = Circuit(1).y(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("1", 0) == 100

    def test_run_z_gate(self) -> None:
        """Z|0> = |0> (no flip)."""
        circuit = Circuit(1).z(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_h_gate(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=10000)
        p_0 = result.counts.get("0", 0) / 10000
        assert 0.45 < p_0 < 0.55

    def test_run_s_gate(self) -> None:
        """S|0> = |0> (phase gate, no flip)."""
        circuit = Circuit(1).s(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_sdg_gate(self) -> None:
        circuit = Circuit(1).sdg(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_t_gate(self) -> None:
        circuit = Circuit(1).t(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_i_gate(self) -> None:
        circuit = Circuit(1).i(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_sx_gate(self) -> None:
        """SX (sqrt-X): SX.SX = X, so SX|0> has 50% prob."""
        circuit = Circuit(1).sx(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=10000)
        p_0 = result.counts.get("0", 0) / 10000
        assert 0.45 < p_0 < 0.55

    def test_run_rx_gate(self) -> None:
        circuit = Circuit(1).rx(0, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("1", 0) == 100

    def test_run_ry_gate(self) -> None:
        circuit = Circuit(1).ry(0, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("1", 0) == 100

    def test_run_rz_gate(self) -> None:
        """RZ is phase gate — no computational basis change."""
        circuit = Circuit(1).rz(0, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_phase_gate(self) -> None:
        circuit = Circuit(1).p(0, math.pi / 4).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("0", 0) == 100

    def test_run_u3_as_x(self) -> None:
        """U3(pi, 0, pi) ~ X gate."""
        circuit = Circuit(1).u3(0, math.pi, 0, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("1", 0) == 100

    def test_run_cx_gate(self) -> None:
        circuit = Circuit(2).x(0).cx(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("11", 0) == 100

    def test_run_cz_gate(self) -> None:
        """CZ|1,+> -> |1,-> ; CZ|1,0> = |1,0>."""
        circuit = Circuit(2).x(0).cz(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("10", 0) == 100

    def test_run_cy_gate(self) -> None:
        circuit = Circuit(2).x(0).cy(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("11", 0) == 100

    def test_run_ch_gate(self) -> None:
        """CH|1,0> -> |1,+> (50/50 on qubit 1)."""
        circuit = Circuit(2).x(0).ch(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=10000)
        p_10 = result.counts.get("10", 0) / 10000
        p_11 = result.counts.get("11", 0) / 10000
        assert 0.45 < p_10 < 0.55
        assert 0.45 < p_11 < 0.55

    def test_run_swap_gate(self) -> None:
        circuit = Circuit(2).x(0).swap(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("01", 0) == 100

    def test_run_iswap_gate(self) -> None:
        """iSWAP|1,0> -> i|0,1> (measurement gives 01)."""
        circuit = Circuit(2).x(0).iswap(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("01", 0) == 100

    def test_run_cphase_gate(self) -> None:
        """CPhase only adds phase, no basis change."""
        circuit = Circuit(2).x(0).x(1).cp(0, 1, math.pi / 4).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("11", 0) == 100

    def test_run_crx_gate(self) -> None:
        """CRX(pi)|1,0> -> |1,1>."""
        circuit = Circuit(2).x(0).crx(0, 1, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("11", 0) == 100

    def test_run_cry_gate(self) -> None:
        """CRY(pi)|1,0> -> |1,1>."""
        circuit = Circuit(2).x(0).cry(0, 1, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("11", 0) == 100

    def test_run_crz_gate(self) -> None:
        """CRZ only affects phase, so |1,0> stays |1,0>."""
        circuit = Circuit(2).x(0).crz(0, 1, math.pi).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("10", 0) == 100

    def test_run_rzz_gate(self) -> None:
        """RZZ is phase-only — |00> stays |00>."""
        circuit = Circuit(2).rzz(0, 1, math.pi / 4).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("00", 0) == 100

    def test_run_toffoli(self) -> None:
        circuit = Circuit(3).x(0).x(1).ccx(0, 1, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("111", 0) == 100

    def test_run_toffoli_no_flip(self) -> None:
        """Toffoli only flips target when both controls are 1."""
        circuit = Circuit(3).x(0).ccx(0, 1, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("100", 0) == 100

    def test_run_fredkin(self) -> None:
        """Fredkin (CSWAP): |1,1,0> -> |1,0,1>."""
        circuit = Circuit(3).x(0).x(1).cswap(0, 1, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("101", 0) == 100

    def test_run_ccz(self) -> None:
        """CCZ only adds phase — |1,1,1> stays |1,1,1>."""
        circuit = Circuit(3).x(0).x(1).x(2).ccz(0, 1, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert result.counts.get("111", 0) == 100

    def test_run_many_shots(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=50000)
        assert sum(result.counts.values()) == 50000
        p_0 = result.counts.get("0", 0) / 50000
        assert 0.45 < p_0 < 0.55

    def test_result_metadata(self) -> None:
        circuit = Circuit(1).h(0).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=100)
        assert "backend" in result.metadata

    def test_barrier_skipped(self) -> None:
        """Barriers are skipped in Braket conversion."""
        circuit = Circuit(2).h(0).barrier().cx(0, 1).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=1000)
        assert sum(result.counts.values()) == 1000

    def test_multi_gate_circuit(self) -> None:
        """Complex circuit with multiple gate types."""
        circuit = Circuit(3).h(0).cx(0, 1).s(1).t(2).rx(2, math.pi / 2).cz(0, 2).measure_all()
        backend = BraketLocalBackend()
        result = backend.run(circuit, shots=1000)
        assert sum(result.counts.values()) == 1000

    def test_unsupported_gate_raises(self) -> None:
        """Unsupported gates raise ValueError."""
        from quantsdk.gates import Gate

        # Gate is a dataclass; create one with a name we don't handle
        fake_gate = Gate(name="fake_gate", qubits=(0,))

        circuit = Circuit(1)
        object.__setattr__(circuit, "_gates", [fake_gate])
        object.__setattr__(circuit, "_num_qubits", 1)

        with pytest.raises(ValueError, match="Unsupported gate"):
            _to_braket_circuit(circuit)


# ═══════════════════════════════════════════════════════════════════
# Circuit conversion tests
# ═══════════════════════════════════════════════════════════════════


class TestToBraketCircuit:
    """Test the _to_braket_circuit conversion function."""

    def test_empty_circuit(self) -> None:
        circuit = Circuit(1)
        bc = _to_braket_circuit(circuit)
        # Empty circuit should have no instructions
        assert len(bc.instructions) == 0

    def test_single_gate(self) -> None:
        circuit = Circuit(1).h(0)
        bc = _to_braket_circuit(circuit)
        assert len(bc.instructions) == 1

    def test_multi_qubit_circuit(self) -> None:
        circuit = Circuit(3).h(0).cx(0, 1).cx(1, 2)
        bc = _to_braket_circuit(circuit)
        assert len(bc.instructions) == 3

    def test_measurement_stripped(self) -> None:
        """Measurements are stripped (Braket measures all at end)."""
        circuit = Circuit(1).h(0).measure_all()
        bc = _to_braket_circuit(circuit)
        # Only the H gate should remain
        assert len(bc.instructions) == 1


# ═══════════════════════════════════════════════════════════════════
# Utility function tests
# ═══════════════════════════════════════════════════════════════════


class TestResolveDeviceArn:
    """Test device ARN resolution."""

    def test_shortname_simulator(self) -> None:
        arn = _resolve_device_arn("simulator")
        assert arn.startswith("arn:aws:braket")

    def test_shortname_harmony(self) -> None:
        arn = _resolve_device_arn("harmony")
        assert "ionq" in arn.lower() or "Harmony" in arn

    def test_shortname_aria(self) -> None:
        arn = _resolve_device_arn("aria")
        assert "Aria" in arn

    def test_shortname_aria2(self) -> None:
        arn = _resolve_device_arn("aria2")
        assert "Aria-2" in arn

    def test_shortname_forte(self) -> None:
        arn = _resolve_device_arn("forte")
        assert "Forte" in arn

    def test_full_arn_passthrough(self) -> None:
        full_arn = "arn:aws:braket:us-east-1::device/qpu/ionq/Custom"
        assert _resolve_device_arn(full_arn) == full_arn

    def test_unknown_device_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown IonQ device"):
            _resolve_device_arn("nonexistent_device")

    def test_unknown_device_lists_options(self) -> None:
        with pytest.raises(ValueError, match="Available shortnames"):
            _resolve_device_arn("bad_name")


class TestCheckBraket:
    """Test the braket import checker."""

    def test_check_braket_passes(self) -> None:
        """Should not raise when braket is installed."""
        _check_braket()  # No exception

    def test_check_braket_fails_gracefully(self) -> None:
        """Should raise ImportError with helpful message when braket missing."""
        with (
            patch.dict("sys.modules", {"braket": None}),
            pytest.raises(ImportError, match="Amazon Braket SDK"),
        ):
            _check_braket()


# ═══════════════════════════════════════════════════════════════════
# IonQBackend tests (mocked — no AWS credentials needed)
# ═══════════════════════════════════════════════════════════════════


class TestIonQBackend:
    """Test IonQBackend with mocked AWS device."""

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_instantiation(self, mock_device_cls: MagicMock) -> None:
        mock_device_cls.return_value = MagicMock()
        backend = IonQBackend(device="simulator")
        assert backend is not None
        mock_device_cls.assert_called_once()

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_repr(self, mock_device_cls: MagicMock) -> None:
        mock_device_cls.return_value = MagicMock()
        backend = IonQBackend(device="harmony")
        r = repr(backend)
        assert "IonQBackend" in r
        assert "harmony" in r

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_info_simulator(self, mock_device_cls: MagicMock) -> None:
        mock_device = MagicMock()
        mock_device.properties.paradigm.qubitCount = 25
        mock_device.status = "ONLINE"
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="simulator")
        info = backend.info()

        assert isinstance(info, BackendInfo)
        assert info.provider == "ionq"
        assert info.is_simulator is True
        assert info.status == BackendStatus.ONLINE
        assert info.num_qubits == 25

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_info_harmony(self, mock_device_cls: MagicMock) -> None:
        mock_device = MagicMock()
        mock_device.properties.paradigm.qubitCount = 11
        mock_device.status = "ONLINE"
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="harmony")
        info = backend.info()

        assert info.is_simulator is False
        assert info.num_qubits == 11

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_info_offline(self, mock_device_cls: MagicMock) -> None:
        mock_device = MagicMock()
        mock_device.properties.paradigm.qubitCount = 11
        mock_device.status = "OFFLINE"
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="harmony")
        info = backend.info()
        assert info.status == BackendStatus.OFFLINE

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_info_maintenance(self, mock_device_cls: MagicMock) -> None:
        mock_device = MagicMock()
        mock_device.properties.paradigm.qubitCount = 11
        mock_device.status = "CALIBRATING"
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="harmony")
        info = backend.info()
        assert info.status == BackendStatus.MAINTENANCE

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_info_fallback_qubit_count(self, mock_device_cls: MagicMock) -> None:
        """Falls back to 11 qubits when device properties are unavailable."""
        mock_device = MagicMock()
        mock_device.properties = None
        mock_device.status = "ONLINE"
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="harmony")
        info = backend.info()
        assert info.num_qubits == 11

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_run_returns_result(self, mock_device_cls: MagicMock) -> None:
        """Run returns a proper Result object."""
        from collections import Counter

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.state.return_value = "COMPLETED"
        mock_task.result.return_value = MagicMock(
            measurement_counts=Counter({"00": 500, "11": 500})
        )

        mock_device = MagicMock()
        mock_device.run.return_value = mock_task
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="simulator")
        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        result = backend.run(circuit, shots=1000)

        assert isinstance(result, Result)
        assert result.shots == 1000
        assert result.job_id == "task-123"
        assert result.backend == "ionq:simulator"
        assert sum(result.counts.values()) == 1000

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_run_with_s3_bucket(self, mock_device_cls: MagicMock) -> None:
        from collections import Counter

        mock_task = MagicMock()
        mock_task.id = "task-456"
        mock_task.state.return_value = "COMPLETED"
        mock_task.result.return_value = MagicMock(measurement_counts=Counter({"0": 1000}))

        mock_device = MagicMock()
        mock_device.run.return_value = mock_task
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(
            device="simulator",
            s3_bucket=("my-bucket", "results/"),
        )
        circuit = Circuit(1).x(0).measure_all()
        result = backend.run(circuit, shots=1000)

        # Verify s3 bucket was passed
        call_kwargs = mock_device.run.call_args[1]
        assert call_kwargs["s3_destination_folder"] == ("my-bucket", "results/")
        assert result.shots == 1000

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_run_with_disable_qubit_rewiring(self, mock_device_cls: MagicMock) -> None:
        from collections import Counter

        mock_task = MagicMock()
        mock_task.id = "task-789"
        mock_task.state.return_value = "COMPLETED"
        mock_task.result.return_value = MagicMock(measurement_counts=Counter({"1": 100}))

        mock_device = MagicMock()
        mock_device.run.return_value = mock_task
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="harmony")
        circuit = Circuit(1).x(0).measure_all()
        result = backend.run(circuit, shots=100, disable_qubit_rewiring=True)

        call_kwargs = mock_device.run.call_args[1]
        assert call_kwargs["disable_qubit_rewiring"] is True
        assert result.shots == 100

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_result_metadata_has_device_info(self, mock_device_cls: MagicMock) -> None:
        from collections import Counter

        mock_task = MagicMock()
        mock_task.id = "task-meta"
        mock_task.state.return_value = "COMPLETED"
        mock_task.result.return_value = MagicMock(measurement_counts=Counter({"0": 100}))

        mock_device = MagicMock()
        mock_device.run.return_value = mock_task
        mock_device_cls.return_value = mock_device

        backend = IonQBackend(device="simulator")
        circuit = Circuit(1).measure_all()
        result = backend.run(circuit, shots=100)

        assert "device_arn" in result.metadata
        assert "region" in result.metadata
        assert "task_status" in result.metadata

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_custom_arn(self, mock_device_cls: MagicMock) -> None:
        mock_device_cls.return_value = MagicMock()
        custom_arn = "arn:aws:braket:us-west-2::device/qpu/ionq/Custom"
        backend = IonQBackend(device=custom_arn, region="us-west-2")
        assert backend._device_arn == custom_arn

    @patch("quantsdk.backends.ionq._get_aws_device")
    def test_invalid_device_raises(self, mock_device_cls: MagicMock) -> None:
        with pytest.raises(ValueError, match="Unknown IonQ device"):
            IonQBackend(device="nonexistent_device_xyz")


# ═══════════════════════════════════════════════════════════════════
# Controlled-rotation matrix tests
# ═══════════════════════════════════════════════════════════════════


class TestControlledRotationMatrices:
    """Verify that CRX/CRY/CRZ unitary matrices are correct."""

    def test_crx_identity_at_zero(self) -> None:
        """CRX(0) should be identity."""
        import numpy as np

        from quantsdk.backends.ionq import _crx_matrix

        m = _crx_matrix(0.0)
        np.testing.assert_allclose(m, np.eye(4), atol=1e-10)

    def test_cry_identity_at_zero(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _cry_matrix

        m = _cry_matrix(0.0)
        np.testing.assert_allclose(m, np.eye(4), atol=1e-10)

    def test_crz_identity_at_zero(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _crz_matrix

        m = _crz_matrix(0.0)
        np.testing.assert_allclose(m, np.eye(4), atol=1e-10)

    def test_crx_is_unitary(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _crx_matrix

        m = _crx_matrix(math.pi / 3)
        np.testing.assert_allclose(m @ m.conj().T, np.eye(4), atol=1e-10)

    def test_cry_is_unitary(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _cry_matrix

        m = _cry_matrix(math.pi / 3)
        np.testing.assert_allclose(m @ m.conj().T, np.eye(4), atol=1e-10)

    def test_crz_is_unitary(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _crz_matrix

        m = _crz_matrix(math.pi / 3)
        np.testing.assert_allclose(m @ m.conj().T, np.eye(4), atol=1e-10)

    def test_crx_pi_flips_target(self) -> None:
        """CRX(pi) with control=1 should flip the target."""
        import numpy as np

        from quantsdk.backends.ionq import _crx_matrix

        m = _crx_matrix(math.pi)
        # State |10> = [0, 0, 1, 0]
        state_in = np.array([0, 0, 1, 0], dtype=complex)
        state_out = m @ state_in
        # Should go to |11> = [0, 0, 0, 1] (up to global phase)
        assert abs(abs(state_out[3]) - 1.0) < 1e-10

    def test_cry_pi_flips_target(self) -> None:
        import numpy as np

        from quantsdk.backends.ionq import _cry_matrix

        m = _cry_matrix(math.pi)
        state_in = np.array([0, 0, 1, 0], dtype=complex)
        state_out = m @ state_in
        assert abs(abs(state_out[3]) - 1.0) < 1e-10


# ═══════════════════════════════════════════════════════════════════
# Import guard test
# ═══════════════════════════════════════════════════════════════════


class TestImportGuard:
    """Test that missing braket gives a clear error."""

    def test_braket_import_error_message(self) -> None:
        with (
            patch.dict("sys.modules", {"braket": None}),
            pytest.raises(ImportError, match="quantsdk\\[ionq\\]"),
        ):
            _check_braket()
