import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { expect, test, vi, beforeEach } from 'vitest';
import { TaskDetail } from '../src/components/task/task-detail';

const mockRefresh = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: mockRefresh,
  }),
}));

const mockTask = {
  id: 'test-task-id',
  project_id: 'test-project-id',
  project_key: 'PET',
  task_number: 1,
  display_id: 'PET-1',
  title: 'Task One',
  description: 'Detailed description',
  acceptance_criteria: 'Given task exists...',
  status: 'backlog',
  priority: 'medium',
  version: 1,
  created_by: 'user-id',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

beforeEach(() => {
  vi.restoreAllMocks();
  mockRefresh.mockReset();
  // Mock global fetch
  global.fetch = vi.fn();
});

test('TaskDetail renders initial backlog status as BACKLOG on data-testid="task-status"', () => {
  render(<TaskDetail task={mockTask} projectId="test-project-id" />);

  const statusBadge = screen.getByTestId('task-status');
  expect(statusBadge).toBeDefined();
  expect(statusBadge.textContent).toBe('BACKLOG');
});

test('Clicking Move to Ready sends target_status="ready" with expected_version and calls router.refresh on success', async () => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: true,
    json: async () => ({ ...mockTask, status: 'ready', version: 2 }),
  });

  render(<TaskDetail task={mockTask} projectId="test-project-id" />);

  const moveButton = screen.getByText('Move to Ready');
  fireEvent.click(moveButton);

  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith('/api/v1/tasks/test-task-id/transition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        expected_version: 1,
        target_status: 'ready',
        reason: undefined,
      }),
    });
  });

  await waitFor(() => {
    expect(mockRefresh).toHaveBeenCalled();
  });
});

test('Failed transition displays error message instead of silently succeeding', async () => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: false,
    json: async () => ({ error: { message: 'Invalid status transition' } }),
  });

  render(<TaskDetail task={mockTask} projectId="test-project-id" />);

  const moveButton = screen.getByText('Move to Ready');
  fireEvent.click(moveButton);

  await waitFor(() => {
    expect(screen.getByText('Invalid status transition')).toBeDefined();
  });
  expect(mockRefresh).not.toHaveBeenCalled();
});
