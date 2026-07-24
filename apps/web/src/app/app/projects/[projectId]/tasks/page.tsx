import { fetchServerApi } from '@/lib/api/server';
import { TaskList } from '@/components/task/task-list';
import type { PaginatedTaskResponse } from '@/lib/api/generated';

export const dynamic = 'force-dynamic';

export default async function ProjectTasksPage({
  params,
  searchParams,
}: {
  params: Promise<{ projectId: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedParams = await params;
  const resolvedSearch = await searchParams;

  const query = new URLSearchParams();
  if (resolvedSearch.status) query.set('status', String(resolvedSearch.status));
  if (resolvedSearch.search) query.set('search', String(resolvedSearch.search));

  const queryString = query.toString() ? `?${query.toString()}` : '';

  let data: PaginatedTaskResponse = { items: [], total: 0, limit: 20, offset: 0 };
  try {
    data = await fetchServerApi<PaginatedTaskResponse>(`/v1/projects/${resolvedParams.projectId}/tasks${queryString}`);
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Project Tasks</h1>
        <p className="text-muted-foreground">Manage and track issues, user stories, and features.</p>
      </div>

      <TaskList
        tasks={data.items || []}
        total={data.total || 0}
        projectId={resolvedParams.projectId}
        initialFilters={{ search: resolvedSearch.search }}
      />
    </div>
  );
}
