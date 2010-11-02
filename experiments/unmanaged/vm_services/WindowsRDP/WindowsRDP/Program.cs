
using System;
using System.Net;

namespace WindowsRDP
{

    class Handler
    {
        private HttpListenerContext context;


        /// <summary>
        /// Create a new Handler object, which will handle the received HTTP
        /// requests.
        /// </summary>
        /// <param name="ctx">Reference to the HttpListenerContext to handle.</param>
        public Handler(HttpListenerContext ctx)
        {
            context = ctx;
        }

        /// <summary>
        /// Will parse and process the request, taking the actions necessary.
        /// </summary>
        public void ProcessRequest()
        {
            // Write the request we received to console for debugging purposeses.
            string info = context.Request.HttpMethod + " " + context.Request.Url;
            Console.WriteLine(info);

            // Retrieve the session id from the request, which will be used as password.
            long sessionid = Int64.Parse(context.Request.QueryString["sessionid"]);
        }
    }


	class Program
	{
		public static void Main(string[] args)
		{
            Program program = new Program();
            program.Run();
		}


        public void Run()
        {
            Console.WriteLine("Starting Windows RDP VM Service");

            HttpListener listener = new HttpListener();
            listener.Prefixes.Add("http://*:6789/");
            listener.Start();

            while (true)
            {
                HttpListenerContext ctx = listener.GetContext();
                Handler handler = new Handler(ctx);
                handler.ProcessRequest();
            }
        }
	}
}