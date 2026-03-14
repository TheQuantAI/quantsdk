# Contributing to QuantSDK

Thank you for your interest in contributing to QuantSDK! This guide will help you get started.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/quantsdk.git
cd quantsdk

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install in development mode with all dev dependencies
pip install -e ".[dev,viz]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests
pytest

# 6. Check linting
ruff check src/ tests/
ruff format --check src/ tests/
```

## Development Workflow

1. **Create an issue** — Describe the feature or bug before starting work.
2. **Create a branch** — `feature/QUANT-{issue_number}-short-description` or `fix/QUANT-{issue_number}-short-description`
3. **Implement with tests** — Every feature needs tests. Aim for 90%+ coverage.
4. **Open a Pull Request** — Fill out the PR template. Link the issue.
5. **CI must pass** — Lint, format, type check, and all tests must be green.
6. **Code review** — At least one maintainer must approve.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=quantsdk --cov-report=term-missing

# Run specific test file
pytest tests/test_circuit.py

# Run tests matching a pattern
pytest -k "test_bell"

# Skip slow/integration tests
pytest -m "not slow and not integration"

# Run only fast unit tests
pytest -m "not slow and not integration" -x
```

## Code Quality

We use **ruff** for linting and formatting:

```bash
# Lint
ruff check src/ tests/

# Auto-fix lint issues
ruff check src/ tests/ --fix

# Format
ruff format src/ tests/

# Type checking
mypy src/quantsdk/ --ignore-missing-imports
```

## Code Style

- **Python 3.10+** — Use modern Python features (type hints, `match`, `|` for unions).
- **Docstrings** — Google style. Every public function/class needs a docstring.
- **Type hints** — All public APIs must have type annotations.
- **Frozen dataclasses** — Gates are immutable (`@dataclass(frozen=True)`).
- **Fluent API** — Circuit methods return `self` for chaining.
- **Line length** — 100 characters max.

## Project Structure

```
src/quantsdk/
  __init__.py              # Public API surface (Circuit, Result, run)
  circuit.py               # Circuit class with fluent gate methods (44+ gates)
  gates.py                 # 44 gate classes, 54 GATE_MAP entries
  result.py                # Result dataclass (counts, probabilities, viz)
  runner.py                # qs.run() top-level API with backend routing
  backend.py               # Abstract Backend interface
  simulators/
    local.py               # Pure NumPy statevector simulator (up to 24 qubits)
  interop/
    qiskit_interop.py      # Qiskit <-> QuantSDK conversion
    openqasm.py            # OpenQASM 2.0 <-> QuantSDK conversion
  backends/
    ibm.py                 # IBM Quantum + Aer backend adapters
tests/
  test_circuit.py          # Circuit class tests
  test_gates.py            # Gate definition tests
  test_simulator.py        # Local simulator tests
  test_qiskit_interop.py   # Qiskit interop tests
  test_openqasm.py         # OpenQASM interop tests
  test_aer_backend.py      # Aer backend tests
  test_api_surface.py      # Public API surface tests
  test_expanded_gates.py   # Extended gate library tests
examples/                  # 22 Jupyter notebooks
docs/                      # MkDocs Material documentation
```

## Adding a New Gate

1. Add the gate class to `src/quantsdk/gates.py` as a frozen dataclass with a `.matrix()` method.
2. Add it to `GATE_MAP` in the same file (can have aliases, e.g., `"toffoli"` -> `CCX`).
3. Add a convenience method to `Circuit` in `src/quantsdk/circuit.py` that returns `self`.
4. Add Qiskit mapping in `src/quantsdk/interop/qiskit_interop.py` (`_QS_TO_QISKIT_MAP` and `_qiskit_gate_to_qs`).
5. Add OpenQASM mapping in `src/quantsdk/interop/openqasm.py` (`_GATE_TO_QASM` and `_QASM_GATE_MAP`).
6. Write tests in `tests/test_expanded_gates.py` (matrix shape, unitarity, known values).
7. Update the gate table in `docs/api/gates.md`.

Example gate class:

```python
@dataclass(frozen=True)
class MyGate(Gate):
    """My custom gate."""
    qubit: int

    @property
    def qubits(self) -> tuple[int, ...]:
        return (self.qubit,)

    @property
    def name(self) -> str:
        return "MyGate"

    def matrix(self) -> np.ndarray:
        return np.array([[1, 0], [0, 1]], dtype=complex)
```

## Adding a New Backend

1. Create a new file in `src/quantsdk/backends/` (e.g., `ionq.py`).
2. Implement the `Backend` ABC from `src/quantsdk/backend.py`.
3. Implement `run(circuit, shots, **options)` and `info()` methods.
4. Add backend alias resolution in `src/quantsdk/runner.py` (`_BACKEND_ALIASES`).
5. Write tests (use simulators or mocks for CI — real hardware tests go in `tests/integration/`).
6. Add docs page in `docs/backends/`.

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add IonQ backend adapter
fix: correct CZ gate matrix phase
docs: add tutorial for quantum teleportation
test: add roundtrip tests for OpenQASM
refactor: simplify gate dispatch in runner
perf: optimize statevector contraction for 2-qubit gates
chore: update ruff to v0.5.0
ci: add Python 3.13 to test matrix
```

Scope prefixes are optional but encouraged:

```
feat(gates): add RZX Ising coupling gate
fix(simulator): handle Reset gate for multi-qubit states
docs(api): update Circuit class docstrings
```

## Reporting Bugs

Please include:

- QuantSDK version: `python -c "import quantsdk; print(quantsdk.__version__)"`
- Python version: `python --version`
- OS and architecture
- Minimal reproducible example
- Full error traceback

## Suggesting Features

Open a GitHub issue with:

- **Problem** — What pain point does this solve?
- **Proposed Solution** — How should it work? (API sketch)
- **Alternatives** — What other approaches did you consider?
- **Context** — Any references, papers, or existing implementations?

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR.
- Update tests and docs alongside code changes.
- Ensure all CI checks pass before requesting review.
- Add a changelog entry in the PR description.
- Be responsive to review feedback.

## Security

If you discover a security vulnerability, please **do not** open a public issue. Instead, see [SECURITY.md](https://github.com/TheQuantAI/quantsdk/blob/main/SECURITY.md) for responsible disclosure instructions.

## Community

- **GitHub Issues** — Bug reports and feature requests
- **GitHub Discussions** — Questions and general discussion
- **Discord** — [Join our Discord](https://discord.gg/uTEW77Kcj4) for real-time chat with the team and community

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
