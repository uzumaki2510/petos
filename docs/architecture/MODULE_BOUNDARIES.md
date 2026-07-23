# Module Boundaries

PetOS follows a strict **Modular Monolith** architecture on the backend. Code must be grouped by domain, not by technical concern.

## Core Modules

### 1. `auth`
- Handles user registration, sessions, and GitHub OAuth integration.
- Does not depend on any other module.

### 2. `workspace`
- Manages Projects, GitHub repository links, and high-level Task definitions.
- Depends on `auth` for user ownership.

### 3. `agents` (The LangGraph Core)
- Contains the LLM interaction logic, prompts, and the LangGraph state machine.
- Defines `Captain`, `ThemeFox`, and `BugDog`.
- Depends on `workspace` to read task inputs and `execution` to perform actions.

### 4. `execution`
- The secure sandbox layer. Manages spinning up containers, running terminal commands, and reading/writing files safely.
- Abstracted behind a strict interface so the `agents` module doesn't know *how* commands run, only that they do.

### 5. `github_integration`
- Handles GitHub API interactions: cloning, committing, branching, and PR creation.

## Rules of Dependency
- Modules should interact via explicit Python function calls or internal event buses (if implemented), rather than HTTP network calls.
- Circular dependencies between modules are strictly forbidden. Use dependency injection or interface abstraction to break them if they occur.
