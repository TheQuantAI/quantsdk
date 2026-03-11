# Changelog

All notable changes to QuantSDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — v0.1.0-dev

### Added
- Core `Circuit` class with fluent API for building quantum circuits
- Gate library: H, X, Y, Z, S, T, I, RX, RY, RZ, U3, CX, CZ, SWAP, RZZ, CCX, CSWAP
- `Result` class with counts, probabilities, `most_likely`, `top_k()`, and `summary()`
- Local statevector simulator (pure NumPy, up to 24 qubits)
- `qs.run()` top-level API for circuit execution
- ASCII circuit drawing via `circuit.draw()`
- Circuit analysis: `depth`, `gate_count`, `count_ops()`
- Full test suite with pytest
