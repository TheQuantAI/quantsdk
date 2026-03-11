# Tutorial 8: Variational Quantum Eigensolver (VQE)

**Time:** 30 minutes  
**Level:** Advanced  
**Concepts:** Hybrid quantum-classical algorithms, parameterized circuits, optimization

!!! tip "Try it interactively"
    This tutorial is also available as a Jupyter notebook you can run locally:  
    [:material-notebook: Open `15_vqe.ipynb`](https://github.com/TheQuantAI/quantsdk/blob/main/examples/15_vqe.ipynb){ .md-button }

## What is VQE?

The **Variational Quantum Eigensolver** finds the ground state energy of a
quantum system (like a molecule) using a hybrid approach:

1. **Quantum computer:** Prepares a parameterized trial state and measures energy
2. **Classical computer:** Optimizes the parameters to minimize energy

This is a **NISQ-era** algorithm — designed to work on near-term noisy hardware.

## The Variational Principle

For any trial state $|\psi(\theta)\rangle$:

$$E(\theta) = \langle\psi(\theta)|H|\psi(\theta)\rangle \geq E_0$$

where $E_0$ is the true ground state energy. By minimizing $E(\theta)$,
we approach $E_0$.

## Implementation: Simple 2-Qubit VQE

We'll find the ground state of a simple Hamiltonian:
$H = Z_0 Z_1 + 0.5 X_0 + 0.5 X_1$

```python
import quantsdk as qs
import math
import numpy as np

def ansatz(params: list[float]) -> qs.Circuit:
    """Create a parameterized trial state (ansatz).

    Args:
        params: List of 4 rotation angles.
    """
    circuit = qs.Circuit(2, name="vqe-ansatz")
    circuit.ry(0, params[0])
    circuit.ry(1, params[1])
    circuit.cx(0, 1)
    circuit.ry(0, params[2])
    circuit.ry(1, params[3])
    return circuit

def measure_zz(params: list[float], shots: int = 4096) -> float:
    """Measure <Z0 Z1> expectation value."""
    circuit = ansatz(params)
    circuit.measure_all()
    result = qs.run(circuit, shots=shots)

    # Calculate <ZZ>: Z|0>=+1, Z|1>=-1
    exp_val = 0.0
    for bitstring, count in result.counts.items():
        z0 = 1 - 2 * int(bitstring[0])
        z1 = 1 - 2 * int(bitstring[1])
        exp_val += z0 * z1 * count
    return exp_val / shots

def measure_x(qubit: int, params: list[float], shots: int = 4096) -> float:
    """Measure <X> on a specific qubit."""
    circuit = ansatz(params)
    # Rotate to X basis: H then measure
    circuit.h(qubit)
    circuit.measure_all()
    result = qs.run(circuit, shots=shots)

    exp_val = 0.0
    for bitstring, count in result.counts.items():
        x_val = 1 - 2 * int(bitstring[qubit])
        exp_val += x_val * count
    return exp_val / shots

def energy(params: list[float]) -> float:
    """Compute <H> = <Z0Z1> + 0.5*<X0> + 0.5*<X1>."""
    zz = measure_zz(params)
    x0 = measure_x(0, params)
    x1 = measure_x(1, params)
    return zz + 0.5 * x0 + 0.5 * x1
```

## Classical Optimization Loop

```python
# Simple gradient-free optimization (coordinate descent)
best_params = [0.0, 0.0, 0.0, 0.0]
best_energy = energy(best_params)
print(f"Initial energy: {best_energy:.4f}")

learning_rate = 0.3
for iteration in range(50):
    for i in range(len(best_params)):
        # Try small perturbation
        trial_params = best_params.copy()
        trial_params[i] += learning_rate
        e_plus = energy(trial_params)

        trial_params[i] -= 2 * learning_rate
        e_minus = energy(trial_params)

        # Update in direction of lower energy
        if e_plus < best_energy:
            best_params[i] += learning_rate
            best_energy = e_plus
        elif e_minus < best_energy:
            best_params[i] -= learning_rate
            best_energy = e_minus

    if iteration % 10 == 0:
        print(f"Iteration {iteration}: energy = {best_energy:.4f}")

print(f"Final energy: {best_energy:.4f}")
print(f"Optimal params: {[f'{p:.3f}' for p in best_params]}")
```

## Ansatz Design

The choice of ansatz is crucial. Common ansatz types:

| Ansatz | Description | Use Case |
|--------|-------------|----------|
| **Hardware-efficient** | Matches native gate set | General NISQ |
| **UCCSD** | Chemistry-inspired | Molecular simulation |
| **QAOA** | Problem-structure aware | Optimization |

## Key Takeaways

1. VQE is a **hybrid** algorithm — quantum state prep + classical optimization
2. The **ansatz** defines the search space for trial states
3. **Shot noise** makes energy estimates noisy — need many shots
4. Works on **near-term hardware** (NISQ) with limited qubits and depth
5. Applications: molecular chemistry, materials science, optimization

## Next Tutorial

:material-arrow-right: [QAOA](09-qaoa.md) — quantum approximate optimization for combinatorial problems.
