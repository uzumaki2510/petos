'use server';

import { cookies } from 'next/headers';
import { fetchServerApi } from '@/lib/api/server';

export async function loginAction(data: any) {
  try {
    const response = await fetchServerApi('/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // The server helper fetches through the proxy which might not set the cookie
    // Wait, the BFF proxy `/api/[...path]/route.ts` runs when called from the browser.
    // fetchServerApi bypasses the BFF proxy and talks directly to the backend!
    // But fetchServerApi DOES NOT receive the Set-Cookie header in the response, because `res.json()` returns the body.
    // We should either return headers from fetchServerApi, or have client components use fetch('/api/v1/auth/login').

    // Actually, Server Actions can't easily proxy cookies from a direct fetch unless we manually get the Response object.
    return { success: true, data: response };
  } catch (error: any) {
    return { success: false, error: error.message || 'Login failed' };
  }
}

export async function registerAction(data: any) {
  try {
    const response = await fetchServerApi('/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return { success: true, data: response };
  } catch (error: any) {
    return { success: false, error: error.message || 'Registration failed' };
  }
}

export async function logoutAction() {
  try {
    await fetchServerApi('/v1/auth/logout', { method: 'POST' });
  } catch (error) {}

  const cookieStore = await cookies();
  const sessionCookie = process.env.SESSION_COOKIE_NAME || "petos_session";
  cookieStore.delete(sessionCookie);

  return { success: true };
}

export async function getCurrentUser() {
  try {
    const data = await fetchServerApi('/v1/auth/me');
    return { data };
  } catch (error) {
    return { data: null };
  }
}
