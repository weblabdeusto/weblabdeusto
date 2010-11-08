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

namespace WebLab.VM.WindowsRDP
{
    public partial class WindowsRDPService : ServiceBase
    {
        private RequestsListener mListener;
        private Thread mListenerThread;

        private string mAdminAccount = "";
        private string mAdminPassword = "";
        private string mPrefix = "";

        public WindowsRDPService()
        {
            InitializeComponent();
        }

        private void ReadConfigVars()
        {
            try
            {
                mPrefix = ConfigurationManager.AppSettings["request_prefix"];
                mAdminAccount = ConfigurationManager.AppSettings["admin_account"];
                mAdminPassword = ConfigurationManager.AppSettings["admin_password"];
            }
            catch (Exception e)
            {
                Trace.WriteLine("Could not read the required configuration variables");
                return;
            }

            if (mPrefix == "" || mAdminAccount == "" || mAdminPassword == "")
            {
                Trace.WriteLine("request_prefix, admin_account and admin_password configuration variables must all be specified");
                return;
            }

            Trace.WriteLine(String.Format("Admin Acc: {0}\nAdmin Pass: {1}\nPrefix: {2}", mAdminAccount, mAdminPassword, mPrefix));
        }


        private void Run()
        {
            try
            {
                using (AccountsManager accsManager = new AccountsManager(mAdminAccount, mAdminPassword))
                {
                    mListener = new RequestsListener(mPrefix, accsManager);
                    mListener.Run();
                }
            }
            catch (Exception e)
            {
                Trace.WriteLine("Exception caught at main thread. Aborting. " + e.Message);
            }
        }

        protected override void OnStart(string[] args)
        {
            Trace.WriteLine("WindowsRDPService starting.");

            ReadConfigVars();

            try
            {
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
