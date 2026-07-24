import { notFound } from 'next/navigation';
import { fetchServerApi } from '@/lib/api/server';
import { TaskDetail } from '@/components/task/task-detail';
import { TaskComments } from '@/components/task/task-comments';
import { TaskDependencies } from '@/components/task/task-dependencies';
import { TaskLabels } from '@/components/task/task-labels';
import { TaskActivityTimeline } from '@/components/task/task-activity-timeline';

export const dynamic = 'force-dynamic';

export default async function TaskDetailPage({
  params,
}: {
  params: Promise<{ projectId: string; taskId: string }>;
}) {
  const resolvedParams = await params;

  let task: any;
  let commentsData: any = { items: [] };
  let deps: any = [];
  let actData: any = { items: [] };

  try {
    const [taskRes, commentsRes, depsRes, actRes] = await Promise.all([
      fetchServerApi(`/v1/tasks/${resolvedParams.taskId}`),
      fetchServerApi(`/v1/tasks/${resolvedParams.taskId}/comments`),
      fetchServerApi(`/v1/tasks/${resolvedParams.taskId}/dependencies`),
      fetchServerApi(`/v1/tasks/${resolvedParams.taskId}/activity`),
    ]);
    task = taskRes;
    commentsData = commentsRes;
    deps = depsRes;
    actData = actRes;
  } catch (error) {
    notFound();
  }

  if (!task) {
    notFound();
  }

  const isArchived = Boolean(task.archived_at);

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      <TaskDetail task={task} projectId={resolvedParams.projectId} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <TaskComments comments={commentsData.items || []} taskId={task.id} isArchived={isArchived} />
          <TaskActivityTimeline activities={actData.items || []} />
        </div>

        <div className="space-y-6">
          <TaskLabels labels={task.labels || []} />
          <TaskDependencies dependencies={deps || []} taskId={task.id} isArchived={isArchived} />
        </div>
      </div>
    </div>
  );
}
