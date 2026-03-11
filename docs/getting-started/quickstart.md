# Quickstart

Get from zero to quantum in 5 minutes.

## 1. Import QuantSDK

```python
import quantsdk as qs
```

## 2. Create a Circuit

Create a 2-qubit circuit and build it with the fluent API:

```python
circuit = qs.Circuit(2, name="my-first-circuit")

# Chain gates with the fluent API
circuit.h(0)        # Hadamard on qubit 0 -> superposition
circuit.cx(0, 1)    # CNOT: entangle qubits 0 and 1
circuit.measure_all()  # Measure all qubits
```

Or in one line:

```python
circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
```

## 3. Run the Circuit

```python
result = qs.run(circuit, shots=1000)
```

This runs on the built-in local simulator by default — no API keys, no cloud
access, no waiting.

## 4. Inspect Results

```python
# Raw counts
print(result.counts)
# {'00': 512, '11': 488}

# Most likely outcome
print(result.most_likely)
# '00'

# Probabilities
print(result.probabilities)
# {'00': 0.512, '11': 0.488}

# Top K results
print(result.top_k(1))
# [('00', 512)]

# Summary string
print(result.summary())
```

## 5. Visualize

```python
# Histogram (requires matplotlib)
result.plot_histogram()

# As a pandas DataFrame
df = result.to_pandas()
print(df)
```

## 6. Export to Other Frameworks

```python
# To Qiskit
qc = circuit.to_qiskit()

# To OpenQASM 2.0
qasm_str = circuit.to_openqasm()
print(qasm_str)
```

Output:
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

## What's Next?

- **[First Circuit](first-circuit.md)** — Learn about all available gates and circuit building patterns
- **[Real Hardware](real-hardware.md)** — Run on IBM Quantum processors
- **[Tutorials](../tutorials/index.md)** — Step-by-step quantum computing tutorials
- **[API Reference](../api/index.md)** — Full API documentation
