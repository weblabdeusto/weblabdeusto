
using System;
using System.Net;
using System.Diagnostics;
using System.DirectoryServices.AccountManagement;


namespace WebLab.VM.WindowsRDP
{

    /// <summary>
    /// Provides straightforward facilities for the account management
    /// that we require.
    /// </summary>
    public class AccountsManager : IDisposable
    {
        private PrincipalContext mPrincipalContext;

        public bool Validated { get; private set; }

        /// <summary>
        /// Retrieves the User with the specified account name. May return null.
        /// </summary>
        /// <param name="accName">Account name whose UserPrincipal to retrieve</param>
        /// <returns>The UserPrincipal object, or null if not found.</returns>
        private UserPrincipal GetUserPrincipal(string accName)
        {
            UserPrincipal principal = UserPrincipal.FindByIdentity(mPrincipalContext, accName);
            return principal;
        }

        public AccountsManager(string admin_acc, string admin_pwd)
        {
            mPrincipalContext = new PrincipalContext(ContextType.Machine, null, admin_acc, admin_pwd);

            // We need to separatedly validate the credentials
            bool success = mPrincipalContext.ValidateCredentials(admin_acc, admin_pwd);

            if (!success)
                throw new Exception("Could not validate credentials");

            Validated = true;
        }

        public void SetPassword(string acc, string pwd)
        {
            var user = GetUserPrincipal(acc);
            if (user == null)
                throw new Exception("Could not find such user");

            user.SetPassword(pwd);
        }

        //public void CreateAccount(string acc, string pwd)
        //{
        //    var user = new UserPrincipal(mPrincipalContext, acc, pwd, true);
        //    user.Save();
        //    user.Dispose();
        //}

        public void Dispose()
        {
            mPrincipalContext.Dispose();
        }
    }

}