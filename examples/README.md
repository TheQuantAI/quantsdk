# QuantSDK Example Notebooks

20+ Jupyter notebooks demonstrating quantum computing with QuantSDK.

## Getting Started

```bash
# Install QuantSDK with visualization support
pip install quantsdk[viz]

# Launch Jupyter
pip install jupyterlab
jupyter lab
```

## Notebook Index

### Beginner (01-07)

| # | Notebook | Concepts |
|---|----------|----------|
| 01 | [Hello Quantum](01_hello_quantum.ipynb) | First circuit, superposition, measurement |
| 02 | [Bell States](02_bell_states.ipynb) | Entanglement, all four Bell states |
| 03 | [GHZ State](03_ghz_state.ipynb) | Multi-qubit entanglement |
| 04 | [Single-Qubit Gates](04_single_qubit_gates.ipynb) | Pauli, Hadamard, S, T, rotations |
| 05 | [Multi-Qubit Gates](05_multi_qubit_gates.ipynb) | CNOT, CZ, SWAP, Toffoli, Fredkin |
| 06 | [Circuit Inspection](06_circuit_inspection.ipynb) | depth, gate_count, draw, count_ops |
| 07 | [Results & Visualization](07_results_visualization.ipynb) | Histograms, DataFrames, expectations |

### Intermediate (08-14)

| # | Notebook | Concepts |
|---|----------|----------|
| 08 | [Quantum Teleportation](08_teleportation.ipynb) | Teleportation protocol |
| 09 | [Deutsch-Jozsa Algorithm](09_deutsch_jozsa.ipynb) | First quantum speedup |
| 10 | [Bernstein-Vazirani](10_bernstein_vazirani.ipynb) | Hidden string problem |
| 11 | [Simon's Algorithm](11_simons_algorithm.ipynb) | Exponential speedup |
| 12 | [Grover's Search](12_grovers_search.ipynb) | Amplitude amplification |
| 13 | [Quantum Fourier Transform](13_qft.ipynb) | QFT and inverse QFT |
| 14 | [Phase Estimation](14_phase_estimation.ipynb) | Eigenvalue estimation |

### Advanced (15-18)

| # | Notebook | Concepts |
|---|----------|----------|
| 15 | [VQE](15_vqe.ipynb) | Variational quantum eigensolver |
| 16 | [QAOA for MaxCut](16_qaoa_maxcut.ipynb) | Combinatorial optimization |
| 17 | [Quantum Machine Learning](17_quantum_ml.ipynb) | Parameterized classifiers |
| 18 | [Hybrid Algorithms](18_hybrid_algorithms.ipynb) | Parameter shift gradients |

### Interop & Backends (19-22)

| # | Notebook | Concepts |
|---|----------|----------|
| 19 | [Qiskit Interop](19_qiskit_interop.ipynb) | to_qiskit, from_qiskit |
| 20 | [OpenQASM Interop](20_openqasm_interop.ipynb) | to_openqasm, from_openqasm |
| 21 | [Backend Comparison](21_backend_comparison.ipynb) | Local vs Aer vs IBM |
| 22 | [Advanced Gate Library](22_advanced_gates.ipynb) | All 50+ gates showcase |

## Requirements

- Python 3.10+
- `quantsdk` (core)
- `quantsdk[viz]` (for histograms and DataFrames)
- `quantsdk[interop]` (for notebooks 19-20)
- `jupyterlab` or `notebook`
