using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WebLab.VM.WindowsRDPVNC
{

    /// <summary>
    /// Exception which will be thrown whenever an error occurs
    /// while trying to change a password.
    /// </summary>
    public class PasswordChangingException : Exception
    {
        public PasswordChangingException(string msg)
            : base(msg)
        {
        }
    }


    /// <summary>
    /// Generic interface which should be implemented by
    /// every class capable of changing the password of some
    /// system or method. 
    /// </summary>
    public interface IPasswordChanger
    {

        /// <summary>
        /// Changes the system's or method's password.
        /// Throws a PasswordChangingException on error.
        /// </summary>
        /// <param name="newPassword">New password. May need to meet some criteria.
        /// Dependent on the implementation.</param>
        void ChangePassword(string newPassword);
    }
}
