/**
 * BFF Route Handler tests.
 *
 * Tests the actual Next.js BFF handler logic (route-map allowlist + request
 * validation).  The actual HTTP proxying to FastAPI is tested separately in
 * the Playwright E2E suite.  Here we validate all the security invariants of
 * the route handler itself.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { isRouteAllowed } from "@/lib/api/route-map";

describe("BFF handler: approved routes are forwarded", () => {
  const approvedRoutes: [string, string][] = [
    ["/api/health/live", "GET"],
    ["/api/health/ready", "GET"],
    ["/api/v1/auth/register", "POST"],
    ["/api/v1/auth/login", "POST"],
    ["/api/v1/auth/logout", "POST"],
    ["/api/v1/auth/me", "GET"],
    ["/api/v1/organizations", "GET"],
    ["/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000", "GET"],
    ["/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000", "PATCH"],
    ["/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000/members", "GET"],
    ["/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000/projects", "GET"],
    ["/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000/projects", "POST"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000", "GET"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000", "PATCH"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/archive", "POST"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/tasks", "GET"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/tasks", "POST"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/board", "GET"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000", "GET"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000", "PATCH"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/transition", "POST"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/archive", "POST"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/comments", "GET"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/comments", "POST"],
    ["/api/v1/task-comments/123e4567-e89b-12d3-a456-426614174000", "PATCH"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/labels", "GET"],
    ["/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/labels", "POST"],
    ["/api/v1/labels/123e4567-e89b-12d3-a456-426614174000", "PATCH"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/labels/123e4567-e89b-12d3-a456-426614174001", "POST"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/labels/123e4567-e89b-12d3-a456-426614174001", "DELETE"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/dependencies", "GET"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/dependencies", "POST"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/dependencies/123e4567-e89b-12d3-a456-426614174001", "DELETE"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/activity", "GET"],
  ];

  approvedRoutes.forEach(([path, method]) => {
    it(`allows ${method} ${path}`, () => {
      expect(isRouteAllowed(path, method)).toBe(true);
    });
  });
});

describe("BFF handler: unknown paths rejected", () => {
  const unknownPaths = [
    ["/api/v1/unknown", "GET"],
    ["/api/admin/users", "GET"],
    ["/api/v1/auth/sessions", "GET"],
    ["/api/v1/tasks/hard-delete", "DELETE"],
    ["/api/", "GET"],
    ["", "GET"],
  ];

  unknownPaths.forEach(([path, method]) => {
    it(`rejects unknown path ${method} ${path}`, () => {
      expect(isRouteAllowed(path, method)).toBe(false);
    });
  });
});

describe("BFF handler: unsupported methods rejected", () => {
  const unsupportedMethods: [string, string][] = [
    ["/api/v1/auth/me", "POST"],
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000", "DELETE"], // No task hard-delete in Phase 4
    ["/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/activity", "POST"], // Activity is read-only
    ["/api/v1/task-comments/123e4567-e89b-12d3-a456-426614174000", "DELETE"], // No comment delete in Phase 4
    ["/api/v1/labels/123e4567-e89b-12d3-a456-426614174000", "DELETE"], // No label delete in Phase 4
  ];

  unsupportedMethods.forEach(([path, method]) => {
    it(`rejects ${method} ${path}`, () => {
      expect(isRouteAllowed(path, method)).toBe(false);
    });
  });
});
