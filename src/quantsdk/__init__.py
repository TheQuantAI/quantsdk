# Copyright 2026 TheQuantAI
# Licensed under the Apache License, Version 2.0

"""
QuantSDK — Write quantum code once, run anywhere.

A framework-agnostic quantum computing SDK by TheQuantAI.

Quick Start::

    import quantsdk as qs

    circuit = qs.Circuit(2, name="bell_state")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    result = qs.run(circuit, shots=1000)
    print(result.counts)  # {'00': 503, '11': 497}
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("quantsdk")
except PackageNotFoundError:  # pragma: no cover — editable / dev installs
    __version__ = "0.1.0"

from quantsdk.circuit import Circuit
from quantsdk.result import Result
from quantsdk.runner import run

__all__ = [
    "Circuit",
    "Result",
    "__version__",
    "run",
]


# Lazy imports for optional modules — available as qs.interop, qs.backends
def __getattr__(name: str) -> object:
    if name == "interop":
        from quantsdk import interop

        return interop
    if name == "backends":
        from quantsdk import backends

        return backends
    raise AttributeError(f"module 'quantsdk' has no attribute {name!r}")
