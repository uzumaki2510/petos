'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

import type { TaskResponse } from '@/lib/api/generated';

export function TaskList({
  tasks,
  total,
  projectId,
  initialFilters,
}: {
  tasks: TaskResponse[];
  total: number;
  projectId: string;
  initialFilters?: any;
}) {
  const [search, setSearch] = useState(initialFilters?.search || '');

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Input
            placeholder="Search tasks by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full sm:w-64"
          />
        </div>
        <div className="flex gap-2">
          <Link href={`/app/projects/${projectId}/board`} className={buttonVariants({ variant: 'outline' })}>
            Board View
          </Link>
          <Link href={`/app/projects/${projectId}/tasks/new`} className={buttonVariants({ variant: 'default' })}>
            + New Task
          </Link>
        </div>
      </div>

      <div className="space-y-3">
        {tasks.map((t) => (
          <Card key={t.id} className="hover:border-primary/50 transition-colors">
            <CardContent className="p-4 flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold px-2 py-0.5 bg-muted rounded">{t.display_id}</span>
                  <Link href={`/app/projects/${projectId}/tasks/${t.id}`} className="font-bold hover:underline">
                    {t.title}
                  </Link>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="uppercase font-semibold">{t.priority}</span>
                  <span>•</span>
                  <span>Created {new Date(t.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs uppercase px-2.5 py-1 rounded-md font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {t.status}
                </span>
                <Link
                  href={`/app/projects/${projectId}/tasks/${t.id}`}
                  className={buttonVariants({ variant: 'ghost', size: 'sm' })}
                >
                  View →
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}

        {tasks.length === 0 && (
          <Card>
            <CardContent className="p-8 text-center text-muted-foreground">
              No tasks found. Create one to get started!
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
