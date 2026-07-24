'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export function TaskComments({
  comments,
  taskId,
  isArchived,
}: {
  comments: any[];
  taskId: string;
  isArchived: boolean;
}) {
  const router = useRouter();
  const [body, setBody] = useState('');
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!body.trim() || isArchived) return;

    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/tasks/${taskId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: body.trim() }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to add comment');
      }

      setBody('');
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
        <CardTitle className="text-lg">Comments ({comments.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">
            {error}
          </div>
        )}

        {!isArchived && (
          <form onSubmit={handleSubmit} className="space-y-2">
            <textarea
              className="w-full p-2 border rounded-md bg-background text-foreground border-input focus:ring-2"
              rows={3}
              placeholder="Add a comment..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />
            <Button type="submit" size="sm" disabled={!body.trim() || isPending}>
              {isPending ? 'Posting...' : 'Post Comment'}
            </Button>
          </form>
        )}

        <div className="space-y-3 pt-2">
          {comments.map((c) => (
            <div key={c.id} className="p-3 border rounded-md bg-muted/20 space-y-1">
              <div className="flex justify-between items-center text-xs text-muted-foreground">
                <span className="font-semibold">{c.author_id}</span>
                <span>{new Date(c.created_at).toLocaleString()}</span>
              </div>
              <p className="text-sm text-foreground whitespace-pre-wrap">{c.body}</p>
            </div>
          ))}
          {comments.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No comments yet.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
