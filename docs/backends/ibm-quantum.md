# IBM Quantum

Run QuantSDK circuits on IBM Quantum processors and the Aer simulator.

## Setup

### 1. Install Dependencies

```bash
pip install quantsdk[ibm]
```

This installs `qiskit`, `qiskit-ibm-runtime`, and `qiskit-aer`.

### 2. Get an API Token

1. Create a free account at [quantum.ibm.com](https://quantum.ibm.com)
2. Go to your account settings
3. Copy your API token

## IBM Quantum Hardware

### Quick Start

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

result = qs.run(
    circuit,
    backend="ibm_brisbane",
    shots=4096,
    token="your-ibm-token"
)
print(result.counts)
```

### Advanced Usage

```python
from quantsdk.backends.ibm import IBMBackend

backend = IBMBackend(
    token="your-ibm-token",
    backend_name="ibm_brisbane",
    instance="ibm-q/open/main",
    channel="ibm_quantum_platform"
)

# Check status
info = backend.info()
print(f"Backend: {info.name}")
print(f"Qubits: {info.num_qubits}")
print(f"Status: {info.status}")

# Run
result = backend.run(circuit, shots=4096)
```

### Available Systems

IBM regularly updates their fleet. Common systems include:

| System | Qubits | Processor | Access |
|--------|--------|-----------|--------|
| ibm_brisbane | 127 | Eagle r3 | Open |
| ibm_osaka | 127 | Eagle r3 | Open |
| ibm_kyoto | 127 | Eagle r3 | Open |

Check [quantum.ibm.com](https://quantum.ibm.com) for the current list.

## Aer Simulator

Qiskit Aer provides high-performance local simulation with noise models.

### Quick Start

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# Via qs.run()
result = qs.run(circuit, backend="aer", shots=4096)

# With seed
result = qs.run(circuit, backend="aer", shots=4096, seed=42)
```

### Direct Usage

```python
from quantsdk.backends.ibm import AerBackend

aer = AerBackend(method="automatic")

info = aer.info()
print(f"Max qubits: {info.num_qubits}")

result = aer.run(circuit, shots=4096, seed=42)
```

### Simulation Methods

| Method | Description | Best For |
|--------|-------------|----------|
| `automatic` | Auto-selects best method | Default |
| `statevector` | Full state vector | Small circuits |
| `density_matrix` | Density matrix | Noise simulation |
| `matrix_product_state` | MPS | Deep circuits |

## Best Practices

### 1. Start Local, Then Go Real

```python
# Development: local simulator
result = qs.run(circuit, shots=100)

# Validation: Aer with noise
result = qs.run(circuit, backend="aer", shots=4096)

# Production: real hardware
result = qs.run(circuit, backend="ibm_brisbane", shots=8192, token="...")
```

### 2. Keep Circuits Shallow

Hardware noise accumulates with circuit depth. Aim for:

- **< 100 two-qubit gates** for useful results
- **Minimize SWAP insertions** by matching your circuit to hardware topology
- **Use barriers** to prevent unwanted optimization

### 3. Use Enough Shots

More shots = better statistics, but more QPU time:

| Shots | Precision | Use Case |
|-------|-----------|----------|
| 100 | ~10% | Quick test |
| 1,024 | ~3% | Default |
| 4,096 | ~1.5% | Good results |
| 8,192 | ~1% | Production |

### 4. Handle Queue Times

IBM Quantum has job queues. For time-sensitive work:

- Use off-peak hours (US nighttime)
- Use the Aer simulator for development
- Consider IBM Premium plans for priority access

## Troubleshooting

### "No module named 'qiskit'"

```bash
pip install quantsdk[ibm]
```

### "Invalid API token"

Verify your token at [quantum.ibm.com](https://quantum.ibm.com) and ensure
you're using the correct channel:

```python
backend = IBMBackend(
    token="your-token",
    channel="ibm_quantum_platform"  # or "ibm_cloud"
)
```

### "Backend not available"

The system may be in maintenance. Check status at
[quantum.ibm.com](https://quantum.ibm.com) or try a different backend.
