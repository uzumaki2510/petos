# Tech Stack

PetOS relies on a modern, typed, and scalable stack separated cleanly into a frontend and backend monolith.

## Frontend
- **Framework:** Next.js (React)
- **Language:** TypeScript
- **Styling:** Vanilla CSS (or preferred CSS-in-JS solution pending further ADR, but prioritizing modern CSS standards).
- **Visualization:** HTML5 Canvas or a 2D rendering library (e.g., Phaser.js or simple React components) to render the pixel-art office.

## Backend
- **Framework:** FastAPI (Python)
- **Language:** Python 3.10+
- **Agent Orchestration:** LangGraph (LangChain ecosystem)
- **Database (Source of Truth):** PostgreSQL
- **Caching & Ephemeral State:** Redis

## Infrastructure & Execution
- **Version Control & Identity:** GitHub (OAuth & API)
- **Execution Sandbox:** Docker / isolated containers (to safely run arbitrary agent code)
- **Containerization:** Docker for deploying the monolith.

## Rationale
- **Next.js & TypeScript:** Excellent for building interactive, SEO-friendly, and type-safe frontends.
- **FastAPI & Python:** Python is the undisputed leader in AI/LLM tooling (LangChain/LangGraph). FastAPI provides high performance and automatic OpenAPI documentation.
- **PostgreSQL:** Reliable relational data modeling for users, projects, and task history.
- **LangGraph:** Crucial for managing stateful, multi-agent workflows with loops (e.g., write code -> test -> if fail -> write code).
