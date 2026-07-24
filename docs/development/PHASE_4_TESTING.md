# Phase 4 Testing Guide

## Testing Strategy

- **Unit Tests**: Test state transitions, priority checks, and schema validation.
- **Integration Tests**: Test database migrations, atomic task number generation, OCC version conflict handling, advisory lock cycle prevention, and RBAC authorization.
- **Frontend Vitest**: Test component rendering and BFF allowlist forwarding.
- **Playwright E2E**: Test complete end-to-end task lifecycle workflow in Chromium.
