# Running on Real Hardware

QuantSDK makes it easy to go from simulation to real quantum processors.

## Supported Backends

| Backend | Provider | Type | Status |
|---------|----------|------|--------|
| `local` | Built-in | Simulator | :material-check-circle:{ style="color: green" } Available |
| `aer` | IBM (Qiskit Aer) | Simulator | :material-check-circle:{ style="color: green" } Available |
| `ibm_*` | IBM Quantum | Real QPU | :material-check-circle:{ style="color: green" } Available |
| `ionq_*` | IonQ | Real QPU | :material-clock-outline:{ style="color: orange" } v0.2 |

## IBM Quantum Setup

### 1. Get an API Token

1. Create a free account at [quantum.ibm.com](https://quantum.ibm.com)
2. Navigate to your account settings
3. Copy your API token

### 2. Install IBM Dependencies

```bash
pip install quantsdk[ibm]
```

### 3. Run on IBM Quantum

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# Run on a real IBM quantum processor
result = qs.run(
    circuit,
    backend="ibm_brisbane",
    shots=1000,
    token="your-ibm-token"
)

print(result.counts)
```

## Using the IBM Backend Directly

For more control, use the `IBMBackend` class directly:

```python
from quantsdk.backends.ibm import IBMBackend

# Initialize with your token
backend = IBMBackend(
    token="your-ibm-token",
    instance="ibm-q/open/main"  # optional
)

# Check backend info
info = backend.info()
print(f"Name: {info.name}")
print(f"Qubits: {info.num_qubits}")
print(f"Status: {backend.status()}")

# Run a circuit
circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = backend.run(circuit, shots=1000)
```

## Using Aer Simulator

IBM's Aer is a high-performance local simulator with noise models:

```python
from quantsdk.backends.ibm import AerBackend

# Initialize (no token needed)
aer = AerBackend()

# Run with Aer
circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = aer.run(circuit, shots=4096)
print(result.counts)
```

Or use the shortcut:

```python
result = qs.run(circuit, backend="aer", shots=4096)
```

## Backend Routing

`qs.run()` automatically routes to the right backend:

```python
# Local simulator (default, no deps needed)
result = qs.run(circuit, shots=1000)
result = qs.run(circuit, backend="local", shots=1000)

# Aer simulator (needs qiskit-aer)
result = qs.run(circuit, backend="aer", shots=1000)

# IBM Quantum (needs ibm extras + token)
result = qs.run(circuit, backend="ibm_brisbane", shots=1000, token="...")
```

## Tips for Real Hardware

### Circuit Optimization

Real quantum processors have limited connectivity and gate sets. Keep circuits
shallow for best results:

```python
# Good: Simple, shallow circuit
circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# Less ideal: Deep circuit with many gates
# (hardware noise accumulates with depth)
```

### Shot Count

More shots = more statistical accuracy, but also more QPU time:

```python
# Quick test
result = qs.run(circuit, backend="ibm_brisbane", shots=100, token="...")

# Production run
result = qs.run(circuit, backend="ibm_brisbane", shots=8192, token="...")
```

### Qubit Count

Current QPUs have limited qubits. Check backend capabilities:

```python
from quantsdk.backends.ibm import IBMBackend

backend = IBMBackend(token="...")
info = backend.info()
print(f"Max qubits: {info.num_qubits}")
```

## What's Next?

- **[Backend Guides](../backends/index.md)** — Detailed backend documentation
- **[Tutorials](../tutorials/index.md)** — Quantum computing tutorials
- **[API Reference](../api/index.md)** — Full API documentation
