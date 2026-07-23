# MVP Scope

The Minimum Viable Product (MVP) for PetOS is strictly scoped to the following features to ensure a timely Phase 15 release.

## In Scope for MVP
- **Authentication:** Basic user accounts and session management.
- **Projects & Repositories:** Ability to link a PetOS project to a single GitHub repository.
- **Task Management:** A simple queue to submit natural language tasks to the AI team.
- **Core Agents:**
  - **Captain:** Orchestration and planning.
  - **ThemeFox:** Frontend and CSS tasks.
  - **BugDog:** Testing and debugging tasks.
- **Shared Project Memory:** A basic PostgreSQL-backed context window for agents to share information during a task.
- **GitHub Integration:** Read/Write access to clone repos, commit code, and open PRs.
- **Secure Terminal Execution:** A local sandboxed environment (e.g., Docker container) for the agents to run commands and execute code safely.
- **Pixel Office UI:** Basic 2D rendering of the office and the three core pets, displaying their current status text.
- **Code-Diff Review:** A UI component for the human user to review and approve changes before a PR is made.
- **Test Results:** Displaying terminal output from BugDog's test runs to the human user.

## Out of Scope for MVP
*(See [NON_GOALS.md](NON_GOALS.md) for a comprehensive list)*
- Customizing the visual look of the pixel office or agents.
- Support for GitLab, Bitbucket, or other VCS.
- Multi-user collaboration on a single PetOS project.
- Long-running, multi-week autonomous epics without human intervention.
- Complex microservices architecture.
