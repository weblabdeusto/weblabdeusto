using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WindowsRDPLib
{

    /// <summary>
    /// Aids with password changing and changers management. 
    /// </summary>
    class PasswordChangerManager
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
    }
}
