using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;
using System.Text;
using System.ServiceProcess;


namespace WebLab.VM.WindowsVM
{

    /// <summary>
    /// Provides straightforward facilities for the account management
    /// that we require.
    /// </summary>
    public class UltraVNCManager : IDisposable
    {
        private const string UVNCServiceName = "uvnc_service";
        private const int ServiceOpTimeout = 20000;

        /// <summary>
        /// Standard DES key
        /// </summary>
        private static byte[] key = { 0x17, 0x52, 0x6b, 0x6, 0x23, 0x4e, 0x58, 0x7 };

        /// <summary>
        /// Path to the UltraVNC installation root folder.
        /// </summary>
        public string UltraVNCPath { get; set; }

        /// <summary>
        /// Constructs an UltraVNCManager object.
        /// </summary>
        /// <param name="ultra_vnc_path">Path to the UltraVNC installation. This path is used to locate 
        /// the ultravnc.ini config file.</param>
        public UltraVNCManager(string ultra_vnc_path)
        {
            UltraVNCPath = ultra_vnc_path;
        }

        /// <summary>
        /// Encrypts the given password using the VNC encryption that UltraVNC uses
        /// to store its passwords. Which is, standard VNC DES encryption plus two
        /// bytes, which are supposed to be a checksum but which are currently not checked
        /// by UltraVNC.
        /// </summary>
        /// <param name="pwd">Password to encrypt. Only the first 8 characters are actually used. (As is standard in VNC).</param>
        /// <returns>A string with the cyphertext in hex, with no spaces or prefixes</returns>
        private static string EncryptPassword(string pwd)
        {
            VNCEncrypt.load();
            VNCEncrypt enc = new VNCEncrypt(key);
            var pwd_bytes = StringToBytes(pwd);
            Array.Resize(ref pwd_bytes, 8);
            var enc_bytes = enc.encrypt(pwd_bytes);
            var sb = new StringBuilder();

            string enc_str = BitConverter.ToString(enc_bytes).Replace("-", "");
            enc_str += "00";

            return enc_str;
        }


        /// <summary>
        /// Restarts the specified service, using ServiceOpTimeout as timeout for 
        /// individual service operations. Throws an Exception if not succesful.
        /// Starts it if it isn't already running.
        /// </summary>
        /// <param name="serviceName"></param>
        private static void RestartService(string serviceName)
        {
            ServiceController service = new ServiceController(serviceName);

            try
            {
                TimeSpan timeout = TimeSpan.FromMilliseconds(ServiceOpTimeout);

                if (service.Status == ServiceControllerStatus.Running)
                {
                    service.Stop();
                    service.WaitForStatus(ServiceControllerStatus.Stopped, timeout);
                }

                service.Start();
                service.WaitForStatus(ServiceControllerStatus.Running, timeout);
            }
            catch
            {
                Trace.WriteLine("Service operation was not successful");
                throw new Exception("Service operation failed");
            }
        }

        /// <summary>
        /// Helper method which converts an ASCII string to bytes.
        /// </summary>
        /// <param name="cadena"></param>
        /// <returns></returns>
        public static byte[] StringToBytes(String cadena)
        {
            System.Text.ASCIIEncoding cod = new System.Text.ASCIIEncoding();
            return cod.GetBytes(cadena);
        }

        /// <summary>
        /// Sets the standard password.
        /// <remarks>
        /// Modifies the config .ini file of UltraVNC to set the new password. In order for the change
        /// to take effect, a restart is required. This restart might be initiated through the
        /// Restart method.
        /// </remarks>
        /// </summary>
        /// <param name="pwd">New password. Only the first 8 characters are actually used.</param>
        public void SetPassword(string pwd)
        {
            Trace.WriteLine("Trying to set password... ");

            string enc_pwd = EncryptPassword(pwd);
            IniRW rw = new IniRW(UltraVNCPath + "\\ultravnc.ini");
            rw.WriteValue("ultravnc", "passwd", enc_pwd);

            Trace.WriteLine("done.");
        }

        /// <summary>
        /// Restarts the UltraVNC service. Configuration changes, including password changes, will
        /// only take effect after such a restart.
        /// <remarks>
        /// Will not return until the service has been restarted. If the restart times out (it uses
        /// ServiceOpTimeout for every operation) or if the restart just fails, an Exception is thrown.
        /// To restart, a stop and a start operations are required, hence, the maximum blocking time will
        /// be two times the ServiceOpTimeout.
        /// </remarks>
        /// </summary>
        public void Restart()
        {
            RestartService(UVNCServiceName);
        }


        /// <summary>
        /// Sets the view password.
        /// <remarks>
        /// Modifies the config .ini file of UltraVNC to set the new password. In order for the change
        /// to take effect, a restart is required. This restart might be initiated through the
        /// Restart method.
        /// </remarks>
        /// </summary>
        /// <param name="pwd">New password. Only the first 8 characters are actually used.</param>
        public void SetViewPassword(string pwd)
        {
            Trace.WriteLine("Trying to set view password...");

            string enc_pwd = EncryptPassword(pwd);
            IniRW rw = new IniRW(UltraVNCPath + "\\ultravnc.ini");
            rw.WriteValue("ultravnc", "passwd2", enc_pwd);

            Trace.WriteLine("done.");
        }

        void IDisposable.Dispose()
        {
        }
    }

}