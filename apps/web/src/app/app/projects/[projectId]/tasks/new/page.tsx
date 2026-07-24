import { fetchServerApi } from '@/lib/api/server';
import { TaskForm } from '@/components/task/task-form';

export default async function NewTaskPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const resolvedParams = await params;
  let project: any = null;
  try {
    project = await fetchServerApi(`/v1/projects/${resolvedParams.projectId}`);
  } catch (error) {
    console.error('Failed to fetch project:', error);
  }

  return (
    <div className="p-6 space-y-6 flex justify-center">
      <TaskForm projectId={resolvedParams.projectId} orgId={project?.organization_id} />
    </div>
  );
}
