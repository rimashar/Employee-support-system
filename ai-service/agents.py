import requests
import os
import json
import requests

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, Optional

from prompts import (
    EMPLOYEE_INTENT,
    ROUTING_PROMPT,
    RESPONSE_PROMPT,
    NOTIFY_AGENT_PROMPT,
    TICKET_PROMPT,
)

GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"

os.environ["GITHUB_MODELS_API_KEY"]=""

API_KEY = os.getenv("GITHUB_MODELS_API_KEY")
MODEL = "gpt-4o"


MCP_SERVER_URL = "http://localhost:8001"

class AgentState(TypedDict):
    employee_id: str
    user_query:str
    messages: list[str]
    intent: str
    data: str
    response: str
    route: Optional[str]
    ticket_data: Optional[dict]

def get_intent_from_keywords(msg: str) -> str:
    """Fallback intent detection using keyword matching"""
    msg_lower = msg.lower()
    
    if "leave" in msg_lower or "vacation" in msg_lower:
        return "GET_LEAVE_BALANCE"
    elif "skip" in msg_lower or "skip manager" in msg_lower:
        return "GET_SKIP"
    elif "manager" in msg_lower:
        return "GET_MANAGER"
    elif "department" in msg_lower or "dept" in msg_lower:
        return "GET_DEPT"
    elif "profile" in msg_lower:
        return "GET_PROFILE"
    else:
        return "GET_PROFILE"

async def ask_github_models(prompt: str):
    """Call GitHub Models API with fallback for intent detection"""
    
    # Skip API call for simple intent detection prompts - use keyword matching
    if "identify the intent" in prompt.lower():
        # Extract message from prompt
        if "Message:" in prompt:
            msg = prompt.split("Message:")[-1].strip()
            return get_intent_from_keywords(msg)
        return "GET_PROFILE"
    
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2
        }

        headers = {
            "Authorization":
                f"Bearer {API_KEY}",
            "Content-Type":
                "application/json"
        }

        response = requests.post(
            GITHUB_MODELS_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["choices"][0]
                ["message"]["content"]
        )
    except requests.exceptions.RequestException as e:
        # Fallback response when API fails
        print(f"Warning: GitHub Models API failed: {e}")
        
        if "response" in prompt.lower() or "data" in prompt.lower():
            return "I have retrieved the requested information from our database."
        else:
            return "I'm unable to process this request at the moment."


def entry_node(state: AgentState) -> AgentState:
    """Entry node: log user's query in the conversation"""
    messages = state.get("messages", []).copy()
    messages.append("User:" + state.get("user_query", ""))
    return {**state, "messages": messages}

async def router_agent(state: AgentState) -> AgentState:
    """llm based router that decides between Employee and ticket"""
    messages = state.get("messages", []).copy()
    q = state.get("user_query", "")

    raw  = await ask_github_models(ROUTING_PROMPT.format(question=q))
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()
    print(raw)
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error parsing router response: {e}")
        print(f"Raw response: {raw}")
        data = {"route": "employee", "reason": "Default fallback route"}
    
    route = data.get("route", "employee")
    reason = data.get("reason", "No reason provided.")

    messages.append(f"Router: decided route = {route}, reason : {reason}")
    return {**state, "messages": messages, "route": route}


async def employee_agent(state : AgentState) -> AgentState:
    employee_id = state["employee_id"]
    msg = state["user_query"]

    try:
        intent = await ask_github_models(EMPLOYEE_INTENT.format(msg=msg))
        intent = intent.strip().upper()
    except Exception as e:
        print(f"Error in intent detection: {e}")
        intent = get_intent_from_keywords(msg)

    if intent == "GET_LEAVE_BALANCE":
        operation = "GET_LEAVE_BALANCE"
    elif intent == "GET_SKIP":
        operation = "GET_SKIP"
    elif intent == "GET_MANAGER":
        operation = "GET_MANAGER"
    elif intent == "GET_DEPT":
        operation = "GET_DEPT"
    elif intent == "GET_PROFILE":
        operation = "GET_PROFILE"
    else:
        operation = "GET_PROFILE"

    payload = {
    "empid": employee_id,
    "operation": operation
    }

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/database_tool",
            json=payload,
            timeout=5
        )
        state["data"] = response.json()
        state["data"]["user_intent"] = intent
        print("data from employee agent", state["data"])
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP server: {e}")
        state["data"] = json.dumps({"error": "Unable to retrieve data"})

    return state


async def notify_agent(state: AgentState) -> AgentState:
    """sends emails to respective department employees suited for the user issue"""
    employee_id = state["employee_id"]
    msg = state["user_query"]
    raw = await ask_github_models(NOTIFY_AGENT_PROMPT.format(employee_id=employee_id, issue=msg))
    
    # Handle JSON parsing with cleanup
    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

    print(f"Raw notify agent response: {raw}")
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error parsing ticket agent response: {e}")
        print(f"Raw response: {raw}")
        data = {"recipient_email": "support@company.com", "subject": "Support Ticket", "body": "Your issue has been logged."}
    to_email = data.get("recipient_email", "")
    subject = data.get("subject", "No Subject")
    body = data.get("body", "No Body")

    payload = {
        "to_email": to_email,
        "subject": subject,
        "body": body
    }

    try: 
        response = requests.post(
            f"{MCP_SERVER_URL}/email_tool",
            json=payload,
            timeout=5
        )
        state["data"] = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP server: {e}")
        state["data"] = json.dumps({"error": "Unable to send email"})
    return state


async def ticket_agent(state: AgentState) -> AgentState:
    """creates and saves tickets created by user"""
    employee_id = state["employee_id"]
    issue = state["user_query"]
    try:
        raw = await ask_github_models(
            TICKET_PROMPT.format(employee_id=employee_id, issue=issue))
        
        if raw.startswith("```"):
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

        ticket_data = json.loads(raw)

    except Exception as e:
        print(f"Error in ticket_agent: {e}")
        ticket_data = {
            "title": "Default Ticket",
            "employeeId": "EMP005",
            "description": "Unable to create ticket due to an error.",
            "category": "IT",
            "priority": "Medium",
            "department": "Support"
        }

    payload = {
        **ticket_data
    }

    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/ticket_tool",
            json=payload,
            timeout=5
        )

        state["ticket_data"] = response.json()
        print("Ticket response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP server: {e}")
        state["ticket_data"] = {"error": "Unable to create ticket"}

    return state

async def response_agent(state: AgentState) -> AgentState:
    """Generates a final response to the user based on the data retrieved"""
    messages = state.get("messages", []).copy()
    data = state.get("data", "")
    ticket_data = state.get("ticket_data")

    if ticket_data:
        prompt = RESPONSE_PROMPT.format(
            data = f"""
                Ticket information:
                {ticket_data}

                Email status:
                {data}"""
        )
    else: 
        prompt = RESPONSE_PROMPT.format(data=data)

    print("the prompt generated by response_agent:", prompt)
    try:
        raw = await ask_github_models(prompt)
    except Exception as e:
        print(f"Error in response_agent: {e}")
        raw = f"Retrieved information: {data}"
    
    messages.append(f"ResponseAgent: {raw}")
    return {
        **state,
        "messages": messages,
        "response": raw
    }


graph = StateGraph(AgentState)

graph.add_node("Entry", entry_node)
graph.add_node("Router", router_agent)
graph.add_node("Employee", employee_agent)
graph.add_node("Notify", notify_agent)
graph.add_node("Ticket", ticket_agent)
graph.add_node("ResponseAgent", response_agent)

graph.set_entry_point("Entry")
graph.add_edge("Entry", "Router")

def route_after_router(state: AgentState):
    if state.get("route", "").lower() == "employee":
        return "Employee"
    return "Ticket"

graph.add_conditional_edges(
    "Router",
    route_after_router,
    {
        "Employee": "Employee",
        "Ticket": "Ticket"
    },
)

graph.add_edge("Ticket", "Notify")
graph.add_edge("Notify", "ResponseAgent")
graph.add_edge("Employee", "ResponseAgent")
graph.add_edge("ResponseAgent", END)
workflow = graph.compile()

print(workflow.get_graph().draw_mermaid())

'''workflow = StateGraph(AgentState)

workflow.add_node(
    "RoutingAgent",
    routing_agent
)

workflow.add_node(
    "EmployeeAgent",
    employee_agent
)

workflow.add_node(
    "TicketAgent",
    ticket_agent
)

workflow.add_node(
    "RequestAgent",
    request_agent
)

workflow.add_node(
    "ApprovalAgent",
    approval_agent
)

workflow.add_node(
    "ResponseAgent",
    response_agent
)'''