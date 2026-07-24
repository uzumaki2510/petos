'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';

export function TaskDetail({ task, projectId }: { task: any; projectId: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);
  const [reason, setReason] = useState('');
  const [showReasonDialog, setShowReasonDialog] = useState<string | null>(null);

  const handleTransition = async (targetStatus: string, reqReason?: string) => {
    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${task.id}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expected_version: task.version,
          target_status: targetStatus,
          reason: reqReason || undefined,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to transition task');
      }

      setShowReasonDialog(null);
      setReason('');
      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  const handleArchive = async () => {
    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${task.id}/archive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          expected_version: task.version,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to archive task');
      }

      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {task.archived_at && (
        <div className="p-3 text-sm text-amber-800 bg-amber-100 dark:bg-amber-900/30 rounded-md">
          This task was archived on {new Date(task.archived_at).toLocaleString()}. It is now read-only.
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <span className="text-xs font-semibold px-2 py-1 bg-muted rounded-md mr-2">{task.display_id}</span>
            <span
              data-testid="task-status"
              className="text-xs uppercase px-2 py-1 rounded-md font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
            >
              {task.status?.toUpperCase()}
            </span>
          </div>
          <div className="flex gap-2">
            {!task.archived_at && (
              <Button variant="destructive" size="sm" onClick={handleArchive} disabled={isPending}>
                Archive Task
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <h1 className="text-2xl font-bold">{task.title}</h1>

          {task.description && (
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">Description</h3>
              <p className="whitespace-pre-wrap">{task.description}</p>
            </div>
          )}

          {task.acceptance_criteria && (
            <div>
              <h3 className="text-sm font-semibold text-muted-foreground uppercase mb-1">Acceptance Criteria</h3>
              <p className="whitespace-pre-wrap bg-muted/40 p-3 rounded-md border">{task.acceptance_criteria}</p>
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm pt-4 border-t">
            <div>
              <span className="text-muted-foreground block">Priority</span>
              <span className="font-semibold uppercase">{task.priority}</span>
            </div>
            <div>
              <span className="text-muted-foreground block">Version</span>
              <span className="font-semibold">{task.version}</span>
            </div>
            <div>
              <span className="text-muted-foreground block">Started At</span>
              <span>{task.started_at ? new Date(task.started_at).toLocaleDateString() : 'Not started'}</span>
            </div>
            <div>
              <span className="text-muted-foreground block">Completed At</span>
              <span>{task.completed_at ? new Date(task.completed_at).toLocaleDateString() : 'Not completed'}</span>
            </div>
          </div>

          {!task.archived_at && (
            <div className="pt-4 border-t space-y-2">
              <h3 className="text-sm font-semibold uppercase">Status Transitions</h3>
              <div className="flex flex-wrap gap-2">
                {task.status === 'backlog' && (
                  <Button size="sm" onClick={() => handleTransition('ready')} disabled={isPending}>
                    Move to Ready
                  </Button>
                )}
                {task.status === 'ready' && (
                  <Button size="sm" onClick={() => handleTransition('in_progress')} disabled={isPending}>
                    Start Task (In Progress)
                  </Button>
                )}
                {task.status === 'in_progress' && (
                  <>
                    <Button size="sm" variant="secondary" onClick={() => handleTransition('blocked')} disabled={isPending}>
                      Mark Blocked
                    </Button>
                    <Button size="sm" onClick={() => handleTransition('review')} disabled={isPending}>
                      Submit for Review
                    </Button>
                  </>
                )}
                {task.status === 'blocked' && (
                  <Button size="sm" onClick={() => handleTransition('in_progress')} disabled={isPending}>
                    Resume (In Progress)
                  </Button>
                )}
                {task.status === 'review' && (
                  <>
                    <Button size="sm" variant="outline" onClick={() => handleTransition('in_progress')} disabled={isPending}>
                      Request Changes
                    </Button>
                    <Button size="sm" onClick={() => handleTransition('completed')} disabled={isPending}>
                      Complete Task
                    </Button>
                  </>
                )}
                {task.status === 'completed' && (
                  <Button size="sm" variant="outline" onClick={() => setShowReasonDialog('in_progress')} disabled={isPending}>
                    Reopen Task
                  </Button>
                )}
                {task.status === 'cancelled' && (
                  <Button size="sm" variant="outline" onClick={() => setShowReasonDialog('backlog')} disabled={isPending}>
                    Reopen to Backlog
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {showReasonDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-background p-6 rounded-lg max-w-md w-full space-y-4 border shadow-lg">
            <h3 className="text-lg font-bold">Reopen Task</h3>
            <p className="text-sm text-muted-foreground">Please provide a reason for reopening this task.</p>
            <textarea
              className="w-full p-2 border rounded-md bg-background text-foreground"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Reason for reopening..."
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowReasonDialog(null)}>
                Cancel
              </Button>

              <Button
                disabled={!reason.trim() || isPending}
                onClick={() => handleTransition(showReasonDialog, reason)}
              >
                Confirm Reopen
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
