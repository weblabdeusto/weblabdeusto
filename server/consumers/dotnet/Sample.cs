using System;
using System.Collections.Generic;
using WebLabDeusto;

namespace Sample
{

    public class WebLabDeustoSample 
    {
        public static void Main(string [] args)
        {
            WebLabDeustoClient weblab = new WebLabDeustoClient("http://localhost/weblab/");

            SessionId sessionId = weblab.Login("any", "password");

//
// Consumer data is an optional argument that can be used to ask the weblab
// server to store different information rather than the one it can try to
// get. For instance, if this .NET software is a not-traditional consumer
// which proxies other users (as running in iLabs), WebLab-Deusto will 
// store the .NET library user-agent rather than the actual final user 
// user-agent. If this component knew what is the actual user agent, it should
// provide it. Same applies to other fields (such as from_ip, etc.)
// 
            Dictionary<string, object> consumerData = new Dictionary<string, object>();

//            consumerData["user_agent"]    = "";
//            consumerData["referer"]       = "";
//            consumerData["mobile"]        = false;
//            consumerData["facebook"]      = false;
//            consumerData["from_ip"]       = "...";

// 
// Additionally, the consumerData may be used to provide scheduling arguments,
// or to provide a user identifier (that could be an anonymized hash).
// 
            consumerData["external_user"]                = "an_external_user_identifier";
//            consumerData["priority"]                     = 3; // the lower, the better
//            consumerData["time_allowed"]                 = 100; // seconds
//            consumerData["initialization_in_accounting"] = false;

            Reservation reservation = weblab.ReserveExperiment(sessionId, "ud-logic", "PIC experiments", consumerData);

            Console.WriteLine(reservation);

            // Optional:
            ReservationId reservationId = reservation.ReservationId;
            reservation = weblab.GetReservationStatus(reservationId);

            Console.WriteLine(reservation);

            Console.WriteLine(weblab.CreateClient(reservation));
        }
    }
}

