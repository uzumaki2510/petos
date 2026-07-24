'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button, buttonVariants } from '@/components/ui/button';
import Link from 'next/link';

import { createProjectTask } from '@/app/actions/task';

const formSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().max(50000).optional(),
  acceptance_criteria: z.string().max(50000).optional(),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  assigned_to: z.string().optional().or(z.literal('')),
  due_at: z.string().optional().or(z.literal('')),
});

type FormData = z.infer<typeof formSchema>;

export function TaskForm({ projectId, orgId }: { projectId: string; orgId?: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);
  const [members, setMembers] = useState<Array<{ user_id: string; display_name: string }>>([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      priority: 'medium',
    },
  });

  useEffect(() => {
    if (orgId) {
      fetch(`/api/v1/organizations/${orgId}/members`)
        .then((res) => (res.ok ? res.json() : { items: [] }))
        .then((data) => setMembers(data.items || []))
        .catch(() => setMembers([]));
    }
  }, [orgId]);

  const onSubmit = async (data: FormData) => {
    setIsPending(true);
    setError(null);
    try {
      const res = await createProjectTask(projectId, {
        title: data.title,
        description: data.description || null,
        acceptance_criteria: data.acceptance_criteria || null,
        priority: data.priority,
        assigned_to: data.assigned_to || null,
        due_at: data.due_at ? new Date(data.due_at).toISOString() : null,
      });

      if (!res.success) {
        throw new Error(res.error || 'Failed to create task');
      }

      router.push(`/app/projects/${projectId}/tasks`);
      router.refresh();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle>Create Task</CardTitle>
        <CardDescription>Add a new task to this project.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="title">Task Title</Label>
            <Input id="title" placeholder="e.g. Implement OAuth Flow" {...register('title')} />
            {errors.title && <p className="text-sm text-red-500">{errors.title.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              rows={4}
              className="w-full p-2 border rounded-md bg-background text-foreground border-input focus:ring-2 focus:ring-ring"
              placeholder="Detailed task description..."
              {...register('description')}
            />
            {errors.description && <p className="text-sm text-red-500">{errors.description.message}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="acceptance_criteria">Acceptance Criteria</Label>
            <textarea
              id="acceptance_criteria"
              rows={3}
              className="w-full p-2 border rounded-md bg-background text-foreground border-input focus:ring-2 focus:ring-ring"
              placeholder="Given... When... Then..."
              {...register('acceptance_criteria')}
            />
            {errors.acceptance_criteria && (
              <p className="text-sm text-red-500">{errors.acceptance_criteria.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="w-full p-2 border rounded-md bg-background text-foreground border-input"
                {...register('priority')}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="assigned_to">Assignee</Label>
              <select
                id="assigned_to"
                className="w-full p-2 border rounded-md bg-background text-foreground border-input"
                {...register('assigned_to')}
              >
                <option value="">Unassigned</option>
                {members.map((m) => (
                  <option key={m.user_id} value={m.user_id}>
                    {m.display_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="due_at">Due Date</Label>
            <Input id="due_at" type="datetime-local" {...register('due_at')} />
          </div>
        </CardContent>
        <CardFooter className="flex items-center justify-between">
          <Link href={`/app/projects/${projectId}/tasks`} prefetch={false} className={buttonVariants({ variant: 'outline' })}>
            Cancel
          </Link>
          <Button id="create-task-submit" type="submit" disabled={isPending}>
            {isPending ? 'Creating...' : 'Create Task'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
