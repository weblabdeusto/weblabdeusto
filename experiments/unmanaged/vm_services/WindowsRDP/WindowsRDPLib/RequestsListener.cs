using System;
using System.Net;
using System.Diagnostics;

namespace WebLab.VM.WindowsRDP
{

    /// <summary>
    /// Listens for HTTP requests according to the ListenerPrefix
    /// and handles them.
    /// </summary>
    public class RequestsListener
    {
        public string ListenerPrefix { get; set; }

        public RequestsListener()
        {
            ListenerPrefix = "http://*:6789/";
        }

        public RequestsListener(string prefix)
        {
            ListenerPrefix = prefix;
        }

        public void Run()
        {
            Trace.WriteLine("Starting Windows RDP VM Service");

            HttpListener listener = new HttpListener();
            listener.Prefixes.Add(ListenerPrefix);
            listener.Start();

            while (true)
            {
                try
                {
                    HttpListenerContext ctx = listener.GetContext();
                    RequestHandler handler = new RequestHandler(ctx);
                    handler.ProcessRequest();
                }
                catch (Exception ex)
                {
                    Trace.WriteLine("Exception caught: ");
                    Trace.WriteLine(ex.Message);
                }
            }
        }
    }
}
