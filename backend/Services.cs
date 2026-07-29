using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Options;

namespace EmployeeSupport;

public class AgentService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly AiServiceOptions _options;

    public AgentService(
        IHttpClientFactory httpClientFactory,
        IOptions<AiServiceOptions> options)
    {
        _httpClientFactory = httpClientFactory;
        _options = options.Value;
    }
    public async Task<ChatResponse> ChatAsync(
        string employeeId,
        string message)
    {
        var aiResponse =
            await SendToAiService(
                employeeId,
                message
            );

      
        return new ChatResponse
        {
            Reply = aiResponse.Reply,
            Data = aiResponse.Data,
            AgentUsed = "Python Agents"
        };
    }

    private async Task<AiResponse> SendToAiService(
        string employeeId,
        string message)
    {
        var client =
            _httpClientFactory.CreateClient();

        var response =
            await client.PostAsJsonAsync(
                $"{_options.BaseUrl}/chat",
                new { employeeId, message }
            );

        response.EnsureSuccessStatusCode();

        return await response.Content
            .ReadFromJsonAsync<AiResponse>()
            ?? new AiResponse();
    }
}

