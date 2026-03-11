# Circuit

The `Circuit` class is the core abstraction in QuantSDK. It represents a
sequence of quantum gates applied to qubits and provides a fluent API for
circuit construction.

## Overview

```python
import quantsdk as qs

# Create and build a circuit using the fluent API
circuit = (
    qs.Circuit(3, name="ghz")
    .h(0)
    .cx(0, 1)
    .cx(0, 2)
    .measure_all()
)

# Run and inspect
result = qs.run(circuit, shots=1000)
print(result.counts)
```

## API Reference

::: quantsdk.circuit.Circuit
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      heading_level: 3
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      filters:
        - "!^_"
        - "^__init__"
