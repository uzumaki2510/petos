---
trigger: always_on
---

# PetOS Engineering Rules

## Project behaviour

- PetOS must be developed one phase at a time.
- Always create an implementation plan before changing files.
- Never generate the complete application in one task.
- Wait for approval before beginning a new development phase.
- Explain which files will be created or modified.
- Keep every phase usable and testable.

## Architecture

- Start with a modular monolith.
- Do not introduce microservices without a documented reason.
- Frontend: Next.js, React and TypeScript.
- Backend: FastAPI and Python.
- Database: PostgreSQL.
- Redis is only for caching, temporary state and event streams.
- Agent reasoning uses LangGraph.
- Durable workflows may use Temporal later.
- The pixel office must display backend state but must not control workflow state.

## Code quality

- Use strong typing.
- Keep modules small and focused.
- Avoid duplicate code.
- Validate all external input.
- Add error handling.
- Add tests for important functionality.
- Run formatting, linting and tests after changes.
- Do not ignore failing tests.
- Do not add unnecessary dependencies.

## Security

- Never commit secrets or API keys.
- Never include secrets in generated prompts or logs.
- Never use unrestricted shell execution.
- Ask before installing dependencies.
- Ask before deleting files.
- Ask before changing database migrations.
- Ask before pushing code.
- Never merge or deploy without explicit approval.

## Development process

For every task:

1. Read the relevant documentation.
2. Inspect the existing repository.
3. Produce an implementation plan.
4. List the files that will change.
5. Wait for approval.
6. Implement the smallest working solution.
7. Run tests and validation.
8. Show the final diff.
9. Produce a walkthrough.
10. Update documentation when architecture changes.

## Restrictions

- Do not build future phases early.
- Do not create placeholder systems that appear functional but are not.
- Do not simulate successful tests.
- Do not report completion until validation succeeds.
- Do not rewrite unrelated files.