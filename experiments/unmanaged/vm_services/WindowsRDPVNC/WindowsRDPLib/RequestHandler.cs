using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;
using System.IO;


namespace WebLab.VM.WindowsRDP
{

    /// <summary>
    /// Handles specific HTTP requests
    /// </summary>
    public class RequestHandler
    {
        private HttpListenerContext mContext;
        private AccountsManager mAccountsManager;

        /// <summary>
        /// Create a new Handler object, which will handle the received HTTP
        /// requests.
        /// </summary>
        /// <param name="ctx">Reference to the HttpListenerContext to handle.</param>
        public RequestHandler(HttpListenerContext ctx, AccountsManager accountsManager)
        {
            mContext = ctx;
            mAccountsManager = accountsManager;
        }

        /// <summary>
        /// Will parse and process the request, taking the actions necessary.
        /// </summary>
        public void ProcessRequest()
        {
            var respWriter = new StreamWriter(mContext.Response.OutputStream);

            try
            {
                // Write the request we received to console for debugging purposeses.
                string info = "Request: " + mContext.Request.HttpMethod + " " + mContext.Request.Url;
                Trace.WriteLine(info);

                // Retrieve the session id from the request, which will be used as password.
                string sessionid = mContext.Request.QueryString["sessionid"];
                if (sessionid == null || sessionid == "")
                {
                    Trace.WriteLine("Received session id is not valid");
                    return;
                }

                // Change the password of the weblab user
                mAccountsManager.SetPassword("weblab", sessionid);

                respWriter.WriteLine("Done");
            }
            catch (Exception ex)
            {
                var msg = "Exception caught: " + ex.Message;
                Trace.WriteLine(msg);

                respWriter.WriteLine("Failed");
            }
            finally
            {
                respWriter.Close();
            }
        }
    }


}
