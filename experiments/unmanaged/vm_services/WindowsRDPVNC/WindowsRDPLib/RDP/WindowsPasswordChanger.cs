using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WebLab.VM.WindowsRDPVNC
{
    public class WindowsPasswordChanger : IPasswordChanger
    {
        private AccountsManager mAccsManager = new AccountsManager();
        private string mAccName;

        public WindowsPasswordChanger(string accName)
        {
            mAccName = accName;
        }

        public void ChangePassword(string newPassword)
        {
            mAccsManager.SetPassword(mAccName, newPassword);
        }
    }
}
