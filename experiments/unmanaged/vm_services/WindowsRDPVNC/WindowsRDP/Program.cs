
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
            try
            {
                string prefix = ConfigurationManager.AppSettings["request_prefix"];
                if (prefix == null)
                    throw new ConfigException("request_prefix variable was not specified in the configuration file");

                PasswordChangerManager.Instance.registerPasswordChangers(ConfigurationManager.AppSettings);

                RequestsListener listener = new RequestsListener(prefix);
                listener.Run();
            }
            catch (ConfigException e)
            {
                Trace.WriteLine(e.Message);
            }
            catch (Exception e)
            {
                Trace.WriteLine(e.Message);
                Trace.WriteLine(e.StackTrace);
            }
        } //! Run()

	} //! Class

} //! Namespace