
using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;


namespace WebLab.VM.WindowsRDP
{

    class AccountsManager : IDisposable
    {
        private PrincipalContext mPrincipalContext;

        public bool Validated { get; private set; }

        /// <summary>
        /// Retrieves the User with the specified account name. May return null.
        /// </summary>
        /// <param name="accName">Account name whose UserPrincipal to retrieve</param>
        /// <returns>The UserPrincipal object, or null if not found.</returns>
        private UserPrincipal GetUserPrincipal(string accName)
        {
            UserPrincipal principal = UserPrincipal.FindByIdentity(mPrincipalContext, accName);
            return principal;
        }

        public AccountsManager(string admin_acc, string admin_pwd)
        {
            mPrincipalContext = new PrincipalContext(ContextType.Machine, null, admin_acc, admin_pwd);

            // We need to separatedly validate the credentials
            bool success = mPrincipalContext.ValidateCredentials(admin_acc, admin_pwd);

            if (!success)
                throw new Exception("Could not validate credentials");

            Validated = true;
        }

        public void SetPassword(string acc, string pwd)
        {
            var user = GetUserPrincipal(acc);
            if (user == null)
                throw new Exception("Could not find such user");

            user.SetPassword(pwd);
        }

        //public void CreateAccount(string acc, string pwd)
        //{
        //    var user = new UserPrincipal(mPrincipalContext, acc, pwd, true);
        //    user.Save();
        //    user.Dispose();
        //}

        public void Dispose()
        {
            mPrincipalContext.Dispose();
        }
    }

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
            string info = "Request: " + context.Request.HttpMethod + " " + context.Request.Url;
            Trace.WriteLine(info);

            // Retrieve the session id from the request, which will be used as password.
            string sessionid = context.Request.QueryString["sessionid"];

            // Change the password of the weblab user
            AccountsManager accManager = new AccountsManager("", "");
            accManager.SetPassword("weblab", sessionid);
        }
    }


	class Program
	{
		public static void Main(string[] args)
		{
            InitializeLogSystem();
            Program program = new Program();
            program.Run();
		}


        private static void InitializeLogSystem()
        {
            TextWriterTraceListener traceListener = new TextWriterTraceListener(System.Console.Out);
            System.Diagnostics.Trace.Listeners.Add(traceListener);
        }

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
                	Handler handler = new Handler(ctx);
                	handler.ProcessRequest();
				}
				catch(Exception ex)
				{
					Trace.WriteLine("Exception caught: ");
					Trace.WriteLine(ex.Message);
				}
			}
        }
	}
}