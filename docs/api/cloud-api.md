# Cloud API Reference

TheQuantCloud REST API provides programmatic access to quantum circuit execution, job management, and account features.

**Base URL**: `https://api.thequantcloud.com`

**Authentication**: All authenticated endpoints accept either:

- **Supabase JWT** — `Authorization: Bearer <jwt_token>` (from QuantStudio login)
- **API Key** — `X-API-Key: qc_live_...` (generated from Dashboard)

---

## Health & Status

### `GET /health`

Health check endpoint. No authentication required.

**Response** `200`:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-03-16T10:00:00Z"
}
```

### `GET /v1/status`

Platform status with backend availability. No authentication required.

**Response** `200`:
```json
{
  "status": "operational",
  "backends": {
    "local_simulator": "online",
    "aer_simulator": "online",
    "cirq_simulator": "online"
  },
  "active_jobs": 3,
  "timestamp": "2026-03-16T10:00:00Z"
}
```

---

## Backends

### `GET /v1/backends`

List all available backends. No authentication required.

**Response** `200`:
```json
{
  "backends": [
    {
      "name": "aer_simulator",
      "provider": "ibm",
      "num_qubits": 25,
      "status": "online",
      "is_simulator": true,
      "queue_depth": 0,
      "avg_queue_time_sec": 0.0,
      "cost_per_shot": 0.0,
      "native_gates": ["h", "cx", "rz", "sx", "x"],
      "description": "IBM Qiskit Aer high-performance simulator"
    }
  ],
  "count": 5
}
```

### `GET /v1/backends/{name}`

Get details for a specific backend.

**Parameters**:

| Name | Location | Required | Description |
|------|----------|----------|-------------|
| `name` | path | Yes | Backend identifier (e.g. `aer_simulator`) |

---

## Authentication & API Keys

### `POST /v1/auth/api-keys`

Generate a new API key. **Requires JWT auth.**

**Request Body**:
```json
{
  "name": "my-laptop"
}
```

**Response** `201`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-laptop",
  "key_prefix": "qc_live_a1",
  "key": "qc_live_a1b2c3d4e5f6g7h8i9j0..."
}
```

!!! warning
    The `key` field is only returned at creation time. Store it securely.

### `GET /v1/auth/api-keys`

List all API keys for the authenticated user. **Requires JWT auth.**

**Response** `200`:
```json
{
  "api_keys": [
    {
      "id": "550e8400-...",
      "name": "my-laptop",
      "key_prefix": "qc_live_a1",
      "created_at": "2026-03-16T10:00:00Z",
      "last_used_at": "2026-03-16T12:00:00Z"
    }
  ]
}
```

### `DELETE /v1/auth/api-keys/{id}`

Revoke an API key. **Requires JWT auth.**

**Response** `200`:
```json
{
  "detail": "API key revoked"
}
```

---

## Circuits

### `POST /v1/circuits/run`

Submit a quantum circuit for execution. This creates a job and returns immediately.

**Request Body**:
```json
{
  "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;",
  "shots": 1024,
  "backend": "aer_simulator",
  "optimize_for": "balanced"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `qasm` | string | Yes | — | OpenQASM 2.0 circuit string |
| `shots` | integer | No | 1024 | Number of measurement shots |
| `backend` | string | No | auto-routed | Target backend (or let QuantRouter decide) |
| `optimize_for` | string | No | `"balanced"` | `"speed"`, `"accuracy"`, `"cost"`, `"balanced"` |

**Response** `202`:
```json
{
  "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "status": "submitted",
  "backend": null,
  "shots": 1024,
  "optimize_for": "balanced",
  "submitted_at": "2026-03-16T10:00:00Z"
}
```

### `POST /v1/circuits`

Save a circuit (without executing).

**Request Body**:
```json
{
  "name": "My Bell State",
  "code": "import quantsdk as qs\n...",
  "qasm": "OPENQASM 2.0;...",
  "num_qubits": 2
}
```

### `GET /v1/circuits`

List the authenticated user's saved circuits. Supports pagination.

**Query Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | integer | 20 | Max results |
| `offset` | integer | 0 | Pagination offset |

### `GET /v1/circuits/{id}`

Get a specific saved circuit.

### `PUT /v1/circuits/{id}`

Update a saved circuit.

### `DELETE /v1/circuits/{id}`

Delete a saved circuit.

---

## Jobs

### `GET /v1/jobs`

List the authenticated user's jobs. Supports pagination and status filtering.

**Query Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `limit` | integer | 20 | Max results |
| `offset` | integer | 0 | Pagination offset |
| `status` | string | — | Filter by status |

### `GET /v1/jobs/{id}`

Get job status and details.

**Response** `200`:
```json
{
  "job_id": "d290f1ee-...",
  "status": "completed",
  "backend": "aer_simulator",
  "shots": 1024,
  "optimize_for": "balanced",
  "submitted_at": "2026-03-16T10:00:00Z",
  "started_at": "2026-03-16T10:00:01Z",
  "completed_at": "2026-03-16T10:00:03Z",
  "error_message": null,
  "metadata": {}
}
```

**Job Status Values**:

| Status | Description |
|--------|-------------|
| `submitted` | Job received, awaiting processing |
| `analyzing` | Circuit analysis in progress |
| `routing` | QuantRouter selecting backend |
| `queued` | Waiting in backend queue |
| `dispatched` | Sent to backend |
| `running` | Executing on backend |
| `completed` | Execution finished successfully |
| `failed` | Execution failed |
| `timeout` | Execution timed out |
| `cancelled` | Cancelled by user |

### `GET /v1/jobs/{id}/result`

Get execution results for a completed job.

**Response** `200`:
```json
{
  "job_id": "d290f1ee-...",
  "counts": {"00": 512, "11": 512},
  "probabilities": {"00": 0.5, "11": 0.5},
  "statevector": null,
  "execution_time_ms": 145.2,
  "backend": "aer_simulator",
  "metadata": {
    "num_qubits": 2,
    "circuit_depth": 3,
    "gate_count": 4
  }
}
```

### `POST /v1/jobs/{id}/cancel`

Cancel a pending or running job.

**Response** `200`:
```json
{
  "job_id": "d290f1ee-...",
  "status": "cancelled"
}
```

---

## Account

### `GET /v1/account/usage`

Get current usage and quota information.

**Response** `200`:
```json
{
  "tier": "explorer",
  "credits_remaining_usd": 49.50,
  "current_month": {
    "simulator_minutes": 12.5,
    "simulator_limit": 60.0,
    "qpu_tasks": 2,
    "qpu_limit": 10,
    "total_jobs": 15,
    "total_cost_usd": 0.50
  },
  "limits": {
    "max_shots": 10000,
    "max_qubits": 25,
    "max_concurrent_jobs": 3,
    "api_keys_limit": 5
  }
}
```

### `GET /v1/account/profile`

Get user profile information. **Requires JWT auth.**

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "detail": "Description of the error"
}
```

**Common Status Codes**:

| Code | Meaning |
|------|---------|
| `400` | Bad request — invalid input |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient permissions or quota exceeded |
| `404` | Not found |
| `429` | Rate limited — too many requests |
| `500` | Internal server error |

**Rate Limits**:

| Tier | Requests/Minute |
|------|-----------------|
| Explorer (free) | 30 |
| Developer | 120 |
| Enterprise | Unlimited |

---

## SDKs & Clients

- **Python**: `pip install thequantsdk` — [GitHub](https://github.com/TheQuantAI/quantsdk)
- **Web IDE**: [QuantStudio](https://studio.thequantcloud.com)
- **REST**: Use any HTTP client with the base URL above
