# Example Notebooks

QuantSDK ships with **22 Jupyter notebooks** covering everything from your
first quantum circuit to advanced variational algorithms and backend interop.
Each notebook is self-contained and can be run locally with JupyterLab.

## Quick Setup

```bash
pip install "quantsdk[viz,interop]" jupyterlab
jupyter lab
```

!!! tip "Clone the repo to get all notebooks at once"
    ```bash
    git clone https://github.com/TheQuantAI/quantsdk.git
    cd quantsdk/examples
    jupyter lab
    ```

---

## :material-school: Beginner

Foundational concepts — no prior quantum experience required.

| # | Notebook | What You'll Learn | Links |
|:-:|----------|-------------------|:-----:|
| 01 | **Hello Quantum** | Create your first circuit, apply a Hadamard gate, measure, and interpret results. | [:material-download: Download][nb01] · [:material-github: View][nb01-gh] |
| 02 | **Bell States** | Build all four Bell states and verify entanglement through correlated measurements. | [:material-download: Download][nb02] · [:material-github: View][nb02-gh] · [:material-book-open-variant: Tutorial](../tutorials/01-bell-state.md) |
| 03 | **GHZ State** | Extend entanglement to 3+ qubits with the Greenberger–Horne–Zeilinger state. | [:material-download: Download][nb03] · [:material-github: View][nb03-gh] |
| 04 | **Single-Qubit Gates** | Explore Pauli (X, Y, Z), Hadamard, S, T, and rotation gates (Rx, Ry, Rz) on the Bloch sphere. | [:material-download: Download][nb04] · [:material-github: View][nb04-gh] |
| 05 | **Multi-Qubit Gates** | Master CNOT, CZ, SWAP, Toffoli, and Fredkin gates for building complex circuits. | [:material-download: Download][nb05] · [:material-github: View][nb05-gh] |
| 06 | **Circuit Inspection** | Use `depth`, `gate_count`, `draw()`, and `count_ops()` to analyze circuits. | [:material-download: Download][nb06] · [:material-github: View][nb06-gh] |
| 07 | **Results & Visualization** | Plot histograms, build DataFrames, and compute expectation values from results. | [:material-download: Download][nb07] · [:material-github: View][nb07-gh] |

[nb01]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/01_hello_quantum.ipynb
[nb01-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/01_hello_quantum.ipynb
[nb02]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/02_bell_states.ipynb
[nb02-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/02_bell_states.ipynb
[nb03]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/03_ghz_state.ipynb
[nb03-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/03_ghz_state.ipynb
[nb04]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/04_single_qubit_gates.ipynb
[nb04-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/04_single_qubit_gates.ipynb
[nb05]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/05_multi_qubit_gates.ipynb
[nb05-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/05_multi_qubit_gates.ipynb
[nb06]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/06_circuit_inspection.ipynb
[nb06-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/06_circuit_inspection.ipynb
[nb07]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/07_results_visualization.ipynb
[nb07-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/07_results_visualization.ipynb

---

## :material-transit-connection-variant: Intermediate

Quantum algorithms that demonstrate real computational advantage.

| # | Notebook | What You'll Learn | Links |
|:-:|----------|-------------------|:-----:|
| 08 | **Quantum Teleportation** | Teleport a qubit state using entanglement and classical communication. | [:material-download: Download][nb08] · [:material-github: View][nb08-gh] · [:material-book-open-variant: Tutorial](../tutorials/02-teleportation.md) |
| 09 | **Deutsch-Jozsa Algorithm** | Determine if a function is constant or balanced in a single query. | [:material-download: Download][nb09] · [:material-github: View][nb09-gh] · [:material-book-open-variant: Tutorial](../tutorials/03-deutsch-jozsa.md) |
| 10 | **Bernstein-Vazirani** | Recover a hidden binary string with one quantum query vs. *n* classical queries. | [:material-download: Download][nb10] · [:material-github: View][nb10-gh] · [:material-book-open-variant: Tutorial](../tutorials/04-bernstein-vazirani.md) |
| 11 | **Simon's Algorithm** | Find a hidden period with exponential speedup over classical approaches. | [:material-download: Download][nb11] · [:material-github: View][nb11-gh] · [:material-book-open-variant: Tutorial](../tutorials/05-simons-algorithm.md) |
| 12 | **Grover's Search** | Search an unsorted database with quadratic speedup using amplitude amplification. | [:material-download: Download][nb12] · [:material-github: View][nb12-gh] · [:material-book-open-variant: Tutorial](../tutorials/06-grovers-search.md) |
| 13 | **Quantum Fourier Transform** | Implement the QFT and inverse QFT — the foundation of Shor's algorithm. | [:material-download: Download][nb13] · [:material-github: View][nb13-gh] · [:material-book-open-variant: Tutorial](../tutorials/07-qft.md) |
| 14 | **Phase Estimation** | Estimate eigenvalues of a unitary operator — key subroutine for many algorithms. | [:material-download: Download][nb14] · [:material-github: View][nb14-gh] |

[nb08]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/08_teleportation.ipynb
[nb08-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/08_teleportation.ipynb
[nb09]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/09_deutsch_jozsa.ipynb
[nb09-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/09_deutsch_jozsa.ipynb
[nb10]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/10_bernstein_vazirani.ipynb
[nb10-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/10_bernstein_vazirani.ipynb
[nb11]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/11_simons_algorithm.ipynb
[nb11-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/11_simons_algorithm.ipynb
[nb12]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/12_grovers_search.ipynb
[nb12-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/12_grovers_search.ipynb
[nb13]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/13_qft.ipynb
[nb13-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/13_qft.ipynb
[nb14]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/14_phase_estimation.ipynb
[nb14-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/14_phase_estimation.ipynb

---

## :material-rocket-launch: Advanced

Variational algorithms and quantum machine learning.

| # | Notebook | What You'll Learn | Links |
|:-:|----------|-------------------|:-----:|
| 15 | **VQE** | Use the Variational Quantum Eigensolver to find ground-state energies. | [:material-download: Download][nb15] · [:material-github: View][nb15-gh] · [:material-book-open-variant: Tutorial](../tutorials/08-vqe.md) |
| 16 | **QAOA for MaxCut** | Solve the MaxCut graph problem with the Quantum Approximate Optimization Algorithm. | [:material-download: Download][nb16] · [:material-github: View][nb16-gh] · [:material-book-open-variant: Tutorial](../tutorials/09-qaoa.md) |
| 17 | **Quantum Machine Learning** | Build a parameterized quantum classifier and train it on simple datasets. | [:material-download: Download][nb17] · [:material-github: View][nb17-gh] |
| 18 | **Hybrid Algorithms** | Implement parameter-shift gradients for end-to-end quantum-classical training loops. | [:material-download: Download][nb18] · [:material-github: View][nb18-gh] · [:material-book-open-variant: Tutorial](../tutorials/10-hybrid-algorithms.md) |

[nb15]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/15_vqe.ipynb
[nb15-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/15_vqe.ipynb
[nb16]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/16_qaoa_maxcut.ipynb
[nb16-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/16_qaoa_maxcut.ipynb
[nb17]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/17_quantum_ml.ipynb
[nb17-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/17_quantum_ml.ipynb
[nb18]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/18_hybrid_algorithms.ipynb
[nb18-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/18_hybrid_algorithms.ipynb

---

## :material-swap-horizontal: Interop & Backends

Framework integration and multi-backend execution.

| # | Notebook | What You'll Learn | Links |
|:-:|----------|-------------------|:-----:|
| 19 | **Qiskit Interop** | Convert circuits between QuantSDK and Qiskit with `to_qiskit()` / `from_qiskit()`. | [:material-download: Download][nb19] · [:material-github: View][nb19-gh] |
| 20 | **OpenQASM Interop** | Export and import circuits via OpenQASM 2.0 for cross-platform portability. | [:material-download: Download][nb20] · [:material-github: View][nb20-gh] |
| 21 | **Backend Comparison** | Run the same circuit on Local, Aer, and IBM backends and compare results. | [:material-download: Download][nb21] · [:material-github: View][nb21-gh] |
| 22 | **Advanced Gate Library** | Showcase all 50+ gates in QuantSDK with parameterized and controlled variants. | [:material-download: Download][nb22] · [:material-github: View][nb22-gh] |

[nb19]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/19_qiskit_interop.ipynb
[nb19-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/19_qiskit_interop.ipynb
[nb20]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/20_openqasm_interop.ipynb
[nb20-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/20_openqasm_interop.ipynb
[nb21]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/21_backend_comparison.ipynb
[nb21-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/21_backend_comparison.ipynb
[nb22]: https://raw.githubusercontent.com/TheQuantAI/quantsdk/main/examples/22_advanced_gates.ipynb
[nb22-gh]: https://github.com/TheQuantAI/quantsdk/blob/main/examples/22_advanced_gates.ipynb

---

## Legend

| Icon | Meaning |
|:----:|---------|
| :material-download: Download | Download the `.ipynb` file directly (right-click → Save As) |
| :material-github: View | View the notebook on GitHub (rendered preview) |
| :material-book-open-variant: Tutorial | Companion step-by-step tutorial in the docs |
