# Product Requirements Document (PRD)

## 1. Introduction
PetOS is a web-based, multi-agent software engineering OS. It allows users to orchestrate a team of specialized AI agents to complete software development tasks, visualizing their progress in a real-time pixel-art office.

## 2. Core Personas
1. **The User (Human Developer):** Manages projects, assigns tasks, reviews code diffs, and approves Pull Requests.
2. **Captain (AI Agent):** The lead orchestrator. Breaks down user requests into actionable steps and assigns them to other agents.
3. **ThemeFox (AI Agent):** The UI/UX specialist. Focuses on frontend development, styling (CSS), and component design.
4. **BugDog (AI Agent):** The QA and debugging specialist. Runs tests, reads stack traces, and proposes fixes.

## 3. Functional Requirements
### 3.1 Workspace & Projects
- Users can create accounts and log in securely.
- Users can create Projects and link them to existing GitHub repositories.
- Users can define Tasks (prompts/issues) within a Project.

### 3.2 Agent Orchestration (Backend)
- The system must use LangGraph to manage agent workflows and state transitions.
- Agents must have access to a shared project memory to maintain context.
- The system must execute code and terminal commands in a secure, sandboxed environment.

### 3.3 Visual Interface (Frontend)
- A 2D pixel-art office must render the agents.
- Agent avatars must display real-time status indicators (e.g., "Idle," "Thinking," "Coding," "Testing").
- The UI must include a feed of agent activities and a code-diff viewer for user approval.

### 3.4 GitHub Integration
- The system must authenticate via GitHub OAuth.
- Agents must be able to pull issues, branch off `main`, commit changes, and create Pull Requests automatically.

## 4. System Constraints
- Must use a Modular Monolith architecture initially.
- The frontend must be strictly React/Next.js and the backend FastAPI/Python.
- The UI is a visualizer; it must not hold workflow business logic. All workflow state lives in the backend (PostgreSQL/LangGraph).
