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

        private AccountsManager mAccountsManager;

        public RequestsListener(string prefix)
        {
            ListenerPrefix = prefix;
            mAccountsManager = new AccountsManager();
        }

        public void Run()
        {
            try
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
                        RequestHandler handler = new RequestHandler(ctx, mAccountsManager);
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
