# Circuit Analysis

`analyze_circuit()` extracts routing- and telemetry-relevant features from a
QuantSDK circuit — the same metrics QuantRouter uses for backend selection and
that the cloud platform logs for ML training. It is a pure, read-only analysis
of a circuit (no execution).

## Usage

```python
import quantsdk as qs

circuit = (
    qs.Circuit(3, name="ghz")
    .h(0)
    .cx(0, 1)
    .cx(0, 2)
    .measure_all()
)

features = qs.analyze_circuit(circuit)

print(features.qubit_count)   # 3
print(features.depth)         # circuit depth
print(features.cx_count)      # 2
print(features.algorithm_class)
```

Both names are top-level public API:

```python
from quantsdk import analyze_circuit, CircuitFeatures
```

They also remain available via the router submodule (`qs.router.analyze_circuit`).

## `CircuitFeatures`

A frozen dataclass returned by `analyze_circuit()`.

| Field | Type | Description |
|---|---|---|
| `qubit_count` | `int` | Number of qubits in the circuit. |
| `gate_count` | `int` | Total number of gates. |
| `depth` | `int` | Circuit depth (longest input→output path). |
| `cx_count` | `int` | Number of two-qubit (entangling) gates. |
| `gate_types` | `frozenset[str]` | Set of gate type names used. |
| `single_qubit_gates` | `int` | Count of single-qubit gates. |
| `two_qubit_gates` | `int` | Count of two-qubit gates. |
| `three_qubit_gates` | `int` | Count of three-qubit gates. |
| `measurement_count` | `int` | Number of measurement operations. |
| `has_parameterized_gates` | `bool` | Whether the circuit has rotation gates. |
| `algorithm_class` | `AlgorithmClass` | Detected algorithm class (e.g. entangling, variational). |
| `connectivity` | `frozenset[tuple[int, int]]` | Qubit pairs that interact via 2-qubit gates. |

Because it is frozen, a `CircuitFeatures` instance is hashable and safe to cache
or log.
