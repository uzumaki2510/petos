import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { TaskActivityTimeline } from '../src/components/task/task-activity-timeline';

const mockActivities = [
  {
    id: 'act-1',
    task_id: 'test-task-id',
    actor_id: 'user-1',
    event_type: 'task.transitioned',
    previous_value: 'backlog',
    new_value: 'ready',
    created_at: new Date('2026-07-24T12:00:00Z').toISOString(),
  },
  {
    id: 'act-2',
    task_id: 'test-task-id',
    actor_id: 'user-1',
    event_type: 'task.transitioned',
    previous_value: 'ready',
    new_value: 'in_progress',
    created_at: new Date('2026-07-24T12:05:00Z').toISOString(),
  },
  {
    id: 'act-3',
    task_id: 'test-task-id',
    actor_id: 'user-1',
    event_type: 'task.transitioned',
    previous_value: 'in_progress',
    new_value: 'review',
    created_at: new Date('2026-07-24T12:10:00Z').toISOString(),
  },
  {
    id: 'act-4',
    task_id: 'test-task-id',
    actor_id: 'user-1',
    event_type: 'task.transitioned',
    previous_value: 'review',
    new_value: 'completed',
    created_at: new Date('2026-07-24T12:15:00Z').toISOString(),
  },
];

test('TaskActivityTimeline renders activity timeline container and 4 transition event rows', () => {
  const { container } = render(<TaskActivityTimeline activities={mockActivities} />);

  const timelineContainer = screen.getByTestId('activity-timeline');
  expect(timelineContainer).toBeDefined();

  const activityEvents = screen.getAllByTestId('activity-event');
  expect(activityEvents.length).toBe(4);

  const transitionEvents = container.querySelectorAll('[data-event-type="task.transitioned"]');
  expect(transitionEvents.length).toBe(4);

  expect(screen.getByText(/backlog →/)).toBeDefined();
  expect(screen.getByText(/ready →/)).toBeDefined();
  expect(screen.getByText(/in_progress →/)).toBeDefined();
  expect(screen.getByText(/review →/)).toBeDefined();
  expect(screen.getByText('completed')).toBeDefined();
});
