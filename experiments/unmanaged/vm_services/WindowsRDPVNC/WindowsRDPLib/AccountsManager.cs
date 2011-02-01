
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

        public AccountsManager()
        {
            mPrincipalContext = new PrincipalContext(ContextType.Machine);

            Validated = true;
        }

        public void SetPassword(string acc, string pwd)
        {
            var user = GetUserPrincipal(acc);
            if (user == null)
                throw new Exception("Could not find such user");

            Trace.WriteLine("Trying to set password... ");
            user.SetPassword(pwd);
            Trace.WriteLine("done.");
        }

        public void Dispose()
        {
            mPrincipalContext.Dispose();
        }
    }

}