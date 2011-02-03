using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Diagnostics;

namespace WebLab.VM.WindowsVM
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        static void Main()
        {
            InitializeLogSystem();
            Trace.WriteLine("Registering Weblab WindowsVM Service");

            ServiceBase[] ServicesToRun;
            ServicesToRun = new ServiceBase[] 
			{ 
				new WindowsVMService() 
			};
            ServiceBase.Run(ServicesToRun);
        }


        private static void InitializeLogSystem()
        {
            TextWriterTraceListener textWriter = new TextWriterTraceListener("WeblabWinVM.log");
            System.Diagnostics.Trace.Listeners.Add(textWriter);

            if (!EventLog.SourceExists("Weblab WinVM"))
                EventLog.CreateEventSource("Weblab WinVM", "Weblab Log");
            EventLog evLog = new EventLog("Weblab Log");
            evLog.Source = "Weblab WinVM";
            EventLogTraceListener evTraceListener = new EventLogTraceListener(evLog);
            System.Diagnostics.Trace.Listeners.Add(evTraceListener);
        }
    }
}
