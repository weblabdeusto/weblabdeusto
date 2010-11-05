using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;


namespace WebLab.VM.WindowsRDP
{

    /// <summary>
    /// Handles specific HTTP requests
    /// </summary>
    public class RequestHandler
    {
        private HttpListenerContext context;

        /// <summary>
        /// Create a new Handler object, which will handle the received HTTP
        /// requests.
        /// </summary>
        /// <param name="ctx">Reference to the HttpListenerContext to handle.</param>
        public RequestHandler(HttpListenerContext ctx)
        {
            context = ctx;
        }

        /// <summary>
        /// Will parse and process the request, taking the actions necessary.
        /// </summary>
        public void ProcessRequest()
        {
            // Write the request we received to console for debugging purposeses.
            string info = "Request: " + context.Request.HttpMethod + " " + context.Request.Url;
            Trace.WriteLine(info);

            // Retrieve the session id from the request, which will be used as password.
            string sessionid = context.Request.QueryString["sessionid"];

            // Change the password of the weblab user
            AccountsManager accManager = new AccountsManager("", "");
            accManager.SetPassword("weblab", sessionid);
        }
    }


}
