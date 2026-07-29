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

## Data Flow

1. **User** enters Employee ID and message in frontend
2. **Frontend** sends POST request to `http://localhost:5000/api/chat`
3. **C# Backend** routes request based on intent:
   - Employee queries → MCP Server via McpClientService
   - Other queries → Python AI Service
4. **Python AI Service** (if used):
   - Detects intent using GitHub Models LLM
   - Sends request to MCP Server for data
   - Formats response with LLM
5. **Response** flows back through all layers to frontend
6. **Frontend** displays response in chat interface

## Fixes Applied

✅ HTML/CSS/JavaScript linking fixed
✅ API response format synchronized across services
✅ C# backend JSON response parsing corrected
✅ Static file serving enabled in C# backend
✅ CORS configured for service-to-service communication
✅ Database initialization script provided
✅ F-string formatting issues in Python agents fixed
✅ Port configuration corrected

## Common Issues

### "Unable to reach Employee Support Service"
- Check if C# backend is running on port 5000
- Check browser console for actual error message
- Verify network connectivity

### "MCP Error" in responses
- Ensure MCP server is running on port 8001
- Verify database file exists and has correct schema
- Check employee ID is valid (EMP001-EMP005)

### API calls failing
- Ensure all three services are running
- Check port configurations match
- Verify GitHub API key is valid
