using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections.Specialized;

namespace WebLab.VM.WindowsRDPVNC
{

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
        /// Registers the appropiate changers by itself according to the specified
        /// configuration.
        /// </summary>
        /// <param name="config">Configuration which will be used to choose the appropiate changers 
        /// and to retrieve the specific information that each of they may require. Generally it will
        /// simply be the app.config collection. Note that the presence of additional unrelated 
        /// NameValues is allowed. </param>
        public void registerPasswordChangers(NameValueCollection config)
        {

        }
    }
}
