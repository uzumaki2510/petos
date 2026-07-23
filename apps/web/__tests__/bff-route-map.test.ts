import { describe, it, expect } from "vitest";
import { isRouteAllowed } from "@/lib/api/route-map";

describe("BFF route allowlist", () => {
  it("allows GET /api/health/live", () => {
    expect(isRouteAllowed("/api/health/live", "GET")).toBe(true);
  });

  it("allows POST /api/v1/auth/register", () => {
    expect(isRouteAllowed("/api/v1/auth/register", "POST")).toBe(true);
  });

  it("allows POST /api/v1/auth/login", () => {
    expect(isRouteAllowed("/api/v1/auth/login", "POST")).toBe(true);
  });

  it("allows POST /api/v1/auth/logout", () => {
    expect(isRouteAllowed("/api/v1/auth/logout", "POST")).toBe(true);
  });

  it("allows GET /api/v1/auth/me", () => {
    expect(isRouteAllowed("/api/v1/auth/me", "GET")).toBe(true);
  });

  it("allows GET /api/v1/organizations", () => {
    expect(isRouteAllowed("/api/v1/organizations", "GET")).toBe(true);
  });

  it("allows GET /api/v1/organizations/{uuid}", () => {
    expect(isRouteAllowed("/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000", "GET")).toBe(true);
  });

  it("allows PATCH /api/v1/organizations/{uuid}", () => {
    expect(isRouteAllowed("/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000", "PATCH")).toBe(true);
  });

  it("allows GET /api/v1/organizations/{uuid}/projects", () => {
    expect(isRouteAllowed("/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000/projects", "GET")).toBe(true);
  });

  it("allows POST /api/v1/organizations/{uuid}/projects", () => {
    expect(isRouteAllowed("/api/v1/organizations/123e4567-e89b-12d3-a456-426614174000/projects", "POST")).toBe(true);
  });

  it("allows GET /api/v1/projects/{uuid}", () => {
    expect(isRouteAllowed("/api/v1/projects/123e4567-e89b-12d3-a456-426614174000", "GET")).toBe(true);
  });

  it("allows PATCH /api/v1/projects/{uuid}", () => {
    expect(isRouteAllowed("/api/v1/projects/123e4567-e89b-12d3-a456-426614174000", "PATCH")).toBe(true);
  });

  it("allows POST /api/v1/projects/{uuid}/archive", () => {
    expect(isRouteAllowed("/api/v1/projects/123e4567-e89b-12d3-a456-426614174000/archive", "POST")).toBe(true);
  });

  it("rejects DELETE on allowed paths", () => {
    expect(isRouteAllowed("/api/v1/auth/me", "DELETE")).toBe(false);
  });

  it("rejects unknown paths", () => {
    expect(isRouteAllowed("/api/v1/unknown/path", "GET")).toBe(false);
  });

  it("rejects admin paths that do not exist", () => {
    expect(isRouteAllowed("/api/admin/users", "GET")).toBe(false);
  });

  it("rejects GET on auth routes that only allow POST", () => {
    expect(isRouteAllowed("/api/v1/auth/login", "GET")).toBe(false);
  });
});
