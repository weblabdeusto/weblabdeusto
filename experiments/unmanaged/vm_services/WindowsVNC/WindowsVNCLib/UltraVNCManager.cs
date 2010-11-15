
using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;


namespace WebLab.VM.WindowsVNC
{

    /// <summary>
    /// Provides straightforward facilities for the account management
    /// that we require.
    /// </summary>
    public class UltraVNCManager : IDisposable
    {

        public string UltraVNCPath {get;set;}

        public UltraVNCManager(string ultra_vnc_path)
        {
            UltraVNCPath = ultra_vnc_path;
        }

        public void SetPassword(string pwd)
        {
            Trace.WriteLine("Trying to set password... ");

            IniRW rw = new IniRW(UltraVNCPath + "ultravnc.ini");
            rw.WriteValue("ultravnc", "passwd", pwd);

            Trace.WriteLine("done.");
        }

        public void SetViewPassword(string pwd)
        {
            Trace.WriteLine("Trying to set view password...");

            IniRW rw = new IniRW(UltraVNCPath + "ultravnc.ini");
            rw.WriteValue("ultravnc", "passwd2", pwd);

            Trace.WriteLine("done.");
        }

        void IDisposable.Dispose()
        {
        }
    }

}