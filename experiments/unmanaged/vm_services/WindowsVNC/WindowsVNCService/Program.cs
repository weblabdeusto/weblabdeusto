using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Diagnostics;

namespace WebLab.VM.WindowsVNC
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main()
        {
            InitializeLogSystem();
            Trace.WriteLine("Registering WindowsVNC Service");

            ServiceBase[] ServicesToRun;
            ServicesToRun = new ServiceBase[] 
			{ 
				new WindowsVNCService() 
			};
            ServiceBase.Run(ServicesToRun);
        }


        private static void InitializeLogSystem()
        {
            TextWriterTraceListener textWriter = new TextWriterTraceListener("WeblabWinRDP.log");
            System.Diagnostics.Trace.Listeners.Add(textWriter);

            if (!EventLog.SourceExists("Weblab WinVNC"))
                EventLog.CreateEventSource("Weblab WinVNC", "Weblab Log");
            EventLog evLog = new EventLog("Weblab Log");
            evLog.Source = "Weblab WinVNC";
            EventLogTraceListener evTraceListener = new EventLogTraceListener(evLog);
            System.Diagnostics.Trace.Listeners.Add(evTraceListener);
        }
    }
}
