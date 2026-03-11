# Changelog

All notable changes to QuantSDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — v0.1.0-dev

### Added

#### Core
- `Circuit` class with fluent API for building quantum circuits
- Named circuits via `qs.Circuit(n, name="my_circuit")`
- Circuit properties: `num_qubits`, `depth`, `gate_count`, `num_measurements`, `count_ops()`
- Circuit operations: `copy()`, `reset_circuit()`, `measure_all()`
- ASCII circuit drawing via `circuit.draw()`

#### Gate Library (44 classes, 54 GATE_MAP entries)
- **Pauli gates**: X, Y, Z, I (Identity)
- **Hadamard**: H
- **Phase gates**: S, Sdg, T, Tdg, Phase (U1)
- **Sqrt gates**: SX, SXdg
- **Rotation gates**: RX, RY, RZ, R, U2, U3
- **Controlled single-qubit**: CX (CNOT), CY, CZ, CH, CS, CSdg, CSX
- **Controlled rotation**: CRX, CRY, CRZ, CP (CPhase), CU1, CU3
- **Swap gates**: SWAP, iSWAP, DCX
- **Ising coupling**: RXX, RYY, RZZ, RZX
- **Multi-qubit**: CCX (Toffoli), CCZ, CSWAP (Fredkin), ECR
- **Utility**: Measure, Barrier, Reset
- All gates have `.matrix()` methods returning unitary numpy arrays
- Gate aliases in GATE_MAP (e.g., `"cnot"` -> CX, `"toffoli"` -> CCX, `"fredkin"` -> CSWAP)

#### Results
- `Result` class with `counts`, `probabilities`, `most_likely`, `top_k(k)`
- `summary()` for pretty-printed result overview
- `expectation_value(qubit)` for computing <Z> on individual qubits
- `plot_histogram()` for matplotlib visualization
- `to_pandas()` for pandas DataFrame conversion
- `to_dict()` for full serializable output

#### Backends & Simulation
- `qs.run()` top-level API with multi-backend routing
- Local statevector simulator (pure NumPy, up to 24 qubits, Reset support)
- Backend selection via `backend=` parameter ("local", "aer", "ibm_*")
- Smart routing parameters: `optimize_for`, `max_cost_usd`, `min_fidelity`
- Reproducible results via `seed=` parameter
- Abstract `Backend` ABC with `BackendInfo` and `BackendStatus`

#### Framework Interop
- `circuit.to_qiskit()` / `qs.Circuit.from_qiskit()` — Qiskit round-trip
- `circuit.to_openqasm()` / `qs.Circuit.from_openqasm()` — OpenQASM 2.0 round-trip
- IBM Quantum backend adapter (`IBMBackend`)
- Qiskit Aer backend adapter (`AerBackend`)

#### Documentation
- Full MkDocs Material documentation site (30+ pages)
- Getting Started guide (installation, first circuit, core concepts)
- API Reference (Circuit, Result, Gates, Runner, Backend)
- Tutorials (Bell states, Grover's search, VQE, teleportation)
- Backend guides (local simulator, IBM Quantum, Aer)
- Contributing guide and changelog

#### Examples
- 22 Jupyter notebooks covering beginner to advanced topics
- Beginner (01-07): Hello quantum, Bell states, GHZ, gates, inspection, visualization
- Intermediate (08-14): Teleportation, Deutsch-Jozsa, BV, Simon's, Grover's, QFT, QPE
- Advanced (15-18): VQE, QAOA MaxCut, quantum ML, parameter-shift gradients
- Interop (19-22): Qiskit interop, OpenQASM interop, backend comparison, gate showcase

#### CI/CD
- GitHub Actions CI: lint (ruff), test (Python 3.10-3.13), interop tests, type check (mypy)
- GitHub Actions publish: PyPI trusted publisher via OIDC on release

#### Community
- Apache 2.0 license
- Contributor Covenant Code of Conduct v2.1
- Contributing guide with development setup and guidelines
- Security policy for responsible disclosure
