'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button, buttonVariants } from '@/components/ui/button';

export function TaskBoard({ columns, projectId }: { columns: any[]; projectId: string }) {
  const router = useRouter();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuickTransition = async (taskId: string, currentVersion: number, targetStatus: string) => {
    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expected_version: currentVersion,
          target_status: targetStatus,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to transition task');
      }

      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">
          {error}
        </div>
      )}

      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Project Board</h2>
        <div className="flex gap-2">
          <Link href={`/app/projects/${projectId}/tasks`} className={buttonVariants({ variant: 'outline' })}>
            List View
          </Link>
          <Link href={`/app/projects/${projectId}/tasks/new`} className={buttonVariants({ variant: 'default' })}>
            + New Task
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-4 overflow-x-auto pb-4">
        {columns.map((col) => (
          <div key={col.status} className="bg-muted/30 p-3 rounded-lg border flex flex-col space-y-3 min-w-[220px]">
            <div className="flex justify-between items-center pb-2 border-b">
              <span className="font-bold text-xs uppercase text-muted-foreground">{col.status}</span>
              <span className="text-xs bg-muted font-semibold px-2 py-0.5 rounded-full">{col.total}</span>
            </div>

            <div className="space-y-3 flex-1">
              {col.items.map((t: any) => (
                <Card key={t.id} className="p-3 space-y-2 hover:border-primary/50 transition-colors">
                  <div className="flex justify-between items-start gap-1">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 bg-muted rounded">{t.display_id}</span>
                    <span className="text-[10px] uppercase font-semibold text-muted-foreground">{t.priority}</span>
                  </div>
                  <Link
                    href={`/app/projects/${projectId}/tasks/${t.id}`}
                    className="font-semibold text-sm hover:underline block leading-snug"
                  >
                    {t.title}
                  </Link>

                  <div className="pt-2 border-t flex justify-between items-center">
                    <select
                      className="text-xs border rounded p-1 bg-background text-foreground"
                      value={t.status}
                      disabled={isPending}
                      onChange={(e) => handleQuickTransition(t.id, t.version, e.target.value)}
                    >
                      <option value="backlog">Backlog</option>
                      <option value="ready">Ready</option>
                      <option value="in_progress">In Progress</option>
                      <option value="blocked">Blocked</option>
                      <option value="review">Review</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </Card>
              ))}

              {col.items.length === 0 && (
                <p className="text-xs text-muted-foreground italic text-center py-4">No tasks</p>
              )}
            </div>

            {col.has_more && (
              <div className="pt-2 text-center border-t">
                <Link
                  href={`/app/projects/${projectId}/tasks?status=${col.status}`}
                  className="text-xs text-primary font-medium hover:underline"
                >
                  View all {col.total} tasks →
                </Link>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
