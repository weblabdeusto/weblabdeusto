using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading;
using System.Configuration;

namespace WebLab.VM.WindowsRDPVNC
{
    public partial class WindowsRDPService : ServiceBase
    {
        private RequestsListener mListener;
        private Thread mListenerThread;

        private string mPrefix = "";

        public WindowsRDPService()
        {
            InitializeComponent();
        }


        private void Run()
        {
            Server.Instance.Run();
        }

        protected override void OnStart(string[] args)
        {
            Trace.WriteLine("WindowsRDPService starting.");

            try
            {
                Server.Instance.Initialize();

                mListenerThread = new Thread(new ThreadStart(this.Run));
                mListenerThread.Start();
            }
            catch (Exception e)
            {
                Trace.WriteLine("Exception caught at OnStart: " + e.Message);
            }
        }

        protected override void OnStop()
        {
            Trace.WriteLine("WindowsRDPService stopping.");

            // This is not particularly advisable, but shouldn't be too bad here.
            mListenerThread.Abort();
        }
    }
}
