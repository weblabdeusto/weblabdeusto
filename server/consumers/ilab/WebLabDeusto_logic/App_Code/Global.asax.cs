using System;
using System.Collections;
using System.ComponentModel;
using System.Configuration;
using System.Web;
using System.Web.SessionState;

using iLabs.Core;
using iLabs.Ticketing;
using iLabs.UtilLib;

namespace iLabs.LabServer.TimeOfDay 
{
	/// <summary>
	/// Summary description for Global.
	/// </summary>
	public class Global : System.Web.HttpApplication
	{
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;
        private TicketRemover ticketRemover;

        static Global()
        {
            if (ConfigurationManager.AppSettings["logPath"] != null
               && ConfigurationManager.AppSettings["logPath"].Length > 0)
            {
                Logger.LogPath = ConfigurationManager.AppSettings["logPath"];
               Logger.WriteLine("");
               Logger.WriteLine("#############################################################################");
               Logger.WriteLine(iLabGlobal.Release);
               Logger.WriteLine("Global Static started: " + iLabGlobal.Release + " -- " + iLabGlobal.BuildDate);
            }
        }

		public Global()
		{
			InitializeComponent();
		}	
		
		protected void Application_Start(Object sender, EventArgs e)
		{
            if (ConfigurationManager.AppSettings["logPath"] != null
              && ConfigurationManager.AppSettings["logPath"].Length > 0)
            {
                Logger.LogPath = ConfigurationManager.AppSettings["logPath"];
                Logger.WriteLine("");
                Logger.WriteLine("#############################################################################");
                Logger.WriteLine(iLabGlobal.Release);
                Logger.WriteLine("TOD Application_Start: starting");
            }
            ProcessAgentDB.RefreshServiceAgent();
            ticketRemover = new TicketRemover();
		}
 
		protected void Session_Start(Object sender, EventArgs e)
		{

		}

		protected void Application_BeginRequest(Object sender, EventArgs e)
		{

		}

		protected void Application_EndRequest(Object sender, EventArgs e)
		{

		}

		protected void Application_AuthenticateRequest(Object sender, EventArgs e)
		{

		}

		protected void Application_Error(Object sender, EventArgs e)
		{

		}

		protected void Session_End(Object sender, EventArgs e)
		{

		}

		protected void Application_End(Object sender, EventArgs e)
		{
            if (ticketRemover != null)
                ticketRemover.Stop();

		}
			
		#region Web Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{    
			this.components = new System.ComponentModel.Container();
		}
		#endregion
	}
}

