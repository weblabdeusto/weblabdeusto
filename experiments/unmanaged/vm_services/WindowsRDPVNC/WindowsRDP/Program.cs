
using System;
using System.Net;
using System.Diagnostics;
using System.Configuration;


namespace WebLab.VM.WindowsRDPVNC
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

            try
            {
                prefix = ConfigurationManager.AppSettings["request_prefix"];
            }
            catch (Exception e)
            {
                Trace.WriteLine("Could not read the required configuration variables");
                return;
            }

            if (prefix == "")
            {
                Trace.WriteLine("request_prefix config variable must be specified");
                return;
            }

            RequestsListener listener = new RequestsListener(prefix);
            listener.Run();
        }
	}
}