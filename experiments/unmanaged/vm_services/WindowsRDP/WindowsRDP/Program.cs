﻿
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
        }

        public void Run()
        {
            var prefix = ConfigurationManager.AppSettings["request_prefix"];
            RequestsListener listener = new RequestsListener(prefix);
            listener.Run();
        }
	}
}