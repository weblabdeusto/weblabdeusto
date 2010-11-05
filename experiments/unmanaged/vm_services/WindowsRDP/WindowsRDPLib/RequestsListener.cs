using System;
using System.Net;
using System.Diagnostics;

namespace WebLab.VM.WindowsRDP
{
    public class RequestsListener
    {
        public void Run()
        {
            Trace.WriteLine("Starting Windows RDP VM Service");

            HttpListener listener = new HttpListener();
            listener.Prefixes.Add("http://*:6789/");
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
