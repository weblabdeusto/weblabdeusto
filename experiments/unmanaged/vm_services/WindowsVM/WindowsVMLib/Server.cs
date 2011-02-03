using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Configuration;
using WebLab.VM.WindowsVM;
using System.Diagnostics;

namespace WebLab.VM.WindowsVM
{

    /// <summary>
    /// Core class which reads the configuration, starts up a server to 
    /// listen for requests, and executes them.
    /// </summary>
    public class Server
    {

        private static Server mInstance = new Server();
        public static Server Instance { get { return mInstance; } }

        public bool Initialized { get; set; }

        // Prefix which will be used when listening for HTTP queries.
        private string mPrefix;


        private Server()
        {
            Initialized = false; // False by default. For clarity only.
        }

        /// <summary>
        /// Initializes the Server, reading the appropiate configuration variables and
        /// registering the changers specified on it. If an exception occurs, it will 
        /// be traced and rethrown.
        /// </summary>
        public void Initialize()
        {
            try
            {
                mPrefix = ConfigurationManager.AppSettings["request_prefix"];
                if (mPrefix == null)
                    throw new ConfigException("request_prefix variable was not specified in the configuration file");

                PasswordChangerManager.Instance.registerPasswordChangers(ConfigurationManager.AppSettings);
            }
            catch (ConfigException e)
            {
                Trace.WriteLine(e.Message);
                throw;
            }
            catch (Exception e)
            {
                Trace.WriteLine(e.Message);
                Trace.WriteLine(e.StackTrace);
                throw;
            }

            Initialized = true;
        }

        /// <summary>
        /// Starts listening for requests and handling them. Will initialize the server
        /// through the Initialize method if it hasn't been done already.
        /// If an error occurs, the exception will be traced and rethrown.
        /// </summary>
        public void Run()
        {
            if (!Initialized)
                Initialize();

            try
            {
                RequestsListener listener = new RequestsListener(mPrefix);
                listener.Run();
            }
            catch (Exception e)
            {
                Trace.WriteLine(e.Message);
                Trace.WriteLine(e.StackTrace);
                throw;
            }
        }

    } //! class
} //! namespace
