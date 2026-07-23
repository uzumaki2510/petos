/**
 * BFF Route Allowlist
 *
 * Only these exact paths and methods may be proxied by the BFF.
 * UUIDs are validated against a strict RFC 4122 pattern.
 * Anything not on this list returns 404.
 */

// RFC 4122 UUID: 8-4-4-4-12 hex chars
const UUID_RE = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";

/** Static routes: exact pathname → allowed methods */
export const STATIC_ROUTES: Record<string, readonly string[]> = {
  "/api/health/live": ["GET"],
  "/api/health/ready": ["GET"],
  "/api/v1/auth/register": ["POST"],
  "/api/v1/auth/login": ["POST"],
  "/api/v1/auth/logout": ["POST"],
  "/api/v1/auth/me": ["GET"],
  "/api/v1/organizations": ["GET"],
};

/** Dynamic route entries: [pattern, allowed methods] */
const DYNAMIC_ROUTES: [RegExp, readonly string[]][] = [
  // GET|PATCH /api/v1/organizations/{uuid}
  [new RegExp(`^\\/api\\/v1\\/organizations\\/${UUID_RE}$`), ["GET", "PATCH"]],
  // GET|POST /api/v1/organizations/{uuid}/projects
  [new RegExp(`^\\/api\\/v1\\/organizations\\/${UUID_RE}\\/projects$`), ["GET", "POST"]],
  // GET|PATCH /api/v1/projects/{uuid}
  [new RegExp(`^\\/api\\/v1\\/projects\\/${UUID_RE}$`), ["GET", "PATCH"]],
  // POST /api/v1/projects/{uuid}/archive
  [new RegExp(`^\\/api\\/v1\\/projects\\/${UUID_RE}\\/archive$`), ["POST"]],
];

/**
 * Returns true if the given pathname + method is on the BFF allowlist.
 * Path must match exactly (including UUID format). Method must be allowed.
 */
export function isRouteAllowed(pathname: string, method: string): boolean {
  if (!pathname || !method) return false;

  // Static exact match
  if (STATIC_ROUTES[pathname]?.includes(method)) {
    return true;
  }

  // Dynamic pattern match
  for (const [pattern, methods] of DYNAMIC_ROUTES) {
    if (pattern.test(pathname) && methods.includes(method)) {
      return true;
    }
  }

  return false;
}
