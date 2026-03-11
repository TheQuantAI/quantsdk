# Your First Quantum Circuit

This guide dives deeper into circuit building with QuantSDK's fluent API.

## Creating Circuits

```python
import quantsdk as qs

# Specify number of qubits
circuit = qs.Circuit(3)

# With a name (useful for debugging)
circuit = qs.Circuit(3, name="ghz-state")
```

All qubits start in the $|0\rangle$ state.

## The Fluent API

Every gate method returns the circuit itself, enabling method chaining:

```python
circuit = (
    qs.Circuit(3)
    .h(0)
    .cx(0, 1)
    .cx(0, 2)
    .measure_all()
)
```

## Single-Qubit Gates

### Pauli Gates

```python
circuit = qs.Circuit(1)
circuit.x(0)    # Pauli-X (NOT gate) — |0> -> |1>
circuit.y(0)    # Pauli-Y
circuit.z(0)    # Pauli-Z — phase flip
circuit.i(0)    # Identity (no-op)
```

### Hadamard

```python
circuit.h(0)    # Creates superposition: |0> -> (|0> + |1>) / sqrt(2)
```

### Phase Gates

```python
circuit.s(0)      # S gate (pi/2 phase)
circuit.sdg(0)    # S-dagger (inverse of S)
circuit.t(0)      # T gate (pi/4 phase)
circuit.tdg(0)    # T-dagger (inverse of T)
circuit.sx(0)     # sqrt(X)
circuit.sxdg(0)   # sqrt(X)-dagger
```

### Rotation Gates

Parametric rotations around the Bloch sphere axes:

```python
import math

circuit.rx(0, math.pi / 4)    # Rotate around X-axis
circuit.ry(0, math.pi / 2)    # Rotate around Y-axis
circuit.rz(0, math.pi)        # Rotate around Z-axis
circuit.r(0, math.pi/4, math.pi/2)  # General rotation R(theta, phi)
```

### General Single-Qubit Unitaries

```python
circuit.phase(0, math.pi / 4)       # Phase gate (= U1)
circuit.u1(0, lam=math.pi / 4)      # U1(lambda)
circuit.u2(0, phi=0, lam=math.pi)   # U2(phi, lambda)
circuit.u3(0, theta=math.pi/2, phi=0, lam=math.pi)  # U3 (most general)
```

## Two-Qubit Gates

### Controlled Gates

```python
circuit.cx(0, 1)     # CNOT (controlled-X) — the workhorse of entanglement
circuit.cy(0, 1)     # Controlled-Y
circuit.cz(0, 1)     # Controlled-Z
circuit.ch(0, 1)     # Controlled-Hadamard
circuit.cs(0, 1)     # Controlled-S
circuit.csdg(0, 1)   # Controlled-S-dagger
circuit.csx(0, 1)    # Controlled-sqrt(X)
```

### Controlled Rotations

```python
circuit.crx(0, 1, math.pi / 4)   # Controlled-RX
circuit.cry(0, 1, math.pi / 2)   # Controlled-RY
circuit.crz(0, 1, math.pi)       # Controlled-RZ
circuit.cp(0, 1, math.pi / 4)    # Controlled-Phase
circuit.cu1(0, 1, lam=math.pi/4) # Controlled-U1
circuit.cu3(0, 1, theta=math.pi/2, phi=0, lam=math.pi)  # Controlled-U3
```

### SWAP-Family Gates

```python
circuit.swap(0, 1)    # SWAP — exchange qubit states
circuit.iswap(0, 1)   # iSWAP — SWAP with phase
circuit.dcx(0, 1)     # Double-CNOT
circuit.ecr(0, 1)     # Echoed Cross-Resonance
```

### Ising Interaction Gates

```python
circuit.rzz(0, 1, math.pi / 4)   # ZZ-interaction
circuit.rxx(0, 1, math.pi / 4)   # XX-interaction
circuit.ryy(0, 1, math.pi / 4)   # YY-interaction
circuit.rzx(0, 1, math.pi / 4)   # ZX-interaction
```

## Three-Qubit Gates

```python
circuit.ccx(0, 1, 2)     # Toffoli (CCNOT)
circuit.ccz(0, 1, 2)     # Controlled-CZ
circuit.cswap(0, 1, 2)   # Fredkin (controlled-SWAP)
```

## Measurement and Control

```python
# Measure specific qubits
circuit.measure(0)     # Measure qubit 0
circuit.measure(1)     # Measure qubit 1

# Measure all qubits at once
circuit.measure_all()

# Barrier (prevents gate optimization across it)
circuit.barrier()
circuit.barrier(0, 1)  # Barrier on specific qubits

# Reset qubit to |0>
circuit.reset(0)
```

## Circuit Inspection

```python
circuit = qs.Circuit(3).h(0).cx(0, 1).cx(0, 2).measure_all()

# Number of qubits
print(circuit.num_qubits)   # 3

# Circuit depth
print(circuit.depth)         # 4

# Total gate count
print(circuit.gate_count)    # 6 (h + 2*cx + 3*measure)

# Gate breakdown
print(circuit.count_ops())
# {'h': 1, 'cx': 2, 'measure': 3}

# Text drawing
print(circuit.draw())
```

## Circuit Operations

```python
# Copy a circuit
circuit2 = circuit.copy()

# Reset (clear all gates)
circuit.reset_circuit()

# Access gates list
for gate, qubits, params in circuit.gates:
    print(f"{gate} on qubits {qubits} with params {params}")
```

## Common Patterns

### Bell State

```python
bell = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = qs.run(bell, shots=1000)
# Expect ~50% |00> and ~50% |11>
```

### GHZ State

```python
ghz = qs.Circuit(3).h(0).cx(0, 1).cx(0, 2).measure_all()
result = qs.run(ghz, shots=1000)
# Expect ~50% |000> and ~50% |111>
```

### Quantum Teleportation

```python
teleport = (
    qs.Circuit(3)
    # Prepare state to teleport on qubit 0
    .rx(0, math.pi / 4)
    # Create Bell pair (qubits 1-2)
    .h(1).cx(1, 2)
    # Bell measurement (qubits 0-1)
    .cx(0, 1).h(0)
    .measure(0).measure(1)
    # Note: Classical corrections would be applied based on measurement
)
```

## Next Steps

- **[Real Hardware](real-hardware.md)** — Run on IBM Quantum
- **[Gate Reference](../api/gates.md)** — Complete gate documentation
- **[Tutorials](../tutorials/index.md)** — Step-by-step quantum algorithms
