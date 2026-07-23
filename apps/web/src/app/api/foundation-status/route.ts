import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const internalUrl = process.env.API_INTERNAL_URL || 'http://localhost:8000';
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

  try {
    const res = await fetch(`${internalUrl}/health/ready`, {
      signal: controller.signal,
      cache: 'no-store'
    });
    
    clearTimeout(timeoutId);
    
    if (!res.ok) {
      return NextResponse.json(
        { error: `Backend responded with status: ${res.status}` },
        { status: res.status }
      );
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: unknown) {
    clearTimeout(timeoutId);
    let errorMessage = "Failed to connect to backend";
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
         errorMessage = "Backend connection timed out";
      } else {
         errorMessage = error.message;
      }
    }
    return NextResponse.json(
      { error: errorMessage },
      { status: 503 }
    );
  }
}
