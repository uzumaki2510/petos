"use client";

import { useEffect, useState } from "react";

type BackendStatus = {
  status: string;
  postgres: string;
  redis: string;
  version: string;
};

export default function StatusDisplay() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkStatus() {
      try {
        const res = await fetch(`/api/foundation-status`);
        const data = await res.json();
        
        if (!res.ok) {
          throw new Error(data.error || `HTTP error! status: ${res.status}`);
        }
        
        setBackendStatus(data);
      } catch (e: unknown) {
        if (e instanceof Error) {
          setError(e.message || "Failed to connect to backend");
        } else {
          setError("Failed to connect to backend");
        }
      }
    }
    checkStatus();
  }, []);

  return (
    <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="p-4 bg-gray-50 rounded-md border">
        <dt className="text-sm font-medium text-gray-500">Frontend Status</dt>
        <dd className="mt-1 text-lg font-semibold text-green-700" data-testid="frontend-status">Ready (Running)</dd>
      </div>

      <div className="p-4 bg-gray-50 rounded-md border">
        <dt className="text-sm font-medium text-gray-500">Backend API</dt>
        <dd data-testid="backend-status" className={`mt-1 text-lg font-semibold ${error ? 'text-red-600' : (backendStatus?.status === 'ok' ? 'text-green-700' : 'text-yellow-600')}`}>
          {error ? `Disconnected: ${error}` : (backendStatus ? `Ready (v${backendStatus.version})` : "Loading...")}
        </dd>
      </div>

      <div className="p-4 bg-gray-50 rounded-md border">
        <dt className="text-sm font-medium text-gray-500">PostgreSQL</dt>
        <dd data-testid="postgres-status" className={`mt-1 text-lg font-semibold ${backendStatus?.postgres === 'ok' ? 'text-green-700' : (backendStatus?.postgres ? 'text-red-600' : 'text-gray-400')}`}>
          {backendStatus?.postgres === 'ok' ? 'Connected' : (backendStatus?.postgres || 'Unknown')}
        </dd>
      </div>

      <div className="p-4 bg-gray-50 rounded-md border">
        <dt className="text-sm font-medium text-gray-500">Redis</dt>
        <dd data-testid="redis-status" className={`mt-1 text-lg font-semibold ${backendStatus?.redis === 'ok' ? 'text-green-700' : (backendStatus?.redis ? 'text-red-600' : 'text-gray-400')}`}>
          {backendStatus?.redis === 'ok' ? 'Connected' : (backendStatus?.redis || 'Unknown')}
        </dd>
      </div>
    </dl>
  );
}
