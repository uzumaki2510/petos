import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { TaskList } from '../src/components/task/task-list';
import type { TaskResponse } from '../src/lib/api/generated';

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
  }),
}));

test('TaskList renders display_id (PET-1) and task title (Task One)', () => {
  const mockTask: TaskResponse = {
    id: 'test-task-id',
    project_id: 'test-project-id',
    project_key: 'PET',
    task_number: 1,
    display_id: 'PET-1',
    title: 'Task One',
    status: 'backlog',
    priority: 'medium',
    created_by: 'user-id',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    version: 1,
  };

  render(<TaskList tasks={[mockTask]} total={1} projectId="test-project-id" />);

  expect(screen.getByText('PET-1')).toBeDefined();
  expect(screen.getByText('Task One')).toBeDefined();
});
