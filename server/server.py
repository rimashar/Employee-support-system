from fastmcp import FastMCP
from tools import *
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from email_send.send import send_email

mcp = FastMCP('Employee Support MCP')

app = FastAPI()

class DatabaseRequest(BaseModel):
    empid: str
    operation: str

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

class ticketRequest(BaseModel):
    title: str
    employeeId: str
    description: str
    category: str
    priority: str
    department: str

class employeeTickets(BaseModel):
    employeeId: str



@mcp.tool()
def database_tool(empid: str, operation: str):
    if(operation == "GET_PROFILE"):
        return get_profile(empid)
    if(operation == "GET_MANAGER"):
        return get_manager(empid)
    if(operation == "GET_SKIP"):
        return get_skip_manager(empid)
    if(operation == "GET_LEAVE_BALANCE"):
        return get_leave_balance(empid)
    if(operation == "GET_DEPT"):
        return get_department(empid)

@mcp.tool()
def email(to_email:str, subject:str, body:str):
    send_email(to_email, subject, body)
    return f"Email sent to {to_email}"

@mcp.tool()
def ticket(title:str, employeeId: str, description:str, category:str, priority:str, department:str):
    return ticket_augment(title, employeeId, description, category, priority, department)

@mcp.tool()
def get_emp_ticket(empid: str):
    return get_tickets_by_employee(empid)


"""REST API POST END POINTS FOR MCP TOOLS"""

@app.post("/database_tool")
def database_tool_endpoint(request: DatabaseRequest):
    return database_tool(request.empid, request.operation)

@app.post("/email_tool")
def send_email_endpoint(req: EmailRequest):
    return email(req.to_email, req.subject, req.body)

@app.post("/ticket_tool")
def create_ticket(part: ticketRequest):
    return ticket(part.title, part.employeeId, part.description, part.category, part.priority, part.department)

@app.post("/employee_tickets")
def get_ticket(req: employeeTickets):
    return get_emp_ticket(req.employeeId)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )