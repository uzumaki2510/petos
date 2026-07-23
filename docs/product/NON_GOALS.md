# Non-Goals

To maintain focus during the MVP phases, the following items are explicitly categorized as non-goals for Phase 1-15.

## 1. Complex Microservices
- We will strictly adhere to a **Modular Monolith** architecture. We will not build distributed microservices, Kubernetes orchestration for backend services, or service meshes.

## 2. Non-Web Interfaces
- We will not build native iOS, Android, or desktop applications. PetOS is exclusively a web application accessed via a browser.

## 3. Production Deployments
- PetOS agents will write code, test it, and create PRs. They will **not** be responsible for pushing code directly to production environments, managing cloud infrastructure, or handling CI/CD pipelines (beyond GitHub Actions triggered by PRs).

## 4. Multiplayer Office
- For the MVP, a project is managed by a single human user. We will not implement real-time multiplayer features where multiple humans interact in the same pixel office simultaneously.

## 5. Custom Agent Creation
- The MVP includes exactly three agents: Captain, ThemeFox, and BugDog. Users cannot create custom agents or upload custom LLM prompts to modify the core team yet.

## 6. Support for alternate VCS
- The system will only support GitHub. GitLab, Bitbucket, and raw Git servers are out of scope.
