
using System;
using System.Net;
using System.Diagnostics;
using System.Configuration;


namespace WebLab.VM.WindowsRDP
{
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

            if(!EventLog.SourceExists("Weblab WinRDP"))
                EventLog.CreateEventSource("Weblab WinRDP", "Weblab Log");
            EventLog evLog = new EventLog("Weblab Log");
            evLog.Source = "Weblab WinRDP";
            EventLogTraceListener evTraceListener = new EventLogTraceListener(evLog);
            System.Diagnostics.Trace.Listeners.Add(evTraceListener);
        }

        public void Run()
        {
            var prefix = "";
            var acc = "";
            var pwd = "";

            try
            {
                prefix = ConfigurationManager.AppSettings["request_prefix"];
                acc = ConfigurationManager.AppSettings["admin_account"];
                pwd = ConfigurationManager.AppSettings["admin_password"];
            }
            catch (Exception e)
            {
                Trace.WriteLine("Could not read the required configuration variables");
                return;
            }

            if (prefix == "" || acc == "" || pwd == "")
            {
                Trace.WriteLine("request_prefix, admin_account and admin_password configuration variables must all be specified");
                return;
            }

            using (AccountsManager accountsManager = new AccountsManager(acc, pwd))
            {
                RequestsListener listener = new RequestsListener(prefix, accountsManager);
                listener.Run();
            }
        }
	}
}