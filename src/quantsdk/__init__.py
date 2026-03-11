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

__version__ = "0.1.0-dev"

from quantsdk.circuit import Circuit
from quantsdk.result import Result
from quantsdk.runner import run

__all__ = [
    "Circuit",
    "Result",
    "__version__",
    "run",
]
