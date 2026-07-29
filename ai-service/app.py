from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from agents import workflow
from fastapi.middleware.cors import CORSMiddleware
import requests

'''from agents import process_request'''

app = FastAPI(
    title="Employee Support AI Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_SERVER_URL = "http://localhost:8001"

class ChatRequest(BaseModel):
    employeeId: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        state = {
            "employee_id": request.employeeId,
            "user_query": request.message,
            "messages": [],
            "intent": "",
            "data": "",
            "response": "",
            "route": "",
            "ticket_data": None
        }

        result = await workflow.ainvoke(state)
        response_text = result.get("response", "Unable to process request")
        data = result.get("ticket_data", "")
        print("response from response agent:", response_text)
        print("data from response agent:", data)
        return {
            "reply": response_text,
            "data":data
        }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {
            "reply": f"An error occurred: {str(e)}"
        }

@app.get("/tickets/{employee_id}")
async def get_tickets(employee_id: str):

    response = requests.post(
        f"{MCP_SERVER_URL}/employee_tickets",
        json={"employeeId": employee_id}
    )

    return response.json()