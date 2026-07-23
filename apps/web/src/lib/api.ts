import { createClient } from '@/lib/api/generated/client';
import { cookies } from 'next/headers';

const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // Browser should use the proxy or relative path
    return '';
  }

  // Server should use internal URL if available or external
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

export const client = createClient({
  baseUrl: getBaseUrl(),
});

// Interceptor to attach session cookie on server-side requests
client.interceptors.request.use(async (request: Request) => {
  if (typeof window === 'undefined') {
    // We are on the server
    const cookieStore = await cookies();
    const isDevelopment = process.env.NODE_ENV === 'development';
    const cookieName = isDevelopment ? 'petos_session' : '__Host-petos_session';

    const sessionCookie = cookieStore.get(cookieName);
    if (sessionCookie) {
      request.headers.set('Cookie', `${cookieName}=${sessionCookie.value}`);
    }
  }
  return request;
});
