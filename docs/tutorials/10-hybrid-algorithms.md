# Tutorial 10: Hybrid Quantum-Classical Algorithms

**Time:** 30 minutes  
**Level:** Advanced  
**Concepts:** Parameterized circuits, classical optimization loop, gradient estimation

## Overview

Hybrid algorithms combine quantum and classical processing in a loop:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│ Parameterize│────>│ Run Quantum  │────>│ Classical         │
│ Circuit     │     │ Circuit      │     │ Optimizer         │
│ theta       │<────│ <O>(theta)   │<────│ theta' = update() │
└─────────────┘     └──────────────┘     └──────────────────┘
```

This pattern underlies VQE, QAOA, quantum machine learning, and more.

## Building a Parameter Sweep

```python
import quantsdk as qs
import math

def parameterized_circuit(theta: float) -> qs.Circuit:
    """Create a circuit parameterized by theta."""
    circuit = qs.Circuit(2, name=f"param-theta={theta:.2f}")
    circuit.h(0)
    circuit.ry(1, theta)
    circuit.cx(0, 1)
    circuit.measure_all()
    return circuit

# Sweep theta and observe how results change
for theta in [0, math.pi/4, math.pi/2, math.pi]:
    circuit = parameterized_circuit(theta)
    result = qs.run(circuit, shots=1000)
    print(f"theta={theta:.2f}: {result.counts}")
```

## Gradient Estimation

The **parameter shift rule** lets us estimate gradients of quantum circuits:

$$\frac{\partial \langle O \rangle}{\partial \theta} = \frac{\langle O \rangle_{\theta + \pi/2} - \langle O \rangle_{\theta - \pi/2}}{2}$$

```python
import quantsdk as qs
import math

def expectation_z(theta: float, shots: int = 4096) -> float:
    """Measure <Z> for a parameterized circuit."""
    circuit = qs.Circuit(1, name="param")
    circuit.ry(0, theta)
    circuit.measure(0)
    result = qs.run(circuit, shots=shots)

    # <Z> = P(0) - P(1)
    p0 = result.counts.get('0', 0) / shots
    p1 = result.counts.get('1', 0) / shots
    return p0 - p1

def parameter_shift_gradient(theta: float) -> float:
    """Estimate gradient using parameter shift rule."""
    shift = math.pi / 2
    return (expectation_z(theta + shift) - expectation_z(theta - shift)) / 2

# Gradient descent to minimize <Z> (find theta = pi, giving |1>)
theta = 0.1  # Initial guess
learning_rate = 0.5

print(f"Goal: Find theta that minimizes <Z>")
print(f"Expected: theta = pi (state |1>, <Z> = -1)")
print()

for step in range(20):
    grad = parameter_shift_gradient(theta)
    exp_z = expectation_z(theta)

    if step % 5 == 0:
        print(f"Step {step:2d}: theta={theta:.3f}, <Z>={exp_z:.3f}, grad={grad:.3f}")

    theta -= learning_rate * grad

print(f"\nFinal: theta={theta:.3f} (expected: {math.pi:.3f})")
print(f"Final <Z>: {expectation_z(theta):.3f} (expected: -1.000)")
```

## Quantum Machine Learning Pattern

```python
import quantsdk as qs
import math

def quantum_classifier(features: list[float], weights: list[float]) -> qs.Circuit:
    """A simple quantum classifier.

    Args:
        features: Input data (2 features).
        weights: Trainable parameters (4 weights).
    """
    circuit = qs.Circuit(2, name="q-classifier")

    # Data encoding layer
    circuit.ry(0, features[0])
    circuit.ry(1, features[1])

    # Trainable layer 1
    circuit.ry(0, weights[0])
    circuit.ry(1, weights[1])
    circuit.cx(0, 1)

    # Trainable layer 2
    circuit.ry(0, weights[2])
    circuit.ry(1, weights[3])

    circuit.measure_all()
    return circuit

# Example: classify a data point
features = [0.5, 1.2]
weights = [0.1, 0.3, 0.5, 0.7]

circuit = quantum_classifier(features, weights)
result = qs.run(circuit, shots=1000)

# Interpret: probability of measuring |00> = class 0, else class 1
p_class_0 = result.counts.get('00', 0) / 1000
print(f"P(class 0) = {p_class_0:.3f}")
print(f"P(class 1) = {1 - p_class_0:.3f}")
```

## Design Patterns

### 1. Variational Ansatz Pattern

```python
def variational_layer(circuit, params, layer_idx):
    """Add a variational layer to a circuit."""
    n = circuit.num_qubits
    offset = layer_idx * n

    # Single-qubit rotations
    for i in range(n):
        circuit.ry(i, params[offset + i])

    # Entangling layer
    for i in range(n - 1):
        circuit.cx(i, i + 1)

    return circuit
```

### 2. Measurement and Post-Processing

```python
def expectation_value(circuit, observable, shots=4096):
    """Estimate expectation value of an observable."""
    circuit_copy = circuit.copy()
    circuit_copy.measure_all()
    result = qs.run(circuit_copy, shots=shots)

    # Post-process based on observable type
    exp_val = 0.0
    for bitstring, count in result.counts.items():
        eigenvalue = observable(bitstring)
        exp_val += eigenvalue * count / shots
    return exp_val
```

## Key Takeaways

1. **Hybrid algorithms** are the dominant paradigm for near-term quantum computing
2. The **parameter shift rule** gives exact gradients (not finite differences)
3. **Shot noise** limits precision — more shots = less noise = slower
4. **Barren plateaus** can make optimization hard for deep circuits
5. QuantSDK's fluent API makes it easy to build parameterized circuits

## What's Next?

Congratulations! You've completed all 10 tutorials. Here are some next steps:

- **[API Reference](../api/index.md)** — explore the full API
- **[Backend Guides](../backends/index.md)** — run on real hardware
- **[Contributing](../contributing.md)** — help build QuantSDK
