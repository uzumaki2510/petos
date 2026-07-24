# Task Authorization Matrix

## Roles & Permissions

- **Owner / Admin**: Full task lifecycle control, comment editing (own comments), label management, dependency management, task archiving.
- **Member**: Create tasks, update tasks, transition task status, comment, manage labels, manage dependencies. Cannot archive tasks.
- **Viewer**: Read-only access to tasks, comments, labels, dependencies, and activity logs. Cannot mutate resources.
- **Non-member**: 404 Not Found response for all project task resources (cross-tenant protection).
