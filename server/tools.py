import sqlite3

def create_conn():
   conn = sqlite3.connect('EmployeeSupport.db')
   conn.row_factory = sqlite3.Row
   return conn

import sqlite3
from datetime import datetime

DB_PATH = "EmployeeSupport.db"


def ticket_augment(
    title: str,
    employeeId: str,
    description: str,
    category: str,
    priority: str,
    department: str
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Generate ticket number
    cursor.execute(
        """
        SELECT ticket_id
        FROM Tickets
        ORDER BY ROWID DESC
        LIMIT 1
        """
    )

    last_ticket = cursor.fetchone()

    if last_ticket:
        try:
            last_num = int(
                last_ticket[0].split("-")[1]
            )
        except Exception:
            last_num = 1000
    else:
        last_num = 1000

    ticket_id = f"INC-{last_num + 1}"

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    ticket_data = {
        "ticket_id": ticket_id,
        "employee_id": employeeId,
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "department": department,
        "status": "Open",
        "created_at": timestamp,
        "updated_at": timestamp
    }

    cursor.execute(
        """
        INSERT INTO Tickets (
            ticket_id,
            employee_id,
            title,
            description,
            category,
            priority,
            department,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_data["ticket_id"],
            ticket_data["employee_id"],
            ticket_data["title"],
            ticket_data["description"],
            ticket_data["category"],
            ticket_data["priority"],
            ticket_data["department"],
            ticket_data["status"],
            ticket_data["created_at"],
            ticket_data["updated_at"]
        )
    )

    conn.commit()
    conn.close()

    return ticket_data     
     

def get_tickets_by_employee(empid: str):
    conn = create_conn()
    cur  = conn.cursor()
   
    cur.execute("""
    SELECT * 
    FROM Tickets
    WHERE employee_id = ?
    ORDER BY created_at DESC
    """, (empid,))

    tickets = [
         dict(row)
         for row in cur.fetchall()
    ]

    conn.close()

    return tickets

def get_profile(empid):
    conn = create_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * 
        FROM Employees
        WHERE EmployeeId = ?
""", (empid,))
    result = cur.fetchone()
    if not result:
           return{
                  "success": False,
                  "message": "Employee not found"
           }
    return dict(result)

def get_manager(employee_id):

        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                m.EmployeeId,
                m.FirstName,
                m.LastName
            FROM Employees e
            JOIN Employees m
                ON e.ManagerId = m.EmployeeId
            WHERE e.EmployeeId = ?
        """, (employee_id,))

        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            return {
                "success": False,
                "message": "Manager information not found for employee"
            }

def get_skip_manager(employee_id):

        conn = create_conn()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.EmployeeId,
                s.FirstName,
                s.LastName
            FROM Employees e
            JOIN Employees s
                ON e.SkipManagerId = s.EmployeeId
            WHERE e.EmployeeId = ?
        """, (employee_id,))

        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            return {
                "success": False,
                "message": "Skip manager information not found for employee"
            }

def get_department(employee_id):

        conn = create_conn()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT Department
            FROM Employees
            WHERE EmployeeId = ?
        """, (employee_id,))

        row = cursor.fetchone()

        if row:
            return {
                "Department": row[0]
            }
        else:
            return {
                "success": False,
                "message": "Department information not found for employee"
            }

def get_leave_balance(employee_id):

        conn = create_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM LeaveBalances
            WHERE EmployeeId = ?
        """, (employee_id,))

        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            return {
                "success": False,
                "message": "Leave balance information not found for employee"
            }