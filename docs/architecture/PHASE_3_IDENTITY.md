# Phase 3: Identity and Workspaces

## Architecture Decisions

1. **API Client Strategy**:
   We chose `@hey-api/openapi-ts` for strictly typed frontend-backend contracts. The frontend API client wrapper centrally handles cookies and server-side request propagation.

2. **Session Management**:
   We implemented `HttpOnly`, `Secure` (in production) cookies for session management to protect against XSS. CSRF protection is enforced via `Origin` and `Referer` checks in the backend for state-modifying requests.

3. **Routing and Middleware**:
   Next.js Middleware intercepts requests to protect private routes like `/dashboard` and redirects unauthenticated users to `/login`. Server Actions encapsulate backend mutations, hiding internal logic and keeping API URLs out of the client payload.

4. **Testing**:
   - `vitest` for fast isolated unit testing of React components.
   - `@playwright/test` for critical path E2E testing (e.g. login, registration) ensuring the integration between the compiled frontend and running backend environment is sound.
