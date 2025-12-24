Multi-agents RAG
=================

Project overview
----------------
- Summary: A full-stack example that demonstrates a Retrieval-Augmented Generation (RAG) system implemented as multiple collaborating Python agents in the `backend` and a React UI in the `frontend`.
- Purpose: Orchestrate agents that retrieve knowledge from a local Chroma vector store and generate or post process responses via LLM(s), exposed through a web chat UI.

Project Architecture
--------------------

<img width="1024" height="1536" alt="Architechture" src="https://github.com/user-attachments/assets/97811147-3a70-4371-b95c-09febc09782e" />


Repository structure
--------------------
- `backend/`: Python agents and server entrypoint. Key files: `backend/main.py`, `backend/rag_agent.py`, `backend/supervisor_agent.py`, `backend/toolcalling_agent.py`, and `.env` for secrets.
- `backend/datastore/`: Chroma persistent DB files (e.g., `chroma.sqlite3`).
- `frontend/`: React app. Key files: `frontend/src/App.js`, `frontend/src/Chat.jsx`, `frontend/public/index.html`.
- Top-level: `requirements.txt` (Python deps) and `frontend/package.json` (JS deps).  

Prerequisites
------------
- Python 3.10+ (for local development).
- Node.js 18+ and `npm` (for the frontend local development).
- Docker and Docker Compose (for containerized setup).
- Provider API keys (LLM, embeddings, etc.) — add them to `backend/.env`.

Quickstart with Docker (Recommended)
-----------------------------------
1. **Create a `.env` file** at the project root with required environment variables:
```powershell
# .env file (in project root)
GROQ_API_KEY = "your-groq-api-key-here"
TAVILY_API_KEY = "your-tavily-api-key-here"
HUGGINGFACE_API_TOKEN = "your-huggingface-api-token-here"
```

2. **Build and run the application** using Docker Compose:
```powershell
# Build images
docker-compose build

# Start services (backend on port 9000, frontend on port 3000)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

3. **Access the application**:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:9000`

4. **Docker Compose Services**:
   - **Backend**: FastAPI server running on port 9000 (maps to 8000 inside container)
   - **Frontend**: React app running on port 3000
   - Both services share the `.env` file for environment variables

Quickstart (Local Development - Windows PowerShell)
---------------------------------------------------
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
**Environment Variables (`.env` file)**:
- Place `.env` at the project root for Docker or in `backend/` for local development
- Required variables: `OPENAI_API_KEY` (or other provider keys) and any vector-store settings
- Example:
  ```
  GROQ_API_KEY = "your-groq-api-key-here"
  TAVILY_API_KEY = "your-tavily-api-key-here"
  HUGGINGFACE_API_TOKEN = "your-huggingface-api-token-here"
  CHROMA_PERSIST_DIR=./backend/datastore
  ```

**Datastore**: 
- `backend/datastore/chroma.sqlite3` contains persistent vectors — back this up before major changes.

**Docker Configuration**:
- Backend Dockerfile: Builds a Python 3.10 slim image running FastAPI on port 9000
- Frontend Dockerfile: Builds a Node.js 18 Alpine image running the React app on port 3000
- Docker Compose: Orchestrates both services with shared environment variables and volume mounts
- Backend volumes: `./backend/app` for live code reloading
- Frontend volumes: `./frontend` for live code reloading

Development notes
-----------------
- Agents: Each agent file in `backend/` represents a distinct role. Inspect `rag_agent.py`, `supervisor_agent.py`, and `toolcalling_agent.py` for interfaces and expected inputs/outputs.
- Frontend: The chat UI is implemented in `frontend/src/Chat.jsx`, with app wiring in `frontend/src/App.js`.
- Tests: There are no automated tests included; consider adding unit and integration tests for agents and frontend components.

Troubleshooting
---------------
- CORS / connectivity: If the frontend cannot reach the backend, confirm the backend is running and adjust CORS or proxy settings.
- Missing API keys: Agents will fail without keys — add them to `backend/.env` and restart the backend.

Contributions
-------------------------
- Document exact environment variable names and expected formats in `backend/.env`.
- Add tests, CI, and example conversation scripts for reproducible demos.
- Improve error handling and add health-check endpoints in the backend.
