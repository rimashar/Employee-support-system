using EmployeeSupport;
using Microsoft.Extensions.FileProviders;

var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<AiServiceOptions>(
    builder.Configuration.GetSection("AiService"));

builder.Services.AddHttpClient();

builder.Services.AddSingleton<AgentService>();


builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

var app = builder.Build();

app.UseCors("AllowAll");

// Serve frontend files
var frontendPath = Path.GetFullPath(
    Path.Combine(app.Environment.ContentRootPath, "..", "frontend"));

if (Directory.Exists(frontendPath))
{
    var provider = new PhysicalFileProvider(frontendPath);
    app.UseDefaultFiles(new DefaultFilesOptions
    {
        FileProvider = provider,
        DefaultFileNames = new List<string> { "landing.html" }
    });
    app.UseStaticFiles(new StaticFileOptions
    {
        FileProvider = provider
    });
}

app.MapGet("/", () =>
{
    var landingPage = Path.Combine(frontendPath, "landing.html");

    if (File.Exists(landingPage))
    {
        return Results.File(landingPage, "text/html");
    }

    return Results.Ok(new
    {
        Application = "Employee Support System",
        Status = "Running"
    });
});

app.MapPost("/api/chat",
async (
    ChatRequest request,
    AgentService agent
) =>
{
    if (string.IsNullOrWhiteSpace(request.EmployeeId))
        return Results.BadRequest("EmployeeId is required");

    if (string.IsNullOrWhiteSpace(request.Message))
        return Results.BadRequest("Message is required");

    var response = await agent.ChatAsync(
        request.EmployeeId,
        request.Message);

    return Results.Ok(response);
});

app.Run();