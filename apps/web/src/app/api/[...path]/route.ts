import { NextRequest, NextResponse } from "next/server";
import { isRouteAllowed } from "@/lib/api/route-map";

const BACKEND_URL = process.env.API_INTERNAL_URL || process.env.API_URL || "http://localhost:8000";
const BFF_SECRET = process.env.BFF_INTERNAL_SECRET || "default_bff_secret_for_local_dev";

async function handleProxy(req: NextRequest) {
  const { pathname, search } = new URL(req.url);

  // Reject unknown paths / unsupported methods
  if (!isRouteAllowed(pathname, req.method)) {
    return NextResponse.json({ error: { code: "not_found", message: "Not found", request_id: "bff" } }, { status: 404 });
  }

  // Reject oversized bodies (> 1MB)
  const contentLength = Number(req.headers.get("content-length") || 0);
  if (contentLength > 1024 * 1024) {
    return NextResponse.json({ error: { code: "payload_too_large", message: "Payload too large", request_id: "bff" } }, { status: 413 });
  }

  const backendUrl = `${BACKEND_URL}${pathname.replace('/api', '')}${search}`;

  // Forward headers securely
  const headers = new Headers();
  headers.set("Content-Type", req.headers.get("content-type") || "application/json");
  headers.set("Accept", "application/json");
  headers.set("X-PetOS-BFF-Secret", BFF_SECRET);

  // Forward client IP (trusted only because BFF controls all outbound requests)
  const forwardedFor = req.headers.get("x-forwarded-for");
  const clientIp = forwardedFor ? forwardedFor.split(",")[0].trim() : "unknown";
  headers.set("X-PetOS-Client-IP", clientIp);

  // Forward cookie
  const cookie = req.headers.get("cookie");
  if (cookie) {
    headers.set("cookie", cookie);
  }

  let body: BodyInit | null = null;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.text();
  }

  try {
    const backendRes = await fetch(backendUrl, {
      method: req.method,
      headers,
      body,
      redirect: "manual",
    });

    const responseHeaders = new Headers(backendRes.headers);

    // Preserve content-type header
    const safeHeaders = new Headers();
    const contentType = responseHeaders.get("content-type");
    if (contentType) safeHeaders.set("content-type", contentType);

    const data = await backendRes.text();
    const res = new NextResponse(data, {
      status: backendRes.status,
      headers: safeHeaders,
    });

    // Forward all Set-Cookie headers using getSetCookie if available
    const setCookieHeaders = typeof backendRes.headers.getSetCookie === "function"
      ? backendRes.headers.getSetCookie()
      : (responseHeaders.get("set-cookie") ? [responseHeaders.get("set-cookie")!] : []);

    for (const cookieHeader of setCookieHeaders) {
      if (cookieHeader) {
        res.headers.append("set-cookie", cookieHeader);
      }
    }

    return res;
  } catch (error) {
    console.error("BFF proxy error:", error);
    return NextResponse.json({ error: { code: "internal_error", message: "Internal server error", request_id: "bff" } }, { status: 500 });
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PATCH = handleProxy;
export const DELETE = handleProxy;
export const PUT = handleProxy;
