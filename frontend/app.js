

function getEmployeeId() {

    const employeeId =
        document.getElementById("employeeId")
        .value
        .trim();

    if (!employeeId) {

        alert(
            "Please enter Employee ID."
        );

        return null;
    }

    return employeeId;
}    


function sendQuickAction(question) {

    document.getElementById(
        "messageInput"
    ).value = question;

    sendMessage();
}

function addUserMessage(text) {

    const container =
        document.getElementById("chatMessages");

    container.innerHTML += `
        <div class="user-message">
            ${text}
        </div>
    `;

    container.scrollTop =
        container.scrollHeight;
}


function addTicket(ticket) {
    console.log("input to ticket adder:", ticket);
    const container =
        document.getElementById(
            "ticketsContainer"
        );

    container.innerHTML += `
        <div class="ticket-card">

            <div class="ticket-id">
                ${ticket.ticket_id}
            </div>

            <div>
                ${ticket.title}
            </div>

            <div>
                Status:
                ${ticket.status}
            </div>

            <div>
                Priority:
                ${ticket.priority}
            </div>

        </div>
    `;
}


function addAssistantMessage(text) {

    const container =
        document.getElementById("chatMessages");

    container.innerHTML += `
        <div class="assistant-message">
            ${text}
        </div>
    `;

    container.scrollTop =
        container.scrollHeight;
}


function addWaitingMessage() {
    const container = document.getElementById("chatMessages");

    const waitingDiv = document.createElement("div");
    waitingDiv.className = "assistant-message loading-message";
    waitingDiv.id = "waitingMessage";
    waitingDiv.textContent = "⏳ Waiting...";

    container.appendChild(waitingDiv);
    container.scrollTop = container.scrollHeight;
}


function removeWaitingMessage() {
    const waitingDiv = document.getElementById("waitingMessage");

    if (waitingDiv) {
        waitingDiv.remove();
    }
}


async function sendMessage() {

    const employeeId = getEmployeeId();

    if (!employeeId) {
        return;
    }

    const input =
        document.getElementById(
            "messageInput"
        );

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    addUserMessage(message);

    input.value = "";
    addWaitingMessage();

    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        employeeId,
                        message
                    })
                });

        const data = await response.json();

        console.log("api response:", data.reply);

        removeWaitingMessage();
        addAssistantMessage(data.reply);
        

        if(data.data && data.data.ticket_id){
            try{
                console.log("Adding ticket card:", data.data);
                addTicket(
                    data.data
                );
            }
            catch(e){
                console.log("Ticket card error:", e);
            }

        }

    }
        catch(error) {
        console.error(error);

        removeWaitingMessage();

        addAssistantMessage(
            "Unable to reach Employee Support Service."
        );
    }
}


async function getTickets(){
    const employeeId = document.getElementById("employeeId").value.trim();
    const response =  await fetch(
        `http://localhost:8000/tickets/${employeeId}`, {
        method: "GET",
       });
    if(!response.ok){
        throw new Error(`HTTP Error:
            ${response.status}`);
    }

    const tickets = await response.json();
    console.log("Employee tickets:", tickets);
    return tickets
}


document
    .getElementById("messageInput")
    .addEventListener(
        "keypress",
        function(event) {

            if (event.key === "Enter") {
                sendMessage();
            }

        }
    );


document
        .getElementById("employeeId")
        .addEventListener("change", async function(){
            try{
                container = document.getElementById("ticketsContainer");
                container.innerHTML = "";
                const user_tickets = await getTickets();
                user_tickets.forEach(ticket => {
                    addTicket(ticket);
                });
            }
            catch(e){
                console.error("Failed to load tickets:", e)
            }
        });





