# Contributing to QuantSDK

Thank you for your interest in contributing to QuantSDK! This guide will help you get started.

## 🚀 Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/quantsdk.git
cd quantsdk

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests
pytest

# 6. Check linting
ruff check src/ tests/
```

## 📋 Development Workflow

1. **Create an issue** — Describe the feature or bug before starting work.
2. **Create a branch** — `feature/QUANT-{issue_number}-short-description`
3. **Implement with tests** — Every feature needs tests. Aim for 90%+ coverage.
4. **Open a Pull Request** — Fill out the PR template. Link the issue.
5. **CI must pass** — Lint, format, and all tests must be green.
6. **Code review** — At least one maintainer must approve.

## 🧪 Running Tests

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
```

## 🔍 Code Quality

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

## 📐 Code Style

- **Python 3.10+** — Use modern Python features (type hints, `match`, `|` for unions).
- **Docstrings** — Google style. Every public function/class needs a docstring.
- **Type hints** — All public APIs must have type annotations.
- **Frozen dataclasses** — Gates are immutable (`@dataclass(frozen=True)`).
- **Fluent API** — Circuit methods return `self` for chaining.

## 🏗️ Project Structure

```
src/quantsdk/
├── __init__.py          # Public API surface
├── circuit.py           # Circuit class (core)
├── gates.py             # Gate definitions (17 gates)
├── result.py            # Result dataclass
├── backend.py           # Abstract Backend interface
├── runner.py            # qs.run() top-level API
├── simulators/
│   └── local.py         # Pure NumPy statevector simulator
├── interop/
│   ├── qiskit_interop.py  # Qiskit <-> QuantSDK
│   └── openqasm.py        # OpenQASM 2.0 <-> QuantSDK
└── backends/
    └── ibm.py           # IBM Quantum + Aer backend adapters
```

## ✅ Adding a New Gate

1. Add the gate class to `src/quantsdk/gates.py` (frozen dataclass, with `.matrix()`).
2. Add it to `GATE_MAP` in the same file.
3. Add a convenience method to `Circuit` in `src/quantsdk/circuit.py`.
4. Add Qiskit mapping in `src/quantsdk/interop/qiskit_interop.py`.
5. Add OpenQASM mapping in `src/quantsdk/interop/openqasm.py`.
6. Write tests in `tests/test_gates.py`, `tests/test_circuit.py`.

## ✅ Adding a New Backend

1. Create a new file in `src/quantsdk/backends/`.
2. Implement the `Backend` ABC from `src/quantsdk/backend.py`.
3. Implement `run()` and `info()` methods.
4. Add backend name resolution in `src/quantsdk/runner.py`.
5. Write tests (use simulators or mocks for CI).

## 📝 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Cirq framework interop
fix: correct CZ gate matrix phase
docs: add tutorial for VQE
test: add roundtrip tests for OpenQASM
chore: update ruff to v0.5.0
```

## 🐛 Reporting Bugs

Please include:
- QuantSDK version (`python -c "import quantsdk; print(quantsdk.__version__)"`)
- Python version (`python --version`)
- OS and architecture
- Minimal reproducible example
- Full error traceback

## 💬 Community

- **GitHub Issues** — Bug reports and feature requests.
- **GitHub Discussions** — Questions and general discussion.
- **Discord** — Real-time chat with the team and community.

## 📜 License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0.
