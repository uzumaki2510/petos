import { test, expect } from '@playwright/test';
import { randomUUID } from 'crypto';

test.describe('Phase 4 Critical Task Workflow', () => {
  test('Complete Task Lifecycle: Create project key, create task, transition status, comment, activity, logout', async ({ page }) => {
    const uniqueId = randomUUID().slice(0, 8);
    const email = `taskuser-${uniqueId}@test.example.com`;
    const password = 'SuperSecretPassword123!';
    const displayName = `Task Owner ${uniqueId}`;
    const projectName = `Task App ${uniqueId}`;

    // 1. Register unique user
    await page.goto('/register');
    await page.fill('#display_name', displayName);
    await page.fill('#email', email);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*\/app$/, { timeout: 15000 });
    await expect(page).toHaveURL(/.*\/app$/);

    // 2. Create project with key
    await page.goto('/app/projects/new');
    await page.fill('#name', projectName);
    await page.fill('#key', 'PET');
    await page.fill('#description', 'Task management testing project');
    await page.click('#create-project-submit');
    await page.waitForURL(/.*\/app\/projects$/, { timeout: 15000 });
    await expect(page.locator(`text=${projectName}`)).toBeVisible();

    // Navigate into project task list page
    await page.click('text=View Project');
    await page.waitForURL(/\/app\/projects\/[0-9a-f-]+$/, { timeout: 15000 });

    // 3. Create task
    await page.goto(`${page.url()}/tasks/new`);
    await page.waitForURL(/\/app\/projects\/[0-9a-f-]+\/tasks\/new$/, { timeout: 15000 });
    await page.fill('#title', 'Task One');
    await page.fill('#description', 'Detailed description for task one');
    await page.fill('#acceptance_criteria', 'Given task exists, when transitioned, then history logged.');
    await page.click('#create-task-submit');
    await page.waitForURL(
      new RegExp(`/app/projects/.+/tasks$`)
    );
    await expect(page.locator('h1:has-text("Project Tasks")')).toBeVisible();

    console.log("CURRENT URL:", page.url());
    console.log("BODY TEXT:", await page.locator("body").innerText());

    // 4. Verify display identifier PET-1 on task list
    await expect(page.locator('text=PET-1')).toBeVisible();
    await expect(page.locator('text=Task One')).toBeVisible();

    // 5. Open Task Detail page
    await page.click('text=Task One');
    await page.waitForURL(/\/app\/projects\/[0-9a-f-]+\/tasks\/[0-9a-f-]+$/, { timeout: 15000 });
    await expect(page.getByText('Given task exists, when transitioned, then history logged.')).toBeVisible();

    // Helper for deterministic task transitions
    const transitionTask = async (buttonName: string, expectedStatus: string) => {
      const transitionPromise = page.waitForResponse(
        (response) =>
          response.url().includes('/transition') &&
          response.request().method() === 'POST'
      );
      await page.getByRole('button', { name: buttonName }).click();
      const transitionResponse = await transitionPromise;
      expect(transitionResponse.ok()).toBeTruthy();
      const transitionBody = await transitionResponse.json();
      expect(transitionBody.status).toBe(expectedStatus.toLowerCase());
      await expect(page.getByTestId('task-status')).toHaveText(expectedStatus);
    };

    // 6. Transition to ready
    await transitionTask('Move to Ready', 'READY');

    // 7. Transition to in_progress
    await transitionTask('Start Task (In Progress)', 'IN_PROGRESS');

    // 8. Add comment
    await page.fill('textarea[placeholder="Add a comment..."]', 'Working on implementation now.');
    await page.click('button:has-text("Post Comment")');
    await expect(page.getByText('Working on implementation now.')).toBeVisible();

    // 9. Transition to review
    await transitionTask('Submit for Review', 'REVIEW');

    // 10. Complete task
    await transitionTask('Complete Task', 'COMPLETED');

    // 11. Confirm activity history
    const activityTimeline = page.getByTestId('activity-timeline');
    await expect(activityTimeline).toBeVisible();

    const createdEvents = activityTimeline.locator('[data-event-type="task.created"]');
    await expect(createdEvents).toHaveCount(1);

    const transitionEvents = activityTimeline.locator('[data-event-type="task.transitioned"]');
    await expect(transitionEvents).toHaveCount(4);

    await expect(activityTimeline.getByText('backlog → ready')).toBeVisible();
    await expect(activityTimeline.getByText('ready → in_progress')).toBeVisible();
    await expect(activityTimeline.getByText('in_progress → review')).toBeVisible();
    await expect(activityTimeline.getByText('review → completed')).toBeVisible();

    // 12. Log out
    await page.goto('/app/settings');
    await page.click('#logout-button');
    await page.waitForURL(/.*\/login/, { timeout: 15000 });

    // 13. Confirm protected access redirects to login
    await page.goto('/app');
    await page.waitForURL(/.*\/login/);
    await expect(page).toHaveURL(/.*\/login/);
  });
});
