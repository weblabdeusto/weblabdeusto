using System;
using System.Data;
using System.Configuration;
using System.Collections;
using System.Collections.Generic;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.UI.WebControls.WebParts;
using System.Web.UI.HtmlControls;
using System.Xml;

using iLabs.Core;
using iLabs.DataTypes;
using iLabs.DataTypes.ProcessAgentTypes;
using iLabs.DataTypes.TicketingTypes;
using iLabs.Ticketing;
using iLabs.DataTypes.SoapHeaderTypes;
using iLabs.Proxies.ESS;

namespace iLabs.LabServer.WebLabDeustoServer
{

    public partial class Redirect : System.Web.UI.Page
    {
        ProcessAgentDB dbTicketing = new ProcessAgentDB();

        private static Dictionary<long, WebLabDeusto.Reservation> RESERVATION_IDS = new Dictionary<long, WebLabDeusto.Reservation>();

        protected void Page_Load(object sender, EventArgs e)
        {
            // retrieve parameters from URL
            string couponId = Request.QueryString["coupon_id"];
            string passkey = Request.QueryString["passkey"];
            string issuerGuid = Request.QueryString["issuer_guid"];
            string sbUrl = Request.QueryString["sb_url"];

            if (passkey != null && couponId != null && issuerGuid != null)
            {
                //set execution coupon and ticket type
                Coupon executionCoupon = new Coupon(issuerGuid, Int64.Parse(couponId), passkey);
                string type = TicketTypes.EXECUTE_EXPERIMENT;

                // retrieve the ticket and verify it
                Ticket retrievedTicket = dbTicketing.RetrieveAndVerify(executionCoupon, type);

                XmlDocument payload = new XmlDocument();
                payload.LoadXml(retrievedTicket.payload);

                long experimentId = Int64.Parse(payload.GetElementsByTagName("experimentID")[0].InnerText);

                string weblabDeustoUrl = ConfigurationManager.AppSettings["weblabdeusto_url"];
                WebLabDeusto.WebLabDeustoClient client = new WebLabDeusto.WebLabDeustoClient(weblabDeustoUrl);

                if (RESERVATION_IDS.ContainsKey(experimentId))
                {
                    string newUrl = client.CreateClient(RESERVATION_IDS[experimentId]);
                    LoadWebLab(newUrl);
                }
                else
                {
                    string username       = ConfigurationManager.AppSettings["weblabdeusto_username"];
                    string password       = ConfigurationManager.AppSettings["weblabdeusto_password"];
                    string experimentName = ConfigurationManager.AppSettings["weblabdeusto_exp_name"];
                    string categoryName   = ConfigurationManager.AppSettings["weblabdeusto_exp_category"];

                    Dictionary<string, object> consumerData = new Dictionary<string, object>();

                    consumerData["external_user"] = Convert.ToString(experimentId); // Could be group ID
                    consumerData["user_agent"]    = Request.UserAgent;
                    consumerData["referer"]       = Request.UrlReferrer.ToString();
                    consumerData["from_ip"]       = Request.UserHostAddress;

                    if (ConfigurationManager.AppSettings["weblabdeusto_priority"] != null)
                        consumerData["priority"] = Convert.ToInt32(ConfigurationManager.AppSettings["weblabdeusto_priority"]);

                    if (ConfigurationManager.AppSettings["weblabdeusto_time_allowed"] != null)
                        consumerData["time_allowed"] = Convert.ToInt32(ConfigurationManager.AppSettings["weblabdeusto_time_allowed"]);

                    if (ConfigurationManager.AppSettings["weblabdeusto_initialization_in_accounting"] != null)
                        consumerData["initialization_in_accounting"] = Convert.ToBoolean(ConfigurationManager.AppSettings["weblabdeusto_initialization_in_accounting"]);

                    WebLabDeusto.SessionId sessid = client.Login(username, password);
                    WebLabDeusto.Reservation reservation = client.ReserveExperiment(sessid, experimentName, categoryName, consumerData);

                    RESERVATION_IDS.Add(experimentId, reservation);

                    string newUrl = client.CreateClient(reservation);

                    LoadWebLab(newUrl);
                }
            }
            else
            {
                Response.Redirect("Default.aspx" + "?sb_url=" + sbUrl);
            }
        }

        private void LoadWebLab(string url)
        {
            bool weblabDebugging = ConfigurationManager.AppSettings["weblabdeusto_debug"] == "true";
            if (weblabDebugging)
                HyperLinkReservation.NavigateUrl = url;
            else
                Response.Redirect(url);
        }
    }
}
