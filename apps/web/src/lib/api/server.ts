import { cookies } from "next/headers";

const BACKEND_URL = process.env.API_INTERNAL_URL || process.env.API_URL || "http://localhost:8000";
const BFF_SECRET = process.env.BFF_INTERNAL_SECRET || "default_bff_secret_for_local_dev";
const SESSION_COOKIE_NAME = process.env.SESSION_COOKIE_NAME || "petos_session";

export async function fetchServerApi(path: string, options: RequestInit = {}) {
  // Wait for cookies explicitly (Next.js 15 requirement)
  const cookieStore = await cookies();
  const sessionCookie = cookieStore.get(SESSION_COOKIE_NAME) || cookieStore.get("__Host-petos_session") || cookieStore.get("petos_session");

  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("Accept", "application/json");
  headers.set("X-PetOS-BFF-Secret", BFF_SECRET);
  headers.set("X-PetOS-Client-IP", "127.0.0.1"); // Server-side rendering

  if (sessionCookie) {
    headers.set("Cookie", `${sessionCookie.name}=${sessionCookie.value}`);
  }

  const url = `${BACKEND_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers,
  });

  // Try to parse JSON, if it fails, return text
  let data;
  try {
    data = await res.json();
  } catch (e) {
    data = await res.text();
  }

  if (!res.ok) {
    const msg = typeof data === "object" ? (data?.error?.message || data?.message || data?.detail || "An error occurred") : data;
    throw new Error(String(msg));
  }

  return data;
}

export async function getCurrentUser() {
  try {
    return await fetchServerApi("/v1/auth/me");
  } catch (e) {
    return null;
  }
}

export async function getUserOrganizations() {
  try {
    const data = await fetchServerApi("/v1/organizations");
    return data.items || [];
  } catch (e) {
    return [];
  }
}

export async function getOrganizationProjects(orgId: string) {
  try {
    const data = await fetchServerApi(`/v1/organizations/${orgId}/projects`);
    return data.items || [];
  } catch (e) {
    return [];
  }
}

export async function getProject(projectId: string) {
  try {
    return await fetchServerApi(`/v1/projects/${projectId}`);
  } catch (e) {
    return null;
  }
}
