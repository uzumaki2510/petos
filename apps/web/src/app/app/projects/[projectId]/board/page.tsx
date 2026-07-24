import { fetchServerApi } from '@/lib/api/server';
import { TaskBoard } from '@/components/task/task-board';

export const dynamic = 'force-dynamic';

export default async function ProjectBoardPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const resolvedParams = await params;
  let data: any = { columns: [] };
  try {
    data = await fetchServerApi(`/v1/projects/${resolvedParams.projectId}/board`);
  } catch (error) {
    console.error('Failed to fetch board:', error);
  }

  return (
    <div className="p-6 space-y-6">
      <TaskBoard columns={data.columns || []} projectId={resolvedParams.projectId} />
    </div>
  );
}
