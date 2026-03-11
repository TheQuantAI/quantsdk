# Result

The `Result` class holds the output of a quantum circuit execution —
measurement counts, probabilities, and methods for analysis and visualization.

## Overview

```python
import quantsdk as qs

circuit = qs.Circuit(2).h(0).cx(0, 1).measure_all()
result = qs.run(circuit, shots=1000)

# Access data
result.counts          # {'00': 512, '11': 488}
result.probabilities   # {'00': 0.512, '11': 0.488}
result.most_likely     # '00'
result.top_k(1)        # [('00', 512)]

# Visualization
result.plot_histogram()          # matplotlib bar chart
df = result.to_pandas()          # pandas DataFrame
print(result.summary())          # formatted summary string

# Serialization
result.to_dict()                 # dict for JSON export
```

## API Reference

::: quantsdk.result.Result
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      heading_level: 3
      show_signature_annotations: true
      separate_signature: true
      filters:
        - "!^_"
