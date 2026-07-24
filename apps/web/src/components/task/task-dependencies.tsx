'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function TaskDependencies({
  dependencies,
  taskId,
  isArchived,
}: {
  dependencies: any[];
  taskId: string;
  isArchived: boolean;
}) {
  const router = useRouter();
  const [targetId, setTargetId] = useState('');
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetId.trim() || isArchived) return;

    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/dependencies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ depends_on_task_id: targetId.trim() }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to add dependency');
      }

      setTargetId('');
      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  const handleRemove = async (depId: string) => {
    if (isArchived) return;
    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/dependencies/${depId}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to remove dependency');
      }

      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Dependencies ({dependencies.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">
            {error}
          </div>
        )}

        {!isArchived && (
          <form onSubmit={handleAdd} className="flex gap-2">
            <Input
              placeholder="Prerequisite Task UUID..."
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" size="sm" disabled={!targetId.trim() || isPending}>
              Add Dependency
            </Button>
          </form>
        )}

        <div className="space-y-2">
          {dependencies.map((dep) => (
            <div key={dep.id} className="flex justify-between items-center p-2 border rounded-md text-sm">
              <div>
                <span className="font-semibold text-xs px-2 py-0.5 bg-muted rounded mr-2">
                  {dep.depends_on_display_id}
                </span>
                <span className="text-xs text-muted-foreground">{dep.depends_on_task_id}</span>
              </div>
              {!isArchived && (
                <Button variant="ghost" size="sm" onClick={() => handleRemove(dep.id)} disabled={isPending}>
                  Remove
                </Button>
              )}
            </div>
          ))}
          {dependencies.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No prerequisite dependencies.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
