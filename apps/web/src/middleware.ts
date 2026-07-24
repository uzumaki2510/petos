import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE_NAME = process.env.SESSION_COOKIE_NAME || "petos_session";
const APP_ORIGIN = process.env.APP_ORIGIN || "http://localhost:3000";
const ALLOWED_ORIGINS = new Set([APP_ORIGIN, "http://localhost:3000", "http://127.0.0.1:3000"]);

const PUBLIC_PATHS = ["/login", "/register", "/"];
const API_PREFIX = "/api";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Basic CSRF Origin validation for mutative requests to the API
  if (pathname.startsWith(API_PREFIX) && ["POST", "PUT", "PATCH", "DELETE"].includes(request.method)) {
    const origin = request.headers.get("origin");
    if (origin && !ALLOWED_ORIGINS.has(origin)) {
      return NextResponse.json({ error: "Invalid origin" }, { status: 403 });
    }
  }

  // Cookie-presence middleware
  const hasSession =
    request.cookies.has(SESSION_COOKIE_NAME) ||
    request.cookies.has("__Host-petos_session") ||
    request.cookies.has("petos_session");

  // Ignore Next.js internals, static files, and API routes for redirection
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith(API_PREFIX) ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // If on a public path and logged in, redirect to dashboard
  if (hasSession && PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.redirect(new URL("/app", request.url));
  }

  // If on a protected path and NOT logged in, redirect to login
  if (!hasSession && !PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
