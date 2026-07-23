# System Context (C4 Model)

## Context Diagram Description
PetOS sits between the Human Developer and GitHub, utilizing a secure execution environment to run autonomous tasks.

1. **Human Developer**: Interacts with the PetOS Next.js web interface to assign tasks, monitor the visual pixel office, and approve code changes.
2. **PetOS Web Interface (Next.js)**: Displays the gamified office, authenticates the user, and sends tasks to the backend.
3. **PetOS Backend (FastAPI)**: The core system. Manages state, handles LangGraph orchestration, interacts with PostgreSQL/Redis, and delegates tasks to the AI Agents.
4. **AI Agents (Captain, ThemeFox, BugDog)**: Python-based LangGraph nodes that utilize LLMs to reason, plan, and generate code.
5. **Secure Execution Environment**: A sandboxed local space (e.g., Docker) where Agents can safely run commands (`npm install`, `pytest`, etc.) and read/write code.
6. **GitHub**: The external system where code is ultimately stored. PetOS clones from here and pushes Pull Requests here.

## Data Flow
- **User -> Web App**: Submit task.
- **Web App -> Backend**: REST/GraphQL/WebSocket API request.
- **Backend -> Agents**: LangGraph state machine execution.
- **Agents -> Secure Execution**: Sandbox command execution and file manipulation.
- **Agents -> GitHub**: Clone repo, push branch, open PR via GitHub API.
- **Backend -> Web App**: WebSocket/SSE stream of agent status to update the pixel UI.
