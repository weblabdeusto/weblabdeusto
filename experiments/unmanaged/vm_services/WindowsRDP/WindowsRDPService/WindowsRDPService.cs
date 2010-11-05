using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading;

namespace WebLab.VM.WindowsRDP
{
    public partial class WindowsRDPService : ServiceBase
    {
        private RequestsListener mListener;
        private Thread mListenerThread;

        public WindowsRDPService()
        {
            InitializeComponent();
        }

        protected override void OnStart(string[] args)
        {
            Trace.WriteLine("WindowsRDPService starting.");

            mListener = new RequestsListener();
            mListenerThread = new Thread(new ThreadStart(mListener.Run));
            mListenerThread.Start();
        }

        protected override void OnStop()
        {
            Trace.WriteLine("WindowsRDPService stopping.");

            // This is not particularly advisable, but shouldn't be too bad here.
            mListenerThread.Abort();
        }
    }
}
