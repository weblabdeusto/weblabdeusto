using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections.Specialized;
using System.Diagnostics;

namespace WebLab.VM.WindowsRDPVNC
{

    public class ConfigException : Exception
    {
        public ConfigException(string msg) : base(msg)
        {
        }   
    }

    /// <summary>
    /// Aids with password changing and changers management. 
    /// </summary>
    public class PasswordChangerManager
    {
        private static PasswordChangerManager mInstance = new PasswordChangerManager();
        public static PasswordChangerManager Instance { get { return mInstance; } }

        private Dictionary<string, IPasswordChanger> mPasswordChangers = new Dictionary<string, IPasswordChanger>();

        /// <summary>
        /// Registers a type of password changer.
        /// </summary>
        /// <param name="name">Name of the changer. Mostly for tracking/debugging purposes.</param>
        /// <param name="changer">The changer.</param>
        public void registerPasswordChanger(string name, IPasswordChanger changer)
        {
            mPasswordChangers.Add(name, changer);
        }

        /// <summary>
        /// Changes the password of every single registered method/type.
        /// </summary>
        /// <param name="newPassword">Password to change everything to.</param>
        public void changePassword(string newPassword)
        {
            foreach (var changer in mPasswordChangers.Values)
                changer.ChangePassword(newPassword);
        }

        /// <summary>
        /// Retrieves the specified value from the NameValueCollection.
        /// Throws a ConfigException custom exception if the value is null or not
        /// found.
        /// </summary>
        /// <param name="config">NameValueCollection in which to search for the value.</param>
        /// <param name="key">Key which specifies the value to retrieve.</param>
        /// <returns></returns>
        private string RetrieveValue(NameValueCollection config, string key)
        {
            var ret = config[key];
            if (ret == null)
                throw new ConfigException(String.Format("Could not find the {0} variable", key));
            return ret;
        }

        /// <summary>
        /// Registers the appropiate changers by itself according to the specified
        /// configuration.
        /// </summary>
        /// <param name="config">Configuration which will be used to choose the appropiate changers 
        /// and to retrieve the specific information that each of them may require. Note that the presence
        /// of every "enable" is required, though they may be set to false. Generally the collection will
        /// simply be the app.config collection. Note also that the presence of additional unrelated 
        /// NameValues is allowed. </param>
        public void registerPasswordChangers(NameValueCollection config)
        {
            bool en_rdp = Convert.ToBoolean(RetrieveValue(config, "enable_rdp"));
            bool en_vnc = Convert.ToBoolean(RetrieveValue(config, "enable_ultravnc"));

            if (en_rdp)
            {
                Trace.WriteLine("Building RDP password changer");
                string acc_name = RetrieveValue(config, "rdp_acc_name");
                var rdp_changer = new WindowsPasswordChanger(acc_name);
                PasswordChangerManager.Instance.registerPasswordChanger("rdp", rdp_changer);
            }

            if (en_vnc)
            {
                Trace.WriteLine("Building VNC password changer");
                string vnc_path = RetrieveValue(config, "ultravnc_path");
                var vnc_changer = new UltraVNCPasswordChanger(vnc_path);
                PasswordChangerManager.Instance.registerPasswordChanger("ultravnc", vnc_changer);
            }
        }
    }
}
