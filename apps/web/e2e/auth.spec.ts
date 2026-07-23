import { test, expect } from '@playwright/test';
import { randomUUID } from 'crypto';

const uniqueEmail = () => `e2e-${randomUUID().slice(0, 8)}@test.example.com`;

test.describe('Critical path', () => {
  test('registers, accesses /app, creates project, views project, logs out, confirms redirect', async ({ page }) => {
    const email = uniqueEmail();
    const password = 'TestPassword123!';
    const displayName = `E2E User ${email.slice(4, 12)}`;
    const projectName = `E2E Project ${randomUUID().slice(0, 6)}`;

    // 1. Navigate to register
    await page.goto('/register');
    await expect(page).toHaveURL(/.*\/register/);

    // 2. Fill in registration form
    await page.fill('#display_name', displayName);
    await page.fill('#email', email);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');

    // 3. Should redirect to /app after registration
    await page.waitForURL(/.*\/app$/, { timeout: 15000 });
    await expect(page).toHaveURL(/.*\/app$/);

    // 4. Verify /app page is visible
    await expect(page.locator('h1')).toBeVisible();

    // 5. Navigate to /app/projects and create a new project
    await page.click('text=Projects');
    await page.waitForURL(/.*\/app\/projects$/);
    await page.click('text=New Project');
    await page.waitForURL(/.*\/app\/projects\/new/);

    await page.fill('#name', projectName);
    await page.click('#create-project-submit');

    // 6. Should redirect back to /app/projects
    await page.waitForURL(/.*\/app\/projects$/, { timeout: 10000 });
    await expect(page.locator(`text=${projectName}`)).toBeVisible();

    // 7. Click "View Project"
    await page.click('text=View Project');
    await page.waitForURL(/.*\/app\/projects\/.+/);
    await expect(page.locator('h1')).toBeVisible();

    // 8. Go back to projects
    await page.click('text=Back');
    await page.waitForURL(/.*\/app\/projects$/);

    // 9. Logout
    await page.click('#logout-button');
    await page.waitForURL(/.*\/login/, { timeout: 10000 });

    // 10. Verify that accessing /app redirects back to /login
    await page.goto('/app');
    await page.waitForURL(/.*\/login/);
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('unauthenticated access to /app redirects to /login', async ({ page }) => {
    await page.goto('/app');
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('unauthenticated access to /app/projects redirects to /login', async ({ page }) => {
    await page.goto('/app/projects');
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('authenticated user is redirected from /login to /app', async ({ page }) => {
    const email = uniqueEmail();
    const password = 'TestPassword123!';

    // Register first
    await page.goto('/register');
    await page.fill('#display_name', 'Redirect Test User');
    await page.fill('#email', email);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*\/app$/, { timeout: 15000 });

    // Now try to navigate to login — should redirect to /app
    await page.goto('/login');
    await expect(page).toHaveURL(/.*\/app$/);
  });
});
