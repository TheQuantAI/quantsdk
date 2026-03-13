# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""Coverage-boost tests for quantsdk modules.

Targets lines in __init__.py, result.py, runner.py, circuit.py (draw),
gates.py, cloud/*, and interop/qiskit_interop.py that were < 90% covered.
"""

from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from quantsdk.circuit import Circuit
from quantsdk.result import Result

# ═══════════════════════════════════════════════════════════════════
# quantsdk.__init__ lazy import tests
# ═══════════════════════════════════════════════════════════════════


class TestLazyImports:
    """Test lazy module __getattr__ in quantsdk/__init__.py."""

    def test_import_interop(self) -> None:
        import importlib

        mod = importlib.import_module("quantsdk.interop")
        assert hasattr(mod, "to_qiskit")

    def test_import_backends(self) -> None:
        import importlib

        mod = importlib.import_module("quantsdk.backends")
        assert mod is not None

    def test_import_router(self) -> None:
        import importlib

        mod = importlib.import_module("quantsdk.router")
        assert hasattr(mod, "QuantRouter")

    def test_import_cloud(self) -> None:
        import importlib

        mod = importlib.import_module("quantsdk.cloud")
        assert hasattr(mod, "CloudClient")

    def test_invalid_attribute_raises(self) -> None:
        import quantsdk as qs

        with pytest.raises(AttributeError, match="no attribute"):
            qs.__getattr__("nonexistent_module_xyz")


# ═══════════════════════════════════════════════════════════════════
# result.py — missing line coverage
# ═══════════════════════════════════════════════════════════════════


class TestResultEdgeCases:
    """Cover edge cases in Result."""

    def test_probabilities_zero_shots(self) -> None:
        r = Result(counts={"00": 0}, shots=0)
        assert r.probabilities == {}

    def test_num_qubits_empty_counts(self) -> None:
        r = Result(counts={}, shots=0)
        assert r.num_qubits == 0

    def test_get_probability_zero_shots(self) -> None:
        r = Result(counts={"00": 10}, shots=0)
        assert r.get_probability("00") == 0.0

    def test_top_k_zero_shots(self) -> None:
        r = Result(counts={"00": 10, "11": 5}, shots=0)
        top = r.top_k(2)
        assert len(top) == 2
        assert top[0][2] == 0.0  # probability is 0

    def test_expectation_value_zero_shots(self) -> None:
        r = Result(counts={"11": 10}, shots=0)
        assert r.expectation_value() == 0.0

    def test_to_dict(self) -> None:
        r = Result(counts={"00": 50, "11": 50}, shots=100, backend="test")
        d = r.to_dict()
        assert d["counts"] == {"00": 50, "11": 50}
        assert d["shots"] == 100
        assert d["backend"] == "test"
        assert d["most_likely"] in ("00", "11")
        assert "probabilities" in d

    def test_to_dict_empty_counts(self) -> None:
        r = Result(counts={}, shots=0, backend="test")
        d = r.to_dict()
        assert d["most_likely"] is None

    def test_to_pandas(self) -> None:
        pytest.importorskip("pandas")
        r = Result(counts={"00": 60, "11": 40}, shots=100)
        df = r.to_pandas()
        assert len(df) == 2
        assert "bitstring" in df.columns
        assert "count" in df.columns
        assert "probability" in df.columns

    def test_to_pandas_missing(self) -> None:
        with patch.dict("sys.modules", {"pandas": None}), pytest.raises(
            ImportError, match="pandas"
        ):
            r = Result(counts={"00": 50}, shots=50)
            r.to_pandas()

    def test_plot_histogram(self) -> None:
        pytest.importorskip("matplotlib")
        r = Result(counts={"00": 60, "11": 40}, shots=100)
        fig = r.plot_histogram(show=False, top_k=2, title="Test")
        assert fig is not None

    def test_plot_histogram_missing(self) -> None:
        with patch.dict("sys.modules", {"matplotlib": None, "matplotlib.pyplot": None}), pytest.raises(
            ImportError, match="matplotlib"
        ):
            r = Result(counts={"00": 50}, shots=50)
            r.plot_histogram()

    def test_repr(self) -> None:
        r = Result(counts={"00": 50, "11": 50}, shots=100, backend="test")
        s = repr(r)
        assert "Result" in s
        assert "100" in s

    def test_repr_many_outcomes(self) -> None:
        counts = {f"{i:04b}": 1 for i in range(16)}
        r = Result(counts=counts, shots=16)
        s = repr(r)
        assert "..." in s

    def test_str_summary(self) -> None:
        r = Result(counts={"00": 60, "11": 40}, shots=100, backend="test")
        s = str(r)
        assert "Result" in s
        assert "test" in s
        assert "Top results" in s


# ═══════════════════════════════════════════════════════════════════
# runner.py — coverage for backend dispatch paths
# ═══════════════════════════════════════════════════════════════════


class TestRunnerPaths:
    """Cover runner.py dispatch paths."""

    def test_run_aer_backend(self) -> None:
        """Test Aer backend dispatch."""
        pytest.importorskip("qiskit_aer")
        from quantsdk.runner import run

        circuit = Circuit(1).x(0).measure_all()
        result = run(circuit, backend="aer", shots=100, seed=42)
        assert result.counts.get("1", 0) == 100

    def test_run_ibm_import_error(self) -> None:
        """IBM backend shows helpful error when deps missing."""
        from quantsdk.runner import run

        with patch.dict("sys.modules", {"quantsdk.backends.ibm": None}), pytest.raises(
            ImportError, match="qiskit"
        ):
            run(Circuit(1).x(0).measure_all(), backend="ibm_brisbane", shots=100)

    def test_run_unknown_backend(self) -> None:
        from quantsdk.runner import run

        with pytest.raises(ValueError, match="Unknown backend"):
            run(Circuit(1).measure_all(), backend="totally_unknown_xyz", shots=100)


# ═══════════════════════════════════════════════════════════════════
# gates.py — base Gate.matrix(), Barrier, Measure with classical_bit
# ═══════════════════════════════════════════════════════════════════


class TestGatesEdgeCases:
    """Cover missing lines in gates.py."""

    def test_base_gate_matrix_not_implemented(self) -> None:
        """Gate base matrix() raises NotImplementedError."""
        from quantsdk.gates import Gate

        g = Gate(name="test", qubits=(0,))
        with pytest.raises(NotImplementedError, match="Matrix not implemented"):
            g.matrix()

    def test_barrier_matrix_raises(self) -> None:
        from quantsdk.gates import Barrier

        b = Barrier(qubits=(0, 1))
        with pytest.raises(NotImplementedError, match="not a unitary"):
            b.matrix()

    def test_measure_with_classical_bit(self) -> None:
        from quantsdk.gates import Measure

        m = Measure(qubit=0, classical_bit=0)
        assert m.classical_bit == 0
        assert m.qubits == (0,)

    def test_reset_gate(self) -> None:
        from quantsdk.gates import Reset

        r = Reset(qubit=0)
        assert r.name == "RESET"
        assert r.qubits == (0,)

    def test_measure_gate_name(self) -> None:
        from quantsdk.gates import Measure

        m = Measure(qubit=0)
        assert m.name == "MEASURE"


# ═══════════════════════════════════════════════════════════════════
# circuit.py — draw() method coverage
# ═══════════════════════════════════════════════════════════════════


class TestCircuitDraw:
    """Cover circuit.draw() method edge cases."""

    def test_draw_empty_circuit(self) -> None:
        c = Circuit(2)
        d = c.draw()
        assert "q0" in d
        assert "q1" in d

    def test_draw_barrier(self) -> None:
        c = Circuit(2).h(0).barrier().cx(0, 1)
        d = c.draw()
        assert "|" in d

    def test_draw_measure(self) -> None:
        c = Circuit(1).h(0).measure_all()
        d = c.draw()
        assert "M" in d

    def test_draw_parametric_single_qubit(self) -> None:
        c = Circuit(1).rx(0, 1.23)
        d = c.draw()
        assert "RX" in d
        assert "1.23" in d

    def test_draw_controlled_gate(self) -> None:
        c = Circuit(2).cx(0, 1)
        d = c.draw()
        assert "X" in d

    def test_draw_cz(self) -> None:
        c = Circuit(3).cz(0, 2)
        d = c.draw()
        # Should show control wire through q1
        lines = d.split("\n")
        assert len(lines) == 3

    def test_draw_swap(self) -> None:
        c = Circuit(2).swap(0, 1)
        d = c.draw()
        assert "x" in d

    def test_draw_iswap(self) -> None:
        c = Circuit(2).iswap(0, 1)
        d = c.draw()
        assert "iS" in d

    def test_draw_toffoli(self) -> None:
        c = Circuit(3).ccx(0, 1, 2)
        d = c.draw()
        assert "X" in d

    def test_draw_multi_gate(self) -> None:
        c = Circuit(3).h(0).cx(0, 1).s(2).ccx(0, 1, 2)
        d = c.draw()
        assert "q0" in d
        assert "q2" in d

    def test_draw_rzz(self) -> None:
        c = Circuit(2).rzz(0, 1, 0.5)
        d = c.draw()
        assert "RZZ" in d

    def test_draw_cp(self) -> None:
        c = Circuit(2).cp(0, 1, 0.5)
        d = c.draw()
        assert "P" in d


# ═══════════════════════════════════════════════════════════════════
# interop/qiskit_interop.py — from_qiskit() path
# ═══════════════════════════════════════════════════════════════════


class TestQiskitInteropCoverage:
    """Cover from_qiskit() and to_qiskit() edge cases."""

    def test_to_qiskit_roundtrip_bell(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import from_qiskit, to_qiskit

        c = Circuit(2).h(0).cx(0, 1).measure_all()
        qc = to_qiskit(c)
        c2 = from_qiskit(qc)
        assert c2.num_qubits == 2

    def test_from_qiskit_various_gates(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(3)
        qc.h(0)
        qc.x(1)
        qc.y(2)
        qc.z(0)
        qc.s(0)
        qc.t(1)
        qc.sdg(0)
        qc.tdg(1)
        qc.sx(0)
        qc.rx(1.0, 0)
        qc.ry(1.0, 1)
        qc.rz(1.0, 2)
        qc.cx(0, 1)
        qc.cz(0, 2)
        qc.swap(0, 1)
        qc.ccx(0, 1, 2)
        qc.measure_all()

        c = from_qiskit(qc)
        assert c.num_qubits == 3
        gate_names = [g.name for g in c.gates]
        assert "H" in gate_names
        assert "X" in gate_names
        assert "S" in gate_names
        assert "CX" in gate_names

    def test_from_qiskit_barrier_and_reset(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.barrier()
        qc.reset(0)
        qc.cx(0, 1)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "BARRIER" in gate_names
        assert "RESET" in gate_names

    def test_to_qiskit_expanded_gates(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(3)
        c.ch(0, 1)
        c.crx(0, 1, 0.5)
        c.cry(0, 1, 0.5)
        c.crz(0, 1, 0.5)
        c.cp(0, 1, 0.5)
        c.cy(0, 1)
        c.ccx(0, 1, 2)
        c.cswap(0, 1, 2)

        qc = to_qiskit(c)
        assert qc.num_qubits == 3


# ═══════════════════════════════════════════════════════════════════
# cloud/__init__.py — CloudClient, errors, dataclasses
# ═══════════════════════════════════════════════════════════════════


class TestCloudErrors:
    """Test cloud error classes."""

    def test_cloud_error(self) -> None:
        from quantsdk.cloud import CloudError

        e = CloudError("test error", status_code=500, response={"detail": "fail"})
        assert str(e) == "test error"
        assert e.status_code == 500
        assert e.response == {"detail": "fail"}

    def test_authentication_error(self) -> None:
        from quantsdk.cloud import AuthenticationError

        e = AuthenticationError("bad key")
        assert "bad key" in str(e)

    def test_quota_exceeded_error(self) -> None:
        from quantsdk.cloud import QuotaExceededError

        e = QuotaExceededError("over limit")
        assert "over limit" in str(e)

    def test_job_not_found_error(self) -> None:
        from quantsdk.cloud import JobNotFoundError

        e = JobNotFoundError("no such job")
        assert "no such job" in str(e)


class TestCloudDataclasses:
    """Test cloud dataclasses."""

    def test_cloud_job(self) -> None:
        from quantsdk.cloud import CloudJob, JobStatus

        job = CloudJob(
            job_id="job-123",
            status=JobStatus.SUBMITTED,
            backend="ibm_brisbane",
            shots=1000,
        )
        assert job.job_id == "job-123"
        assert job.status == JobStatus.SUBMITTED

    def test_cloud_backend_info(self) -> None:
        from quantsdk.cloud import CloudBackendInfo

        info = CloudBackendInfo(
            name="ibm_brisbane",
            provider="ibm",
            num_qubits=127,
            status="online",
            is_simulator=False,
            queue_depth=5,
        )
        assert info.name == "ibm_brisbane"
        assert info.num_qubits == 127

    def test_usage_info(self) -> None:
        from quantsdk.cloud import UsageInfo

        usage = UsageInfo(
            tier="explorer",
            simulator_minutes_used=10,
            simulator_minutes_limit=60,
            qpu_tasks_used=2,
            qpu_tasks_limit=10,
        )
        assert usage.tier == "explorer"
        assert usage.simulator_minutes_used == 10

    def test_job_status_values(self) -> None:
        from quantsdk.cloud import JobStatus

        assert JobStatus.SUBMITTED.value == "submitted"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"


class TestCloudClient:
    """Test CloudClient with mocked HTTP."""

    def test_init_with_api_key(self) -> None:
        from quantsdk.cloud import CloudClient

        client = CloudClient(api_key="test-key-123")
        assert client.api_base == "https://api.thequantcloud.com/v1"

    def test_init_from_env(self) -> None:
        from quantsdk.cloud import CloudClient

        with patch.dict(os.environ, {"QUANTCLOUD_API_KEY": "env-key-456"}):
            client = CloudClient()
            assert client._api_key == "env-key-456"

    def test_init_no_key_raises(self) -> None:
        from quantsdk.cloud import AuthenticationError, CloudClient

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("os.path.exists", return_value=False),
            pytest.raises(AuthenticationError, match="No API key"),
        ):
            CloudClient()

    def test_get_session_creates_httpx(self) -> None:
        pytest.importorskip("httpx")
        from quantsdk.cloud import CloudClient

        client = CloudClient(api_key="test-key")
        session = client._get_session()
        assert session is not None
        client.close()

    def test_get_session_httpx_missing(self) -> None:
        from quantsdk.cloud import CloudClient

        client = CloudClient.__new__(CloudClient)
        client._api_key = "test"
        client._api_base = "https://example.com"
        client._timeout = 30
        client._session = None

        with patch.dict("sys.modules", {"httpx": None}), pytest.raises(
            ImportError, match="httpx"
        ):
            client._get_session()

    def test_context_manager(self) -> None:
        pytest.importorskip("httpx")
        from quantsdk.cloud import CloudClient

        with CloudClient(api_key="test-key") as client:
            assert client is not None
        # session closed after exit

    def test_close_no_session(self) -> None:
        from quantsdk.cloud import CloudClient

        client = CloudClient.__new__(CloudClient)
        client._session = None
        client.close()  # Should not raise

    @patch("httpx.Client")
    def test_request_success(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"job_id": "j-1", "status": "submitted"}

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        result = client._request("GET", "/jobs/j-1")
        assert result["job_id"] == "j-1"

    @patch("httpx.Client")
    def test_request_401_raises_auth_error(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import AuthenticationError, CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="bad-key")
        client._session = mock_session

        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client._request("GET", "/test")

    @patch("httpx.Client")
    def test_request_403_raises_quota_error(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, QuotaExceededError

        mock_response = MagicMock()
        mock_response.status_code = 403

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        with pytest.raises(QuotaExceededError):
            client._request("GET", "/test")

    @patch("httpx.Client")
    def test_request_404_raises_not_found(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, JobNotFoundError

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        with pytest.raises(JobNotFoundError):
            client._request("GET", "/jobs/nonexistent")

    @patch("httpx.Client")
    def test_request_500_raises_cloud_error(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, CloudError

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"error": "Internal server error"}

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        with pytest.raises(CloudError, match="Internal server error"):
            client._request("GET", "/test")

    @patch("httpx.Client")
    def test_request_network_error(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, CloudError

        mock_session = MagicMock()
        mock_session.request.side_effect = ConnectionError("network down")

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        with pytest.raises(CloudError, match="Request failed"):
            client._request("GET", "/test")

    @patch("httpx.Client")
    def test_submit(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, JobStatus

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "j-submit-1",
            "status": "submitted",
            "backend": "ibm_brisbane",
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        circuit = Circuit(2).h(0).cx(0, 1).measure_all()
        job = client.submit(circuit, shots=1000, backend="ibm_brisbane")
        assert job.job_id == "j-submit-1"
        assert job.status == JobStatus.SUBMITTED

    @patch("httpx.Client")
    def test_get_job(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, JobStatus

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "j-get-1",
            "status": "running",
            "backend": "ibm_brisbane",
            "shots": 1000,
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        job = client.get_job("j-get-1")
        assert job.job_id == "j-get-1"
        assert job.status == JobStatus.RUNNING

    @patch("httpx.Client")
    def test_get_result(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "counts": {"00": 500, "11": 500},
            "shots": 1000,
            "backend": "ibm_brisbane",
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        result = client.get_result("j-result-1")
        assert isinstance(result, Result)
        assert result.shots == 1000

    @patch("httpx.Client")
    def test_cancel_job(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient, JobStatus

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "j-cancel-1",
            "status": "cancelled",
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        job = client.cancel_job("j-cancel-1")
        assert job.status == JobStatus.CANCELLED

    @patch("httpx.Client")
    def test_list_backends(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "backends": [
                {"name": "ibm_brisbane", "provider": "ibm", "num_qubits": 127},
                {"name": "ionq_harmony", "provider": "ionq", "num_qubits": 11, "is_simulator": False},
            ]
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        backends = client.list_backends()
        assert len(backends) == 2
        assert backends[0].name == "ibm_brisbane"

    @patch("httpx.Client")
    def test_get_backend(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "ibm_brisbane",
            "provider": "ibm",
            "num_qubits": 127,
            "status": "online",
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        backend = client.get_backend("ibm_brisbane")
        assert backend.name == "ibm_brisbane"
        assert backend.num_qubits == 127

    @patch("httpx.Client")
    def test_get_usage(self, mock_client_cls: MagicMock) -> None:
        from quantsdk.cloud import CloudClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tier": "developer",
            "simulator_minutes_used": 30,
            "simulator_minutes_limit": 300,
            "qpu_tasks_used": 5,
            "qpu_tasks_limit": 100,
            "credits_remaining_usd": 45.0,
        }

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        client = CloudClient(api_key="test-key")
        client._session = mock_session

        usage = client.get_usage()
        assert usage.tier == "developer"
        assert usage.simulator_minutes_used == 30


# ═══════════════════════════════════════════════════════════════════
# cloud/config.py — QuantCloudConfig load/save
# ═══════════════════════════════════════════════════════════════════


class TestCloudConfig:
    """Test CloudConfig load and save."""

    def test_load_from_env(self) -> None:
        from quantsdk.cloud.config import CloudConfig

        with patch.dict(
            os.environ,
            {
                "QUANTCLOUD_API_KEY": "env-key-test",
                "QUANTCLOUD_API_BASE": "https://custom.api.com",
            },
        ):
            config = CloudConfig.load()
            assert config.api_key == "env-key-test"
            assert config.api_base == "https://custom.api.com"

    def test_load_defaults_no_env(self) -> None:
        from quantsdk.cloud.config import CloudConfig

        config = CloudConfig()
        assert config.api_base == "https://api.thequantcloud.com/v1"
        assert config.default_shots == 1024

    def test_save_and_load_roundtrip(self) -> None:
        from pathlib import Path

        from quantsdk.cloud.config import CloudConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, ".quantcloud")
            config_file = os.path.join(config_dir, "config.json")
            cred_file = os.path.join(config_dir, "credentials")

            with (
                patch("quantsdk.cloud.config._CONFIG_DIR", Path(config_dir)),
                patch("quantsdk.cloud.config._CONFIG_FILE", Path(config_file)),
                patch("quantsdk.cloud.config._CREDENTIALS_FILE", Path(cred_file)),
            ):
                config = CloudConfig()
                config.api_key = "save-test-key"
                config.api_base = "https://saved.api.com"
                config.default_shots = 4096
                config.save()

                assert os.path.exists(config_file)
                assert os.path.exists(cred_file)

                with open(config_file) as f:
                    data = json.load(f)
                assert data["api_base"] == "https://saved.api.com"
                assert data["default_shots"] == 4096

                with open(cred_file) as f:
                    content = f.read()
                assert "save-test-key" in content

    def test_default_values(self) -> None:
        from quantsdk.cloud.config import CloudConfig

        config = CloudConfig()
        assert config.api_base == "https://api.thequantcloud.com/v1"
        assert config.default_shots == 1024
        assert config.timeout == 30.0


# ═══════════════════════════════════════════════════════════════════
# backends/ibm.py — mock-based coverage
# ═══════════════════════════════════════════════════════════════════


class TestIBMBackendMocked:
    """Cover IBMBackend paths with mocks."""

    def test_check_ibm_deps_passes(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.backends.ibm import _check_ibm_deps

        _check_ibm_deps()

    def test_check_aer_passes(self) -> None:
        pytest.importorskip("qiskit_aer")
        from quantsdk.backends.ibm import _check_aer

        _check_aer()

    def test_aer_backend_method(self) -> None:
        pytest.importorskip("qiskit_aer")
        from quantsdk.backends.ibm import AerBackend

        backend = AerBackend(method="statevector")
        info = backend.info()
        assert info.is_simulator is True

    def test_aer_backend_name_property(self) -> None:
        pytest.importorskip("qiskit_aer")
        from quantsdk.backends.ibm import AerBackend

        backend = AerBackend()
        assert backend.name == "aer_simulator"


# ═══════════════════════════════════════════════════════════════════
# Additional from_qiskit coverage for expanded gate types
# ═══════════════════════════════════════════════════════════════════


class TestFromQiskitExpanded:
    """Cover from_qiskit with more gate types (lines 362-449)."""

    def test_from_qiskit_parametric_gates(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.p(0.5, 0)       # PhaseGate
        qc.rx(1.0, 0)      # RX
        qc.ry(1.5, 1)      # RY
        qc.rz(2.0, 0)      # RZ
        qc.u(1.0, 2.0, 3.0, 0)  # U3

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "P" in gate_names
        assert "RX" in gate_names
        assert "RY" in gate_names
        assert "RZ" in gate_names
        assert "U3" in gate_names

    def test_from_qiskit_controlled_parametric(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.crx(1.0, 0, 1)
        qc.cry(1.0, 0, 1)
        qc.crz(1.0, 0, 1)
        qc.cp(0.5, 0, 1)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "CRX" in gate_names
        assert "CRY" in gate_names
        assert "CRZ" in gate_names
        assert "CP" in gate_names

    def test_from_qiskit_two_qubit_no_params(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.cx(0, 1)
        qc.cz(0, 1)
        qc.cy(0, 1)
        qc.ch(0, 1)
        qc.swap(0, 1)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "CX" in gate_names
        assert "CZ" in gate_names
        assert "CY" in gate_names
        assert "CH" in gate_names
        assert "SWAP" in gate_names

    def test_from_qiskit_three_qubit_gates(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(3)
        qc.ccx(0, 1, 2)
        qc.ccz(0, 1, 2)
        qc.cswap(0, 1, 2)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "CCX" in gate_names
        assert "CCZ" in gate_names
        assert "CSWAP" in gate_names

    def test_from_qiskit_rotation_gates(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.rxx(0.5, 0, 1)
        qc.ryy(0.5, 0, 1)
        qc.rzz(0.5, 0, 1)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "RXX" in gate_names
        assert "RYY" in gate_names
        assert "RZZ" in gate_names

    def test_from_qiskit_identity_gate(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(1)
        qc.id(0)

        c = from_qiskit(qc)
        gate_names = [g.name for g in c.gates]
        assert "I" in gate_names

    def test_from_qiskit_unsupported_gate(self) -> None:
        pytest.importorskip("qiskit")
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import XXMinusYYGate

        from quantsdk.interop.qiskit_interop import from_qiskit

        qc = QuantumCircuit(2)
        qc.append(XXMinusYYGate(0.5), [0, 1])

        with pytest.raises(ValueError, match="Unsupported"):
            from_qiskit(qc)


# ═══════════════════════════════════════════════════════════════════
# Additional to_qiskit coverage for expanded gates
# ═══════════════════════════════════════════════════════════════════


class TestToQiskitExpanded:
    """Cover to_qiskit() with expanded gate types."""

    def test_to_qiskit_sdg_tdg_sx_sxdg(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(1).sdg(0).tdg(0).sx(0).sxdg(0)
        qc = to_qiskit(c)
        assert qc.num_qubits == 1

    def test_to_qiskit_phase_u1(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(1).p(0, 0.5).u1(0, 0.5)
        qc = to_qiskit(c)
        assert qc.num_qubits == 1

    def test_to_qiskit_u2_r(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(1).u2(0, 0.5, 1.0).r(0, 0.5, 1.0)
        qc = to_qiskit(c)
        assert qc.num_qubits == 1

    def test_to_qiskit_cy_ch_cs_csdg(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(2).cy(0, 1).ch(0, 1).cs(0, 1).csdg(0, 1)
        qc = to_qiskit(c)
        assert qc.num_qubits == 2

    def test_to_qiskit_controlled_rotations(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(2).crx(0, 1, 0.5).cry(0, 1, 0.5).crz(0, 1, 0.5).cp(0, 1, 0.5)
        qc = to_qiskit(c)
        assert qc.num_qubits == 2

    def test_to_qiskit_cu1_cu3_csx(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(2).cu1(0, 1, 0.5).cu3(0, 1, 0.5, 1.0, 1.5).csx(0, 1)
        qc = to_qiskit(c)
        assert qc.num_qubits == 2

    def test_to_qiskit_rxx_ryy_rzz_rzx(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(2).rxx(0, 1, 0.5).ryy(0, 1, 0.5).rzz(0, 1, 0.5).rzx(0, 1, 0.5)
        qc = to_qiskit(c)
        assert qc.num_qubits == 2

    def test_to_qiskit_iswap_dcx_ecr(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(2).iswap(0, 1).dcx(0, 1).ecr(0, 1)
        qc = to_qiskit(c)
        assert qc.num_qubits == 2

    def test_to_qiskit_ccz_fredkin(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(3).ccz(0, 1, 2).cswap(0, 1, 2)
        qc = to_qiskit(c)
        assert qc.num_qubits == 3

    def test_to_qiskit_reset(self) -> None:
        pytest.importorskip("qiskit")
        from quantsdk.interop.qiskit_interop import to_qiskit

        c = Circuit(1).x(0).reset(0)
        qc = to_qiskit(c)
        ops = [inst.operation.name for inst in qc.data]
        assert "reset" in ops


# ═══════════════════════════════════════════════════════════════════
# cloud/config.py — load from config file
# ═══════════════════════════════════════════════════════════════════


class TestCloudConfigFile:
    """Cover CloudConfig.load() from files."""

    def test_load_from_config_file(self) -> None:
        from pathlib import Path

        from quantsdk.cloud.config import CloudConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            cred_file = Path(tmpdir) / "credentials"

            config_data = {"api_base": "https://custom.api.com", "default_shots": 2048}
            config_file.write_text(json.dumps(config_data))
            cred_file.write_text("api_key=file-key-test\n")

            with (
                patch("quantsdk.cloud.config._CONFIG_FILE", config_file),
                patch("quantsdk.cloud.config._CREDENTIALS_FILE", cred_file),
                patch.dict(os.environ, {}, clear=True),
            ):
                config = CloudConfig.load()
                assert config.api_base == "https://custom.api.com"
                assert config.default_shots == 2048
                assert config.api_key == "file-key-test"

    def test_load_env_overrides_file(self) -> None:
        from pathlib import Path

        from quantsdk.cloud.config import CloudConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            cred_file = Path(tmpdir) / "credentials"

            config_data = {"api_base": "https://file.api.com"}
            config_file.write_text(json.dumps(config_data))
            cred_file.write_text("api_key=file-key\n")

            with (
                patch("quantsdk.cloud.config._CONFIG_FILE", config_file),
                patch("quantsdk.cloud.config._CREDENTIALS_FILE", cred_file),
                patch.dict(os.environ, {"QUANTCLOUD_API_KEY": "env-key", "QUANTCLOUD_API_BASE": "https://env.api.com"}),
            ):
                config = CloudConfig.load()
                # Env should override
                assert config.api_key == "env-key"
                assert config.api_base == "https://env.api.com"

    def test_load_bad_json(self) -> None:
        from pathlib import Path

        from quantsdk.cloud.config import CloudConfig

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            cred_file = Path(tmpdir) / "credentials"

            config_file.write_text("not valid json!!!")

            with (
                patch("quantsdk.cloud.config._CONFIG_FILE", config_file),
                patch("quantsdk.cloud.config._CREDENTIALS_FILE", cred_file),
                patch.dict(os.environ, {}, clear=True),
            ):
                # Should not crash, just use defaults
                config = CloudConfig.load()
                assert config.api_base == "https://api.thequantcloud.com/v1"
