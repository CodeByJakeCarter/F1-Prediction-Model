# Error Handling

## Principles

- Fail fast on invalid inputs.
- Return deterministic and actionable error messages.
- Separate domain errors from HTTP transport mapping.

## Current API behavior (step 1.1.1.8)

- `/health` returns `200` with `{"status": "ok"}`.
- Other routes are not implemented yet.

## Mapping guideline for future endpoints

- Validation errors -> HTTP `422`.
- Domain not-found errors -> HTTP `404`.
- Domain rule violations -> HTTP `400` or `409` depending on conflict semantics.
- Unexpected internal failures -> HTTP `500` with sanitized message.
