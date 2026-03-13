# QuantSDK — Write Quantum Code Once, Run Anywhere

<p align="center">
  <strong>A framework-agnostic quantum computing SDK by <a href="https://thequantai.in">TheQuantAI</a></strong>
</p>

<p align="center">
  <a href="https://github.com/TheQuantAI/quantsdk"><img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version"></a>
  <a href="https://github.com/TheQuantAI/quantsdk"><img src="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue" alt="Python versions"></a>
  <a href="https://github.com/TheQuantAI/quantsdk/blob/main/LICENSE"><img src="https://img.shields.io/github/license/TheQuantAI/quantsdk" alt="License"></a>
  <a href="https://github.com/TheQuantAI/quantsdk/actions"><img src="https://img.shields.io/github/actions/workflow/status/TheQuantAI/quantsdk/ci.yml?branch=main" alt="CI"></a>
</p>

<p align="center">
  <a href="https://docs.thequantcloud.com">Documentation</a> |
  <a href="https://docs.thequantcloud.com/getting-started/">Getting Started</a> |
  <a href="https://docs.thequantcloud.com/api/">API Reference</a> |
  <a href="#-examples">Examples</a> |
  <a href="https://discord.gg/thequantai">Discord</a>
</p>

---

## What is QuantSDK?

QuantSDK is a **framework-agnostic** quantum computing SDK that lets you write quantum circuits once and run them on **any backend** — IBM Quantum, IonQ, GPU simulators, and more.

No more vendor lock-in. No more rewriting circuits for each framework. **One API, every quantum computer.**

## Features

- **Framework-Agnostic** — Write once, export to Qiskit or OpenQASM 2.0
- **QuantRouter** — Rule-based smart routing picks the best backend for your circuit
- **Cloud Client** — Connect to TheQuantCloud for remote execution and job management
- **Pythonic API** — Clean fluent interface, minimal boilerplate
- **50+ Gates** — 44 gate classes, 54 named entries including all standard, parametric, and multi-qubit gates
- **Rich Results** — Histograms, probabilities, DataFrames, expectation values
- **Interop** — Seamless import/export with Qiskit circuits and OpenQASM 2.0
- **Fast Simulator** — Pure NumPy statevector simulator, up to 24 qubits
- **Well Tested** — 330+ tests across 10 test modules
- **Open Source** — Apache 2.0 license

## Installation

```bash
pip install quantsdk
```

With optional backends:

```bash
pip install quantsdk[ibm]     # IBM Quantum + Aer support
pip install quantsdk[gpu]     # GPU simulator support
pip install quantsdk[interop] # Qiskit interop
pip install quantsdk[viz]     # Matplotlib visualization
pip install quantsdk[all]     # Everything
```

## Quick Start

```python
import quantsdk as qs

# Create a Bell State circuit
circuit = qs.Circuit(2, name="bell_state")
circuit.h(0).cx(0, 1).measure_all()

# Run on local simulator (default)
result = qs.run(circuit, shots=1000, seed=42)

print(result.counts)         # {'00': 503, '11': 497}
print(result.probabilities)  # {'00': 0.503, '11': 0.497}
print(result.most_likely)    # '00'
```

## Run on Real Quantum Hardware

```python
# Run on IBM Quantum
result = qs.run(circuit, backend="ibm_brisbane", shots=1000)

# Run on Aer simulator
result = qs.run(circuit, backend="aer", shots=1000)

# Smart routing — let QuantRouter pick the best backend
result = qs.run(circuit,
    optimize_for="quality",
    max_cost_usd=0.50,
    shots=1000)
```

## Framework Interop

```python
# Export to Qiskit
qiskit_circuit = circuit.to_qiskit()

# Import from Qiskit
qs_circuit = qs.Circuit.from_qiskit(qiskit_circuit)

# Export to OpenQASM 2.0
qasm_str = circuit.to_openqasm()

# Import from OpenQASM
qs_circuit = qs.Circuit.from_openqasm(qasm_str)
```

## Rich Results

```python
result = qs.run(circuit, shots=4000, seed=42)

result.counts              # Raw counts dict
result.probabilities       # Normalized probabilities
result.most_likely         # Most frequent bitstring
result.top_k(3)            # Top 3 outcomes
result.summary()           # Pretty-printed summary
result.expectation_value(0)  # <Z> on qubit 0
result.to_pandas()         # pandas DataFrame
result.plot_histogram()    # Matplotlib histogram
result.to_dict()           # Full serializable dict
```

## Gate Library

QuantSDK includes **44 gate classes** with **54 named entries** in the gate map:

| Category | Gates |
|----------|-------|
| **Pauli** | X, Y, Z, I |
| **Hadamard** | H |
| **Phase** | S, Sdg, T, Tdg, Phase (U1) |
| **Sqrt** | SX, SXdg |
| **Rotation** | RX, RY, RZ, R, U2, U3 |
| **Controlled** | CX (CNOT), CY, CZ, CH, CS, CSdg, CSX, CP, CU1, CU3, CRX, CRY, CRZ |
| **Swap** | SWAP, iSWAP, DCX |
| **Ising** | RXX, RYY, RZZ, RZX |
| **Multi-Qubit** | CCX (Toffoli), CCZ, CSWAP (Fredkin), ECR |
| **Utility** | Measure, Barrier, Reset |

## Circuit Inspection

```python
circuit = qs.Circuit(3, name="ghz")
circuit.h(0).cx(0, 1).cx(1, 2).measure_all()

circuit.num_qubits       # 3
circuit.depth             # 3
circuit.gate_count        # 6  (H + 2 CX + 3 Measure)
circuit.count_ops()       # {'H': 1, 'CX': 2, 'Measure': 3}
circuit.draw()            # ASCII circuit diagram
circuit.copy()            # Deep copy
circuit.reset_circuit()   # Clear all gates
```

## Examples

The [`examples/`](examples/) directory contains **22 Jupyter notebooks** organized by difficulty:

### Beginner (01-07)
| Notebook | Topics |
|----------|--------|
| [01 Hello Quantum](examples/01_hello_quantum.ipynb) | First circuit, superposition, measurement |
| [02 Bell States](examples/02_bell_states.ipynb) | Entanglement, all four Bell states |
| [03 GHZ State](examples/03_ghz_state.ipynb) | Multi-qubit entanglement, scaling |
| [04 Single-Qubit Gates](examples/04_single_qubit_gates.ipynb) | Pauli, phase, rotation gates |
| [05 Multi-Qubit Gates](examples/05_multi_qubit_gates.ipynb) | CNOT, Toffoli, SWAP, Fredkin |
| [06 Circuit Inspection](examples/06_circuit_inspection.ipynb) | Properties, draw, depth analysis |
| [07 Results Visualization](examples/07_results_visualization.ipynb) | Histograms, DataFrames, statistics |

### Intermediate (08-14)
| Notebook | Topics |
|----------|--------|
| [08 Teleportation](examples/08_teleportation.ipynb) | Quantum teleportation protocol |
| [09 Deutsch-Jozsa](examples/09_deutsch_jozsa.ipynb) | Constant vs balanced oracle |
| [10 Bernstein-Vazirani](examples/10_bernstein_vazirani.ipynb) | Hidden string problem |
| [11 Simon's Algorithm](examples/11_simons_algorithm.ipynb) | Period finding |
| [12 Grover's Search](examples/12_grovers_search.ipynb) | Amplitude amplification |
| [13 QFT](examples/13_qft.ipynb) | Quantum Fourier Transform |
| [14 Phase Estimation](examples/14_phase_estimation.ipynb) | Eigenvalue estimation |

### Advanced (15-18)
| Notebook | Topics |
|----------|--------|
| [15 VQE](examples/15_vqe.ipynb) | Variational Quantum Eigensolver |
| [16 QAOA MaxCut](examples/16_qaoa_maxcut.ipynb) | Combinatorial optimization |
| [17 Quantum ML](examples/17_quantum_ml.ipynb) | Parameterized classifier |
| [18 Hybrid Algorithms](examples/18_hybrid_algorithms.ipynb) | Parameter-shift gradients |

### Interop & Backends (19-22)
| Notebook | Topics |
|----------|--------|
| [19 Qiskit Interop](examples/19_qiskit_interop.ipynb) | to_qiskit / from_qiskit |
| [20 OpenQASM Interop](examples/20_openqasm_interop.ipynb) | to_openqasm / from_openqasm |
| [21 Backend Comparison](examples/21_backend_comparison.ipynb) | Local vs Aer benchmarks |
| [22 Advanced Gates](examples/22_advanced_gates.ipynb) | Full 50+ gate showcase |

## Architecture

```
src/quantsdk/
  __init__.py              # Public API: Circuit, Result, run
  circuit.py               # Circuit class with fluent gate API
  gates.py                 # 44 gate classes, 54 GATE_MAP entries
  result.py                # Result with counts, probabilities, viz
  runner.py                # qs.run() multi-backend routing
  backend.py               # Abstract Backend interface
  router.py                # QuantRouter — rule-based smart backend routing
  cloud/
    __init__.py            # CloudClient — TheQuantCloud API client
    config.py              # Cloud configuration and endpoint management
  simulators/
    local.py               # Pure NumPy statevector simulator
  interop/
    qiskit_interop.py      # Qiskit <-> QuantSDK conversion
    openqasm.py            # OpenQASM 2.0 <-> QuantSDK conversion
  backends/
    ibm.py                 # IBM Quantum + Aer backend adapters
```

## Documentation

Full documentation is available at [docs.thequantcloud.com](https://docs.thequantcloud.com):

- [Getting Started](https://docs.thequantcloud.com/getting-started/) — Installation, first circuit, core concepts
- [API Reference](https://docs.thequantcloud.com/api/) — Circuit, Result, Gates, Runner, Backend
- [Tutorials](https://docs.thequantcloud.com/tutorials/) — Bell states, Grover's, VQE, teleportation
- [Backend Guides](https://docs.thequantcloud.com/backends/) — IBM Quantum, Aer, local simulator
- [Contributing](https://docs.thequantcloud.com/contributing/) — How to contribute

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Code style and testing guidelines
- How to add new gates and backends
- Commit message conventions

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## Security

To report security vulnerabilities, please see [SECURITY.md](SECURITY.md).

## About TheQuantAI

QuantSDK is built by [TheQuantAI](https://thequantai.in) — building the infrastructure layer for quantum computing.

- **TheQuantCloud** ([thequantcloud.com](https://thequantcloud.com)) — Quantum Computing Cloud Platform
- **TheQuantDefense** ([thequantdefense.com](https://thequantdefense.com)) — Quantum Solutions for Defense & Aerospace
