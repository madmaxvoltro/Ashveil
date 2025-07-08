using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Drawing;
using System.Drawing.Imaging;

class Program
{
    private static HttpClient client = new HttpClient();
    private static string serverUrl = "http://127.0.0.1:7777/upload"; // Flask server URL

    static void Main(string[] args)
    {
        Console.WriteLine("Starting screenshot capture...");

        // Loop to capture screenshot every second
        while (true)
        {
            // Capture screenshot
            var screenshot = CaptureScreenshot();

            // Send screenshot to server
            SendScreenshotToServer(screenshot);

            // Wait 1 second before taking the next screenshot
            Thread.Sleep(1000);
        }
    }

    static byte[] CaptureScreenshot()
    {
        // Create a bitmap of the screen
        Rectangle bounds = System.Windows.Forms.Screen.PrimaryScreen.Bounds;
        Bitmap bitmap = new Bitmap(bounds.Width, bounds.Height);
        using (Graphics g = Graphics.FromImage(bitmap))
        {
            g.CopyFromScreen(0, 0, 0, 0, bounds.Size);
        }

        // Convert to byte array
        using (MemoryStream ms = new MemoryStream())
        {
            bitmap.Save(ms, ImageFormat.Jpeg);
            return ms.ToArray();
        }
    }

    static void SendScreenshotToServer(byte[] screenshot)
    {
        try
        {
            var content = new ByteArrayContent(screenshot);
            content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg");

            // Send POST request to the Flask server
            var response = client.PostAsync(serverUrl, content).Result;

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("Screenshot sent successfully.");
            }
            else
            {
                Console.WriteLine("Failed to send screenshot. Status code: " + response.StatusCode);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error sending screenshot: " + ex.Message);
        }
    }
}
