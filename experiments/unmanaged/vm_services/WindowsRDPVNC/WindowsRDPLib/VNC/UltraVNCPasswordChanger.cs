using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WebLab.VM.WindowsRDPVNC
{
    class UltraVNCPasswordChanger
    {

        private string mUltraVNCPath;
        private UltraVNCManager mUltraVNCMngr;

        public UltraVNCPasswordChanger(string ultraVNCPath)
        {
            mUltraVNCPath = ultraVNCPath;
            mUltraVNCMngr = new UltraVNCManager(ultraVNCPath);
        }

        /// <summary>
        /// Changes the UltraVNC password. 
        /// TODO: Add view-only password changing capabilities.
        /// </summary>
        /// <param name="newPassword">New password</param>
        public void ChangePassword(string newPassword)
        {
            mUltraVNCMngr.SetPassword(newPassword);
        }
    }
}
