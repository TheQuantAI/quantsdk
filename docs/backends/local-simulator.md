# Local Simulator

The built-in local simulator uses pure NumPy tensor contraction to simulate
quantum circuits. No external dependencies required.

## Features

| Feature | Support |
|---------|---------|
| Max qubits | 24 |
| Noise model | No |
| Deterministic seed | Yes |
| GPU acceleration | No |
| Dependencies | None (NumPy only) |

## Usage

### Via `qs.run()` (Recommended)

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()

# Default (no backend specified = local)
result = qs.run(circuit, shots=1000)

# Explicit
result = qs.run(circuit, backend="local", shots=1000)

# With seed for reproducibility
result = qs.run(circuit, backend="local", shots=1000, seed=42)
```

### Direct Instantiation

```python
from quantsdk.simulators.local import LocalSimulator

sim = LocalSimulator()

# Backend info
info = sim.info()
print(f"Name: {info.name}")           # local_simulator
print(f"Provider: {info.provider}")    # quantsdk
print(f"Qubits: {info.num_qubits}")   # 24
print(f"Simulator: {info.is_simulator}") # True

# Run
result = sim.run(circuit, shots=1000, seed=42)
print(result.counts)
```

## How It Works

The simulator represents the quantum state as a complex vector of size $2^n$
(where $n$ is the number of qubits) and applies gate operations via tensor
contraction:

1. **State initialization:** $|\psi\rangle = |00\ldots0\rangle$
2. **Gate application:** For each gate, compute the tensor product of the gate
   matrix with identity matrices and multiply with the state vector
3. **Measurement:** Sample from the probability distribution $|a_i|^2$

## Performance

| Qubits | State Vector Size | Memory | Time (1000 shots) |
|--------|-------------------|--------|--------------------|
| 10 | 1,024 | ~16 KB | < 0.01s |
| 15 | 32,768 | ~512 KB | ~0.05s |
| 20 | 1,048,576 | ~16 MB | ~1s |
| 24 | 16,777,216 | ~256 MB | ~10s |
| 25+ | — | > 512 MB | Not supported |

## Limitations

- **24 qubit maximum** — memory scales as $O(2^n)$
- **No noise model** — use Aer for realistic noise simulation
- **CPU only** — use GPU backend for larger circuits
- **No mid-circuit measurement** — all measurements must be at the end

## Supported Gates

All 50+ QuantSDK gates are supported by the local simulator. Each gate class
implements a `matrix()` method returning its unitary, which the simulator
applies to the state vector.

## Reproducibility

Use the `seed` parameter for deterministic results:

```python
result1 = qs.run(circuit, shots=100, seed=42)
result2 = qs.run(circuit, shots=100, seed=42)
assert result1.counts == result2.counts  # Identical!
```
