# Custom Backend

Build your own backend to integrate any quantum hardware or simulator with
QuantSDK.

## The Backend Interface

Every backend must implement the `Backend` abstract base class:

```python
from quantsdk.backend import Backend, BackendInfo, BackendStatus
from quantsdk.circuit import Circuit
from quantsdk.result import Result


class MyBackend(Backend):
    """A custom quantum backend."""

    def run(self, circuit: Circuit, shots: int = 1024, **options) -> Result:
        """Execute a circuit and return results."""
        # 1. Convert QuantSDK circuit to your format
        native_circuit = self._translate(circuit)

        # 2. Execute on your hardware/simulator
        raw_results = self._execute(native_circuit, shots)

        # 3. Convert results back to QuantSDK format
        return Result(
            counts=raw_results,
            shots=shots,
            backend=self.name,
        )

    def info(self) -> BackendInfo:
        """Return backend metadata."""
        return BackendInfo(
            name="my_backend",
            provider="my_company",
            num_qubits=20,
            status=BackendStatus.ONLINE,
            is_simulator=False,
            native_gates=frozenset({"h", "cx", "rz", "x"}),
            max_shots=100_000,
        )

    def _translate(self, circuit: Circuit):
        """Convert QuantSDK circuit to native format."""
        for gate in circuit.gates:
            gate_obj, qubits, params = gate
            # Process each gate...
        return native_circuit

    def _execute(self, native_circuit, shots: int) -> dict[str, int]:
        """Run on hardware and return counts."""
        # Your execution logic here
        return {"00": 512, "11": 488}
```

## Step-by-Step Guide

### 1. Implement `run()`

The `run()` method is the core of your backend:

```python
def run(self, circuit: Circuit, shots: int = 1024, **options) -> Result:
    # Access circuit gates
    for gate_obj, qubits, params in circuit.gates:
        print(f"Gate: {gate_obj.name}, Qubits: {qubits}, Params: {params}")

    # gate_obj is a Gate instance with:
    #   .name     - string name (e.g., "H", "CX", "RZ")
    #   .qubits   - tuple of qubit indices
    #   .params   - tuple of float parameters
    #   .matrix() - unitary matrix (numpy array)

    # ... execute and collect results ...

    return Result(
        counts={"00": 500, "11": 500},
        shots=shots,
        backend="my_backend",
        job_id="job-12345",
        metadata={"execution_time": 0.5},
    )
```

### 2. Implement `info()`

```python
def info(self) -> BackendInfo:
    return BackendInfo(
        name="my_backend",
        provider="my_company",
        num_qubits=20,
        status=BackendStatus.ONLINE,
        is_simulator=False,
        native_gates=frozenset({"h", "cx", "rz", "x", "sx"}),
        max_shots=100_000,
        queue_depth=0,
        metadata={
            "version": "1.0",
            "connectivity": "heavy-hex",
        },
    )
```

### 3. Register with `qs.run()` (Optional)

Currently, custom backends are used directly. Integration with `qs.run()`
routing is coming in v0.2:

```python
# Direct usage (current)
backend = MyBackend()
result = backend.run(circuit, shots=1000)

# Via qs.run() (coming in v0.2)
# qs.register_backend("my_backend", MyBackend)
# result = qs.run(circuit, backend="my_backend", shots=1000)
```

## Using Interop for Translation

Leverage QuantSDK's interop to convert circuits:

```python
from quantsdk.interop import to_qiskit, to_openqasm

class QiskitWrapperBackend(Backend):
    def run(self, circuit: Circuit, shots: int = 1024, **options) -> Result:
        # Convert to Qiskit
        qc = to_qiskit(circuit)

        # Use any Qiskit-compatible backend
        from qiskit_aer import AerSimulator
        sim = AerSimulator()
        job = sim.run(qc, shots=shots)
        qiskit_result = job.result()
        counts = qiskit_result.get_counts()

        return Result(counts=counts, shots=shots, backend="qiskit-wrapper")
```

## Testing Your Backend

```python
import quantsdk as qs
from my_backend import MyBackend

backend = MyBackend()

# Test 1: Simple circuit
circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = backend.run(circuit, shots=1000)
assert sum(result.counts.values()) == 1000

# Test 2: Backend info
info = backend.info()
assert info.num_qubits >= 2
assert info.status == BackendStatus.ONLINE

# Test 3: All gate types
from quantsdk.gates import GATE_MAP
# Ensure your backend handles all gates it claims to support
```

## Best Practices

1. **Validate circuits** before execution (check qubit count, gate support)
2. **Return accurate metadata** in `BackendInfo`
3. **Handle errors gracefully** with informative error messages
4. **Support the `seed` parameter** for simulators
5. **Document limitations** (max qubits, supported gates, etc.)
