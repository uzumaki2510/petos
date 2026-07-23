'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button, buttonVariants } from '@/components/ui/button';
import Link from 'next/link';

const formSchema = z.object({
  name: z.string().min(1, 'Name must be at least 1 character').max(255),
  description: z.string().max(1000).optional(),
});

type FormData = z.infer<typeof formSchema>;

export function ProjectForm({ orgId }: { orgId: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = async (data: FormData) => {
    setIsPending(true);
    setError(null);
    try {
      const res = await fetch(`/api/v1/organizations/${orgId}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: data.name,
          description: data.description || null,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error?.message || 'Failed to create project');
      }

      router.push('/app/projects');
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
        <CardTitle>Create Project</CardTitle>
        <CardDescription>Add a new project to your workspace.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {error && (
            <div className="p-3 text-sm text-red-500 bg-red-100 dark:bg-red-900/30 rounded-md">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="name">Project Name</Label>
            <Input id="name" placeholder="My Awesome Project" {...register('name')} />
            {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input id="description" placeholder="Optional project description" {...register('description')} />
            {errors.description && <p className="text-sm text-red-500">{errors.description.message}</p>}
          </div>
        </CardContent>
        <CardFooter className="flex items-center justify-between">
          <Link href="/app/projects" className={buttonVariants({ variant: "outline" })}>
            Cancel
          </Link>
          <Button id="create-project-submit" type="submit" disabled={isPending}>
            {isPending ? 'Creating...' : 'Create Project'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
