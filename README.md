Multi-agents RAG
=================

Project overview
----------------
- Summary: A full-stack example that demonstrates a Retrieval-Augmented Generation (RAG) system implemented as multiple collaborating Python agents in the `backend` and a React UI in the `frontend`.
- Purpose: Orchestrate agents that retrieve knowledge from a local Chroma vector store and generate or post process responses via LLM(s), exposed through a web chat UI.

Repository structure
--------------------
- `backend/`: Python agents and server entrypoint. Key files: `backend/main.py`, `backend/rag_agent.py`, `backend/supervisor_agent.py`, `backend/toolcalling_agent.py`, and `.env` for secrets.
- `backend/datastore/`: Chroma persistent DB files (e.g., `chroma.sqlite3`).
- `frontend/`: React app. Key files: `frontend/src/App.js`, `frontend/src/Chat.jsx`, `frontend/public/index.html`.
- Top-level: `requirements.txt` (Python deps) and `frontend/package.json` (JS deps).

Prerequisites
-------------
- Python 3.8+ .
- Node.js 16+ and `npm` (for the frontend).
- Provider API keys (LLM, embeddings, etc.) — add them to `backend/.env`.

Quickstart (Windows PowerShell)
-------------------------------
Backend:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# populate backend/.env with required keys
python backend/main.py
```

Frontend:
```powershell
cd frontend
npm install
npm run start
```

Open the frontend (usually at `http://localhost:3000`) and ensure the backend is running. Check `backend/main.py` for host/port details.

Configuration
-------------
- `backend/.env`: Add required environment variables such as `OPENAI_API_KEY` (or other provider keys) and any vector-store settings.
- Datastore: `backend/datastore/chroma.sqlite3` contains persistent vectors — back this up before major changes.

Development notes
-----------------
- Agents: Each agent file in `backend/` represents a distinct role. Inspect `rag_agent.py`, `supervisor_agent.py`, and `toolcalling_agent.py` for interfaces and expected inputs/outputs.
- Frontend: The chat UI is implemented in `frontend/src/Chat.jsx`, with app wiring in `frontend/src/App.js`.
- Tests: There are no automated tests included; consider adding unit and integration tests for agents and frontend components.

Troubleshooting
---------------
- CORS / connectivity: If the frontend cannot reach the backend, confirm the backend is running and adjust CORS or proxy settings.
- Missing API keys: Agents will fail without keys — add them to `backend/.env` and restart the backend.

Next steps / contributions
-------------------------
- Document exact environment variable names and expected formats in `backend/.env`.
- Add tests, CI, and example conversation scripts for reproducible demos.
- Improve error handling and add health-check endpoints in the backend.

License
-------
Add a license file if you plan to publish or share this project.

