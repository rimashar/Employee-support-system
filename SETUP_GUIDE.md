# Employee Support System - Setup and Run Guide




## Components

### 2. **Backend Services**

#### MCP Server (port 8001)
- **File**: `server/server.py`
- **Purpose**: Database tool interface
- **Endpoints**: `/database_tool` (POST)
- **Startup**: `cd server && uvicorn server.py --port 8001`

#### Python AI Service (port 8000)
- **Files**: `ai-service/app.py`, `ai-service/agents.py`, `ai-service/prompts.py`
- **Purpose**: Intent detection and response generation
- **Endpoints**: `/chat` (POST)
- **Startup**: `cd ai-service && uvicorn app:app --port 8000`

#### C# Backend (port 5000)
- **Files**: `backend/Program.cs`, `backend/Services.cs`, `backend/Models.cs`
- **Purpose**: Main API + static file serving
- **Endpoints**: 
  - `GET /` - Health check
  - `POST /api/chat` - Main chat endpoint
  - Static files from `../frontend/`
- **Startup**: `cd backend && dotnet run`

### 3. **Frontend**
- **Files**: `frontend/landing.html`, `frontend/app.js`, `frontend/styles.css`
- **Served**: By C# Backend on port 5000
- **Access**: `http://localhost:5000`

## Setup Instructions

### Step 1: Start MCP Server
```bash
cd server
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Step 2: Start Python AI Service
```bash
cd ai-service
pip install fastapi uvicorn langchain langchain-openai langgraph requests
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Step 3: Start C# Backend
```bash
cd backend
dotnet run
```
The backend will start on `http://localhost:5000`

### Step 4: Access Frontend
Open browser and navigate to:
```
http://localhost:5000
```

## Testing the System

### Test Employee IDs
- EMP001, EMP002, EMP003, EMP004, EMP005

### Sample Queries
- "Show my profile"
- "Who is my manager?"
- "Who is my skip manager?"
- "Which department am I in?"
- "What is my leave balance?"

## Configuration

### Environment Variables
- `GITHUB_MODELS_API_KEY` - GitHub Models API key (in agents.py)

### Ports
- Frontend: 5000 (served by C# backend)
- C# Backend: 5000
- Python AI Service: 8000
- MCP Server: 8001

### AppSettings.json
```json
{
  "AiService": {
    "BaseUrl": "http://localhost:8000"
  },
  "Mcp": {
    "BaseUrl": "http://localhost:8001"
  }
}
```


