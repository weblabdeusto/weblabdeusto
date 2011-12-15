/*
 * Copyright (c) 2004 The Massachusetts Institute of Technology. All rights reserved.
 * Please see license.txt in top level directory for full license.
 * 
 * $Id: SelfRegistration.aspx.cs,v 1.10 2007/12/26 05:27:26 pbailey Exp $
 */

using System;
using System.Collections;
using System.ComponentModel;
using System.Configuration;
using System.Data;
using System.Drawing;
using System.Text;
using System.Web;
using System.Web.SessionState;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.HtmlControls;

using iLabs.Core;
using iLabs.DataTypes;
using iLabs.DataTypes.ProcessAgentTypes;
using iLabs.DataTypes.TicketingTypes;
using iLabs.Ticketing;
using iLabs.UtilLib;

namespace iLabs.Services
{
	/// <summary>
	/// Summary description for administration.
	/// </summary>
	public partial class SelfRegistration : System.Web.UI.Page
	{
        private Color disabled = Color.FromArgb(243, 239, 229);
        private Color enabled = Color.White;
  
	    protected bool secure = false; // Backdoor
        ProcessAgentDB dbTicketing = null;


        protected void Page_Load(object sender, System.EventArgs e)
        {
            string couponId;
            string passkey;
            string issuerGuid;
            dbTicketing = new ProcessAgentDB();
           
            if (!IsPostBack)
            {
                // try & test for local access or not configured
                if (secure)
                {
                    // retrieve parameters from URL
                    couponId = Request.QueryString["coupon_id"];
                    passkey = Request.QueryString["passkey"];
                    issuerGuid = Request.QueryString["issuer_guid"];
                    Ticket allowAdminTicket = null;
                    if (couponId != null && passkey != null && issuerGuid != null)
                    {
                        allowAdminTicket = dbTicketing.RetrieveAndVerify(
                            new Coupon(issuerGuid, Int64.Parse(couponId), passkey),
                            TicketTypes.ADMINISTER_LS);
                    }
                    else
                    {
                        Response.Redirect("AccessDenied.aspx", true);
                    }
                }
            }
        }


		#region Web Form Designer generated code
		override protected void OnInit(EventArgs e)
		{
			//
			// CODEGEN: This call is required by the ASP.NET Web Form Designer.
			//
			InitializeComponent();
			base.OnInit(e);
		}
		
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{    

		}
		#endregion
	}
}
