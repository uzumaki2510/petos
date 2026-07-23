# Initial Risk Register

| Risk | Likelihood | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Untrusted Code Execution** <br> Agents might write destructive code (`rm -rf /`) or run malicious `npm` packages. | High | Critical | **Strict Sandboxing:** All agent terminal executions must run inside ephemeral, unprivileged Docker containers with no mount access to the host machine. |
| **Secret Exfiltration** <br> Agents might accidentally log or commit GitHub API keys or database passwords. | Medium | Critical | **Environment Isolation:** Do not provide production secrets to the execution sandbox. Use granular, short-lived GitHub tokens scoped strictly to the target repository. Implement secret-scanning in agent outputs. |
| **Infinite Agent Loops** <br> LangGraph nodes might get stuck in an endless cycle of writing broken code, failing tests, and rewriting broken code. | High | Medium | **Circuit Breakers:** Implement strict hard-limits on graph execution steps (e.g., max 5 iterations). Fail the task gracefully and ask the human user for intervention. |
| **Prompt Injection** <br> Users might submit tasks containing malicious prompts to manipulate agent behavior. | Medium | Medium | **Input Validation & LLM Guardrails:** Sanitize task inputs. Rely on system prompts to dictate agent constraints, though true protection against prompt injection is an ongoing industry challenge. |
