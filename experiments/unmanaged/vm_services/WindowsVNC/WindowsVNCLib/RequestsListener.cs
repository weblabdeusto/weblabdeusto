using System;
using System.Net;
using System.Diagnostics;

namespace WebLab.VM.WindowsVNC
{

    /// <summary>
    /// Listens for HTTP requests according to the ListenerPrefix
    /// and handles them.
    /// </summary>
    public class RequestsListener
    {
        public string ListenerPrefix { get; set; }
        public string UltraVNCPath { get; set; }

        private UltraVNCManager mUVNCManager;

        public RequestsListener(string prefix, string ultravnc_path)
        {
            ListenerPrefix = prefix;
            UltraVNCPath = ultravnc_path;
            mUVNCManager = new UltraVNCManager(UltraVNCPath);
        }

        public void Run()
        {
            try
            {
                Trace.WriteLine("Starting Windows VNC VM Service");

                HttpListener listener = new HttpListener();
                listener.Prefixes.Add(ListenerPrefix);
                listener.Start();

                while (true)
                {
                    try
                    {
                        HttpListenerContext ctx = listener.GetContext();
                        RequestHandler handler = new RequestHandler(ctx, mUVNCManager);
                        handler.ProcessRequest();
                    }
                    catch (Exception ex)
                    {
                        Trace.WriteLine("Exception caught: " + ex.Message + "\n" + ex.StackTrace);
                    }
                }
            }
            catch (Exception e)
            {
                Trace.WriteLine("Exception caught @ run: " + e.Message);
            }
        }
    }
}
