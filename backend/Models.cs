namespace EmployeeSupport;

public class ChatRequest
{
    public string EmployeeId { get; set; } = string.Empty;

    public string Message { get; set; } = string.Empty;
}

public class ChatResponse
{
    public string Reply { get; set; } = string.Empty;

    public string AgentUsed { get; set; } = string.Empty;

    public object? Data { get; set; }
}


public class EmployeeProfile
{
    public string EmployeeId { get; set; } = string.Empty;

    public string FirstName { get; set; } = string.Empty;

    public string LastName { get; set; } = string.Empty;

    public string Department { get; set; } = string.Empty;
}

public class TicketInfo
{
    public string TicketId { get; set; } = string.Empty;

    public string Status { get; set; } = string.Empty;
}

public class RequestInfo
{
    public string RequestId { get; set; } = string.Empty;

    public string RequestType { get; set; } = string.Empty;
}

public class AiServiceOptions
{
    public string BaseUrl { get; set; } = string.Empty;
}

public class McpOptions
{
    public string BaseUrl { get; set; } = string.Empty;
}

public class AiResponse
{
    public string Reply { get; set; } = "";
    public object? Data { get; set; }
}