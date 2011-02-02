using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Configuration;
using WebLab.VM.WindowsRDPVNC;
using System.Diagnostics;

namespace WebLab.VM.WindowsRDPVNC
{

    /// <summary>
    /// Core class which reads the configuration, starts up a server to 
    /// listen for requests, and executes them.
    /// </summary>
    public class Server
    {

        private static Server mInstance = new Server();
        public static Server Instance { get { return mInstance; } }

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
        }

    } //! class
} //! namespace
