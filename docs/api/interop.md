# Interop

QuantSDK circuits can be seamlessly converted to and from other quantum
frameworks — enabling you to leverage existing tooling while staying
framework-agnostic.

## Supported Frameworks

| Framework | Import | Export | Status |
|-----------|--------|--------|--------|
| Qiskit | :material-check-circle:{ style="color: green" } | :material-check-circle:{ style="color: green" } | Available |
| OpenQASM 2.0 | :material-check-circle:{ style="color: green" } | :material-check-circle:{ style="color: green" } | Available |
| Cirq | :material-clock-outline:{ style="color: orange" } | :material-clock-outline:{ style="color: orange" } | v0.2 |
| PennyLane | :material-clock-outline:{ style="color: orange" } | :material-clock-outline:{ style="color: orange" } | v0.2 |

## Quick Usage

### Via Circuit Convenience Methods

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# Export
qc = circuit.to_qiskit()         # -> qiskit.QuantumCircuit
qasm = circuit.to_openqasm()     # -> str (OpenQASM 2.0)

# Import
circuit2 = qs.Circuit.from_qiskit(qc)
circuit3 = qs.Circuit.from_openqasm(qasm)
```

### Via Interop Module

```python
from quantsdk.interop import to_qiskit, from_qiskit, to_openqasm, from_openqasm

# Export
qc = to_qiskit(circuit)
qasm_str = to_openqasm(circuit)

# Import
circuit = from_qiskit(qc)
circuit = from_openqasm(qasm_str)
```

## Qiskit Interop

### `to_qiskit`

::: quantsdk.interop.qiskit_interop.to_qiskit
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### `from_qiskit`

::: quantsdk.interop.qiskit_interop.from_qiskit
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Gate Mapping

All 50+ QuantSDK gates are mapped to their Qiskit equivalents:

| QuantSDK | Qiskit |
|----------|--------|
| `HGate` | `qiskit.circuit.library.HGate` |
| `CXGate` | `qiskit.circuit.library.CXGate` |
| `RZGate(theta)` | `qiskit.circuit.library.RZGate(theta)` |
| `ToffoliGate` | `qiskit.circuit.library.CCXGate` |
| ... | ... |

## OpenQASM Interop

### `to_openqasm`

::: quantsdk.interop.openqasm.to_openqasm
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### `from_openqasm`

::: quantsdk.interop.openqasm.from_openqasm
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Supported QASM Gates

The OpenQASM exporter supports all standard `qelib1.inc` gates plus custom
gate definitions for QuantSDK-specific gates.

```
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
```

## Notes

- **Qiskit interop** requires `pip install quantsdk[interop]` (or `quantsdk[ibm]`)
- **OpenQASM interop** requires `pip install quantsdk[interop]` (uses Qiskit's QASM parser for import)
- Gate parameters (rotation angles) are preserved exactly during round-trips
- Measurement mappings are preserved during conversion
- Circuit names are carried over when available
